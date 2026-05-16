from __future__ import annotations


OVERALL_COVERAGE_SQL = """
select
  count(*) as total_tickets,
  count(*) filter (where converger_agent_status = true) as marked_processed,
  count(*) filter (where converger_agent_status = false) as marked_pending,
  round(
    100.0 * count(*) filter (where converger_agent_status = true) / nullif(count(*), 0),
    2
  ) as processed_percent
from raw_complaint_tickets;
"""


RESULT_COVERAGE_SQL = """
select
  (select count(*) from converger_agent_result) as result_rows,
  (select count(distinct ticket_id) from converger_agent_result) as result_distinct_tickets,
  (select count(*) from converger_resolution_summary_atomic) as summary_rows,
  (select count(distinct source_ticket_id) from converger_resolution_summary_atomic) as summary_distinct_tickets,
  (select count(*) from converger_handling_advice where status = 'active') as active_advice_rows;
"""


CONSISTENCY_SQL = """
select
  '已标记处理但无分类结果' as check_name,
  count(*) as row_count
from raw_complaint_tickets t
left join converger_agent_result r on r.ticket_id = t.ticket_id
where t.converger_agent_status = true
  and r.ticket_id is null
union all
select
  '有分类结果但未标记处理' as check_name,
  count(*) as row_count
from converger_agent_result r
join raw_complaint_tickets t on t.ticket_id = r.ticket_id
where t.converger_agent_status = false
union all
select
  '分类结果缺少摘要' as check_name,
  count(*) as row_count
from converger_agent_result r
left join converger_resolution_summary_atomic s on s.source_ticket_id = r.ticket_id
where s.source_ticket_id is null
union all
select
  '摘要缺少分类结果' as check_name,
  count(*) as row_count
from converger_resolution_summary_atomic s
left join converger_agent_result r on r.ticket_id = s.source_ticket_id
where r.ticket_id is null;
"""


VERSION_DISTRIBUTION_SQL = """
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
"""


CATEGORY_DISTRIBUTION_SQL = """
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
"""


TAG_COVERAGE_SQL = """
select
  count(*) as result_rows,
  count(*) filter (where request_tag_code is not null) as has_request_tag,
  count(*) filter (where emotion_tag_code is not null) as has_emotion_tag,
  count(*) filter (where risk_tag_code is not null) as has_risk_tag,
  count(*) filter (where product_tag_code is not null) as has_product_tag,
  count(*) filter (where line_category is not null and btrim(line_category) <> '') as has_line_category
from converger_agent_result;
"""


TAG_DISTRIBUTION_SQL = """
select '诉求标签' as tag_group, request_tag_code as tag_code, request_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by request_tag_code, request_tag_name
union all
select '情绪标签' as tag_group, emotion_tag_code as tag_code, emotion_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by emotion_tag_code, emotion_tag_name
union all
select '风险标签' as tag_group, risk_tag_code as tag_code, risk_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by risk_tag_code, risk_tag_name
union all
select '产品标签' as tag_group, product_tag_code as tag_code, product_tag_name as tag_name, count(*) as row_count
from converger_agent_result
group by product_tag_code, product_tag_name
order by tag_group, row_count desc;
"""


SUMMARY_QUALITY_SQL = """
select
  count(*) as summary_rows,
  count(*) filter (where resolution_summary is null or btrim(resolution_summary) = '') as empty_summary_rows,
  min(length(resolution_summary)) as min_summary_length,
  percentile_cont(0.25) within group (order by length(resolution_summary)) as p25_summary_length,
  percentile_cont(0.50) within group (order by length(resolution_summary)) as p50_summary_length,
  percentile_cont(0.75) within group (order by length(resolution_summary)) as p75_summary_length,
  max(length(resolution_summary)) as max_summary_length
from converger_resolution_summary_atomic;
"""


SUMMARY_OUTLIERS_SQL = """
select
  source_ticket_id,
  primary_leaf_name,
  product_tag_name,
  request_tag_name,
  risk_tag_name,
  emotion_tag_name,
  length(resolution_summary) as summary_length,
  left(regexp_replace(resolution_summary, '\\s+', ' ', 'g'), 240) as summary_preview
from converger_resolution_summary_atomic
where resolution_summary is null
   or length(resolution_summary) < 20
   or length(resolution_summary) > 1200
order by summary_length nulls first
limit 80;
"""


ADVICE_READINESS_SQL = """
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
"""


MISSING_ADVICE_SQL = """
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
"""


RECENT_SAMPLES_SQL = """
select
  r.ticket_id,
  r.primary_level1_name,
  r.primary_level2_name,
  r.primary_leaf_name,
  r.product_tag_name,
  r.request_tag_name,
  r.risk_tag_name,
  r.emotion_tag_name,
  left(regexp_replace(s.resolution_summary, '\\s+', ' ', 'g'), 240) as summary_preview,
  r.created_at
from converger_agent_result r
left join converger_resolution_summary_atomic s on s.source_ticket_id = r.ticket_id
order by r.created_at desc
limit 30;
"""


