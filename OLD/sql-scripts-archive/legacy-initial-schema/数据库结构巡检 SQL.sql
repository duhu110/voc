--0. 先定义本次巡检范围
with target_tables as (
    select unnest(array[
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
    ]) as table_name
)
select * from target_tables;

--1. 巡检：哪些表没有主键
with target_tables as (
    select unnest(array[
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
    ]) as table_name
)
select
    t.table_name as "表名",
    case when exists (
        select 1
        from information_schema.table_constraints tc
        where tc.table_schema = 'public'
          and tc.table_name = t.table_name
          and tc.constraint_type = 'PRIMARY KEY'
    ) then '有主键' else '缺少主键' end as "主键检查结果"
from target_tables t
order by t.table_name;


--2. 巡检：哪些表缺少 created_at / updated_at
with target_tables as (
    select unnest(array[
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
    ]) as table_name
)
select
    t.table_name as "表名",
    case when exists (
        select 1 from information_schema.columns c
        where c.table_schema = 'public'
          and c.table_name = t.table_name
          and c.column_name = 'created_at'
    ) then 'Y' else 'N' end as "有created_at",
    case when exists (
        select 1 from information_schema.columns c
        where c.table_schema = 'public'
          and c.table_name = t.table_name
          and c.column_name = 'updated_at'
    ) then 'Y' else 'N' end as "有updated_at"
from target_tables t
order by t.table_name;

--3. 巡检：结果表是否有 evaluation_status
with target_tables as (
    select unnest(array[
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result'
    ]) as table_name
)
select
    t.table_name as "表名",
    case when exists (
        select 1
        from information_schema.columns c
        where c.table_schema = 'public'
          and c.table_name = t.table_name
          and c.column_name = 'evaluation_status'
    ) then '有' else '缺少' end as "evaluation_status检查"
from target_tables t
order by t.table_name;


---4. 巡检：哪些表没有唯一约束
with target_tables as (
    select unnest(array[
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
    ]) as table_name
)
select
    t.table_name as "表名",
    case when exists (
        select 1
        from information_schema.table_constraints tc
        where tc.table_schema = 'public'
          and tc.table_name = t.table_name
          and tc.constraint_type = 'UNIQUE'
    ) then '有唯一约束' else '无唯一约束' end as "唯一约束检查"
from target_tables t
order by t.table_name;


--5. 巡检：所有外键字段及是否缺少索引
with fk_columns as (
    select
        tc.table_name,
        kcu.column_name,
        ccu.table_name as ref_table_name,
        ccu.column_name as ref_column_name,
        tc.constraint_name
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on tc.constraint_name = kcu.constraint_name
     and tc.table_schema = kcu.table_schema
    join information_schema.constraint_column_usage ccu
      on tc.constraint_name = ccu.constraint_name
     and tc.table_schema = ccu.table_schema
    where tc.table_schema = 'public'
      and tc.constraint_type = 'FOREIGN KEY'
      and tc.table_name in (
        'complaint_category',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
      )
),
indexed_columns as (
    select
        t.relname as table_name,
        a.attname as column_name
    from pg_class t
    join pg_index i on t.oid = i.indrelid
    join pg_attribute a on a.attrelid = t.oid and a.attnum = any(i.indkey)
    join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public'
)
select
    fk.table_name as "表名",
    fk.column_name as "外键字段",
    fk.ref_table_name as "引用表",
    fk.ref_column_name as "引用字段",
    fk.constraint_name as "外键名",
    case
        when exists (
            select 1
            from indexed_columns ic
            where ic.table_name = fk.table_name
              and ic.column_name = fk.column_name
        ) then '已建索引'
        else '缺少索引'
    end as "索引检查"
