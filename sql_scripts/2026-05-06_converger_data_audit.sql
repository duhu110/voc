-- Read-only audit for converger_agent production results.
-- Run this against the server database and share the output before building
-- the new-ticket agent.

-- 1. Overall coverage.
select
  count(*) as total_tickets,
  count(*) filter (where converger_agent_status = true) as marked_processed,
  count(*) filter (where converger_agent_status = false) as marked_pending,
  round(
    100.0 * count(*) filter (where converger_agent_status = true) / nullif(count(*), 0),
    2
  ) as processed_percent
from raw_complaint_tickets;

select
  (select count(*) from converger_agent_result) as result_rows,
  (select count(distinct ticket_id) from converger_agent_result) as result_distinct_tickets,
  (select count(*) from converger_resolution_summary_atomic) as summary_rows,
  (select count(distinct source_ticket_id) from converger_resolution_summary_atomic) as summary_distinct_tickets,
  (select count(*) from converger_handling_advice where status = 'active') as active_advice_rows;

-- 2. Status/result consistency.
select
  'marked_processed_without_result' as check_name,
  count(*) as row_count
from raw_complaint_tickets t
left join converger_agent_result r on r.ticket_id = t.ticket_id
where t.converger_agent_status = true
  and r.ticket_id is null
union all
select
  'has_result_but_not_marked_processed' as check_name,
  count(*) as row_count
from converger_agent_result r
join raw_complaint_tickets t on t.ticket_id = r.ticket_id
where t.converger_agent_status = false
union all
select
  'result_without_summary' as check_name,
  count(*) as row_count
from converger_agent_result r
left join converger_resolution_summary_atomic s on s.source_ticket_id = r.ticket_id
where s.source_ticket_id is null
union all
select
  'summary_without_result' as check_name,
  count(*) as row_count
from converger_resolution_summary_atomic s
left join converger_agent_result r on r.ticket_id = s.source_ticket_id
where r.ticket_id is null;

-- 3. Agent versions, taxonomy versions, models, and result statuses.
select
  taxonomy_version,
  agent_version,
  model_name,
  status,
  count(*) as row_count,
  min(created_at) as first_created_at,
  max(created_at) as last_created_at
from converger_agent_result
group by taxonomy_version, agent_version, model_name, status
order by row_count desc;

-- 4. Category distribution. Look for extreme concentration or tiny categories.
select
  primary_level1_name,
  primary_level2_name,
  primary_leaf_code,
  primary_leaf_name,
  count(*) as row_count,
  round(100.0 * count(*) / nullif(sum(count(*)) over (), 0), 2) as percent_of_results
from converger_agent_result
group by primary_level1_name, primary_level2_name, primary_leaf_code, primary_leaf_name
order by row_count desc
limit 80;

-- 5. Controlled tag coverage.
select
  count(*) as result_rows,
  count(*) filter (where request_tag_code is not null) as has_request_tag,
  count(*) filter (where emotion_tag_code is not null) as has_emotion_tag,
  count(*) filter (where risk_tag_code is not null) as has_risk_tag,
  count(*) filter (where product_tag_code is not null) as has_product_tag,
  count(*) filter (where line_category is not null and btrim(line_category) <> '') as has_line_category
from converger_agent_result;

select 'request' as tag_group, request_tag_code as tag_code, request_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by request_tag_code, request_tag_name
order by row_count desc
limit 40;

select 'emotion' as tag_group, emotion_tag_code as tag_code, emotion_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by emotion_tag_code, emotion_tag_name
order by row_count desc
limit 40;

select 'risk' as tag_group, risk_tag_code as tag_code, risk_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by risk_tag_code, risk_tag_name
order by row_count desc
limit 40;

select 'product' as tag_group, product_tag_code as tag_code, product_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by product_tag_code, product_tag_name
order by row_count desc
limit 40;

-- 6. Summary quality signals.
select
  count(*) as summary_rows,
  count(*) filter (where resolution_summary is null or btrim(resolution_summary) = '') as empty_summary_rows,
  min(length(resolution_summary)) as min_summary_length,
  percentile_cont(0.25) within group (order by length(resolution_summary)) as p25_summary_length,
  percentile_cont(0.50) within group (order by length(resolution_summary)) as p50_summary_length,
  percentile_cont(0.75) within group (order by length(resolution_summary)) as p75_summary_length,
  max(length(resolution_summary)) as max_summary_length
from converger_resolution_summary_atomic;

select
  source_ticket_id,
  primary_leaf_name,
  product_tag_name,
  request_tag_name,
  risk_tag_name,
  emotion_tag_name,
  length(resolution_summary) as summary_length,
  left(regexp_replace(resolution_summary, '\s+', ' ', 'g'), 240) as summary_preview
from converger_resolution_summary_atomic
where resolution_summary is null
   or length(resolution_summary) < 20
   or length(resolution_summary) > 1200
order by summary_length nulls first
limit 80;

-- 7. Handling advice readiness for a new-ticket agent.
select
  primary_leaf_code,
  primary_leaf_name,
  product_tag_code,
  product_tag_name,
  request_tag_code,
  request_tag_name,
  count(*) as advice_rows,
  sum(source_summary_count) as source_summary_count,
  max(updated_at) as latest_updated_at
from converger_handling_advice
where status = 'active'
group by
  primary_leaf_code,
  primary_leaf_name,
  product_tag_code,
  product_tag_name,
  request_tag_code,
  request_tag_name
order by source_summary_count desc nulls last, advice_rows desc
limit 80;

-- 8. Sparse or missing advice scopes.
with result_scope as (
  select
    primary_leaf_code,
    primary_leaf_name,
    product_tag_code,
    product_tag_name,
    request_tag_code,
    request_tag_name,
    count(*) as result_count
  from converger_agent_result
  group by
    primary_leaf_code,
    primary_leaf_name,
    product_tag_code,
    product_tag_name,
    request_tag_code,
    request_tag_name
),
advice_scope as (
  select
    primary_leaf_code,
    coalesce(product_tag_code, '') as product_tag_code,
    coalesce(request_tag_code, '') as request_tag_code,
    count(*) as advice_count,
    sum(source_summary_count) as source_summary_count
  from converger_handling_advice
  where status = 'active'
  group by primary_leaf_code, coalesce(product_tag_code, ''), coalesce(request_tag_code, '')
)
select
  r.primary_leaf_code,
  r.primary_leaf_name,
  r.product_tag_code,
  r.product_tag_name,
  r.request_tag_code,
  r.request_tag_name,
  r.result_count,
  coalesce(a.advice_count, 0) as advice_count,
  coalesce(a.source_summary_count, 0) as source_summary_count
from result_scope r
left join advice_scope a
  on a.primary_leaf_code = r.primary_leaf_code
 and a.product_tag_code = coalesce(r.product_tag_code, '')
 and a.request_tag_code = coalesce(r.request_tag_code, '')
where coalesce(a.advice_count, 0) = 0
order by r.result_count desc
limit 80;

-- 9. Recent samples for manual review.
select
  r.ticket_id,
  r.primary_level1_name,
  r.primary_level2_name,
  r.primary_leaf_name,
  r.product_tag_name,
  r.request_tag_name,
  r.risk_tag_name,
  r.emotion_tag_name,
  left(regexp_replace(s.resolution_summary, '\s+', ' ', 'g'), 240) as summary_preview,
  r.created_at
from converger_agent_result r
left join converger_resolution_summary_atomic s on s.source_ticket_id = r.ticket_id
order by r.created_at desc
limit 30;