ADVICE_TOTAL_SQL = """
select
  count(*) as active_advice_rows,
  count(distinct primary_leaf_code) as covered_leaf_count,
  count(distinct primary_leaf_code || '|' || coalesce(product_tag_code,'') || '|' || coalesce(request_tag_code,'')) as covered_scope_count,
  coalesce(sum(source_summary_count), 0) as source_summary_count,
  min(created_at) as first_created_at,
  max(updated_at) as latest_updated_at
from converger_handling_advice
where status = 'active';
"""


ADVICE_SUMMARY_SCOPE_COVERAGE_SQL = """
with summary_scopes as (
  select
    primary_leaf_code,
    product_tag_code,
    request_tag_code,
    count(*) as summary_count
  from converger_resolution_summary_atomic
  where status = 'active'
    and resolution_summary is not null
    and btrim(resolution_summary) <> ''
  group by primary_leaf_code, product_tag_code, request_tag_code
),
advice_scopes as (
  select distinct
    primary_leaf_code,
    product_tag_code,
    request_tag_code
  from converger_handling_advice
  where status = 'active'
)
select
  count(*) as total_summary_scopes,
  count(*) filter (where a.primary_leaf_code is not null) as covered_scopes,
  count(*) filter (where a.primary_leaf_code is null) as uncovered_scopes,
  round(
    100.0 * count(*) filter (where a.primary_leaf_code is not null) / nullif(count(*), 0),
    2
  ) as covered_percent
from summary_scopes s
left join advice_scopes a
  on a.primary_leaf_code = s.primary_leaf_code
 and coalesce(a.product_tag_code, '') = coalesce(s.product_tag_code, '')
 and coalesce(a.request_tag_code, '') = coalesce(s.request_tag_code, '');
"""


ADVICE_BUCKET_COVERAGE_SQL = """
with summary_scopes as (
  select
    primary_leaf_code,
    product_tag_code,
    request_tag_code,
    count(*) as summary_count
  from converger_resolution_summary_atomic
  where status = 'active'
    and resolution_summary is not null
    and btrim(resolution_summary) <> ''
  group by primary_leaf_code, product_tag_code, request_tag_code
),
marked as (
  select
    s.*,
    exists (
      select 1
      from converger_handling_advice a
      where a.status = 'active'
        and a.primary_leaf_code = s.primary_leaf_code
        and coalesce(a.product_tag_code, '') = coalesce(s.product_tag_code, '')
        and coalesce(a.request_tag_code, '') = coalesce(s.request_tag_code, '')
    ) as has_advice
  from summary_scopes s
),
bucketed as (
  select
    case
      when summary_count >= 200 then '>=200'
      when summary_count >= 100 then '100-199'
      when summary_count >= 50 then '50-99'
      when summary_count >= 20 then '20-49'
      else '<20'
    end as bucket,
    summary_count,
    has_advice
  from marked
)
select
  bucket,
  count(*) as scope_count,
  count(*) filter (where has_advice) as covered_count,
  round(100.0 * count(*) filter (where has_advice) / nullif(count(*), 0), 2) as covered_percent,
  case
    when max(summary_count) >= 200 then 100
    when max(summary_count) >= 100 then 95
    when max(summary_count) >= 50 then 80
    when max(summary_count) >= 20 then 60
    else null
  end as target_percent
from bucketed
group by bucket
order by
  case bucket
    when '>=200' then 1
    when '100-199' then 2
    when '50-99' then 3
    when '20-49' then 4
    else 5
  end;
"""


ADVICE_UNCOVERED_HIGH_VALUE_SQL = """
with summary_scopes as (
  select
    primary_leaf_code,
    primary_leaf_name,
    product_tag_code,
    product_tag_name,
    request_tag_code,
    request_tag_name,
    count(*) as summary_count
  from converger_resolution_summary_atomic
  where status = 'active'
    and resolution_summary is not null
    and btrim(resolution_summary) <> ''
  group by
    primary_leaf_code,
    primary_leaf_name,
    product_tag_code,
    product_tag_name,
    request_tag_code,
    request_tag_name
)
select
  s.primary_leaf_code,
  s.primary_leaf_name,
  s.product_tag_code,
  s.product_tag_name,
  s.request_tag_code,
  s.request_tag_name,
  s.summary_count
from summary_scopes s
where not exists (
  select 1
  from converger_handling_advice a
  where a.status = 'active'
    and a.primary_leaf_code = s.primary_leaf_code
    and coalesce(a.product_tag_code, '') = coalesce(s.product_tag_code, '')
    and coalesce(a.request_tag_code, '') = coalesce(s.request_tag_code, '')
)
order by s.summary_count desc
limit 50;
"""


ADVICE_QUALITY_SAMPLE_SQL = """
select
  primary_leaf_name,
  product_tag_name,
  request_tag_name,
  source_summary_count,
  advice_title,
  left(regexp_replace(advice_content, '\\s+', ' ', 'g'), 360) as advice_preview,
  left(regexp_replace(applicability_note, '\\s+', ' ', 'g'), 240) as applicability_preview,
  updated_at
from converger_handling_advice
where status = 'active'
order by source_summary_count desc nulls last, updated_at desc
limit 50;
"""