from fk_columns fk
order by fk.table_name, fk.column_name;
```

--6. 巡检：命名不规范字段
select
    c.table_name as "表名",
    c.column_name as "字段名"
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name in (
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
  )
  and c.column_name !~ '^[a-z][a-z0-9_]*$'
order by c.table_name, c.column_name;


--7. 巡检：可能缺少注释的表
select
    c.relname as "表名",
    case
        when obj_description(c.oid) is null then '缺少表注释'
        else '有表注释'
    end as "表注释检查"
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relkind = 'r'
  and c.relname in (
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
  )
order by c.relname;

--8. 巡检：可能缺少字段注释的列
select
    c.table_name as "表名",
    c.ordinal_position as "顺序",
    c.column_name as "字段名",
    case
        when pgd.description is null then '缺少字段注释'
        else '有字段注释'
    end as "字段注释检查"
from information_schema.columns c
left join pg_class pc
    on pc.relname = c.table_name
left join pg_namespace pn
    on pn.oid = pc.relnamespace
   and pn.nspname = c.table_schema
left join pg_description pgd
    on pgd.objoid = pc.oid
   and pgd.objsubid = c.ordinal_position
where c.table_schema = 'public'
  and c.table_name in (
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
  )
order by c.table_name, c.ordinal_position;


--9. 巡检：哪些表没有任何索引
with target_tables as (
    select unnest(array[
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
    ]) as table_name
)
select
    t.table_name as "表名",
    count(pi.indexname) as "索引数量"
from target_tables t
left join pg_indexes pi
    on pi.schemaname = 'public'
   and pi.tablename = t.table_name
group by t.table_name
order by t.table_name;

--10. 巡检：结果表里的 ticket_id 是否可用于关联原始工单
with target_tables as (
    select unnest(array[
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
    ]) as table_name
)
select
    t.table_name as "表名",
    case when exists (
        select 1
        from information_schema.columns c
        where c.table_schema = 'public'
          and c.table_name = t.table_name
          and c.column_name = 'ticket_id'
    ) then '有ticket_id' else '缺少ticket_id' end as "ticket_id检查"
from target_tables t
order by t.table_name;


--11. 巡检：分类字典表是否具备层级关键字段
select
    'complaint_category' as "表名",
    case when exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'complaint_category' and column_name = 'code'
    ) then 'Y' else 'N' end as "有code",
    case when exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'complaint_category' and column_name = 'name'
    ) then 'Y' else 'N' end as "有name",
    case when exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'complaint_category' and column_name = 'parent_id'
    ) then 'Y' else 'N' end as "有parent_id",
    case when exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'complaint_category' and column_name = 'level'
    ) then 'Y' else 'N' end as "有level",
    case when exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'complaint_category' and column_name = 'full_name'
    ) then 'Y' else 'N' end as "有full_name",
    case when exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'complaint_category' and column_name = 'path'
    ) then 'Y' else 'N' end as "有path";


--12. 巡检：标签体系是否具备 group 约束能力
select
    'complaint_tag' as "表名",
    case when exists (
        select 1 from information_schema.columns
        where table_schema = 'public' and table_name = 'complaint_tag' and column_name = 'group_id'
    ) then 'Y' else 'N' end as "有group_id",
    case when exists (
        select 1
        from information_schema.table_constraints tc
        where tc.table_schema = 'public'
          and tc.table_name = 'complaint_tag'
          and tc.constraint_type = 'UNIQUE'
    ) then '有唯一约束' else '无唯一约束' end as "唯一约束检查";


--13. 巡检：大文本字段清单
select
    c.table_name as "表名",
    c.column_name as "字段名",
    c.data_type as "类型"
from information_schema.columns c
where c.table_schema = 'public'
  and c.table_name in (
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
  )
  and c.data_type in ('text', 'character varying')
order by c.table_name, c.column_name;

--14. 巡检：给你一个总览版评分视图
with target_tables as (
    select unnest(array[
        'raw_complaint_tickets',
        'complaint_category',
        'complaint_tag_group',
        'complaint_tag',
        'complaint_category_tag_relation',
        'complaint_category_rule',
        'complaint_tag_rule',
        'complaint_ticket_category_result',
        'complaint_ticket_tag_result',
        'complaint_ticket_keyword_result',
        'complaint_ticket_match_detail'
    ]) as table_name
)
select
    t.table_name as "表名",
    case when exists (
        select 1 from information_schema.table_constraints tc
        where tc.table_schema = 'public'
          and tc.table_name = t.table_name
          and tc.constraint_type = 'PRIMARY KEY'
    ) then 1 else 0 end as has_pk,
    case when exists (
        select 1 from information_schema.columns c
        where c.table_schema = 'public'
          and c.table_name = t.table_name
          and c.column_name = 'created_at'
    ) then 1 else 0 end as has_created_at,
    case when exists (
        select 1 from information_schema.columns c
        where c.table_schema = 'public'
          and c.table_name = t.table_name
          and c.column_name = 'updated_at'
    ) then 1 else 0 end as has_updated_at,
    case when exists (
        select 1 from pg_indexes pi
        where pi.schemaname = 'public'
          and pi.tablename = t.table_name
    ) then 1 else 0 end as has_index,
    case when exists (
        select 1
        from information_schema.table_constraints tc
        where tc.table_schema = 'public'
          and tc.table_name = t.table_name
          and tc.constraint_type = 'UNIQUE'
    ) then 1 else 0 end as has_unique
from target_tables t
order by t.table_name;

--15. 如果你想一次性导出结构给我检查

最推荐你跑这 5 段，把结果贴给我：
1. 字段结构
2. 约束
3. 索引
4. `evaluation_status` 巡检
5. 外键索引巡检


# 16. 我建议你先优先检查的几个点
按你现在的项目阶段，最重要的是这几个：
* `complaint_ticket_category_result` 是否有 `ticket_id`、`category_id`、`evaluation_status`
* `complaint_ticket_tag_result` 是否有 `ticket_id`、`tag_id`、`evaluation_status`
* 所有 `*_id` 外键字段是否建索引
* `complaint_category` 是否有 `code` 唯一约束
* `complaint_tag` 是否有 `(group_id, code)` 或 `(group_id, name)` 唯一约束
* `raw_complaint_tickets` 的 `ticket_id` 是否唯一


comment on table complaint_category_rule is '投诉分类规则表，用于配置分类关键词、短语、正则等命中规则';
comment on table complaint_category_tag_relation is '投诉分类与标签基线关系表，用于定义某分类常见推荐标签';
comment on table complaint_tag_rule is '投诉标签规则表，用于配置标签关键词、短语、正则等命中规则';
comment on table complaint_ticket_category_result is '投诉工单分类结果表，存储AI或规则生成的分类候选及最终结果';
comment on table complaint_ticket_keyword_result is '投诉工单关键词抽取结果表，存储从原始投诉文本中提取的关键词';
comment on table complaint_ticket_match_detail is '投诉工单规则命中明细表，记录分类或标签的具体命中依据';
comment on table complaint_ticket_tag_result is '投诉工单标签结果表，存储AI或规则生成的标签结果';
comment on table raw_complaint_tickets is '历史原始投诉工单表，存放投诉原文及原始业务字段';
