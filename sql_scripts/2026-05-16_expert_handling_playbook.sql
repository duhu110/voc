create table if not exists expert_handling_playbook (
    id bigserial primary key,
    scenario_key varchar(160) not null,
    title varchar(255) not null,
    case_description text,
    customer_type varchar(80),
    repeat_type varchar(80),
    province varchar(80),
    source_file varchar(255) not null,
    source_sheet_name varchar(255),
    source_case_no integer,
    source_case_title varchar(255),
    source_note varchar(255),
    trigger_keywords jsonb not null default '[]'::jsonb,
    primary_leaf_code varchar(80),
    primary_leaf_name varchar(120),
    product_tag_code varchar(80),
    product_tag_name varchar(120),
    request_tag_code varchar(80),
    request_tag_name varchar(120),
    verify_steps jsonb not null default '[]'::jsonb,
    judgment_rules jsonb not null default '[]'::jsonb,
    execution_steps jsonb not null default '[]'::jsonb,
    callback_requirements jsonb not null default '[]'::jsonb,
    communication_tips jsonb not null default '[]'::jsonb,
    raw_case_text text,
    review_status varchar(40) not null default 'draft',
    priority integer not null default 100,
    status varchar(40) not null default 'active',
    created_at timestamp without time zone not null default current_timestamp,
    updated_at timestamp without time zone not null default current_timestamp,
    constraint uq_expert_playbook_source unique (source_file, source_case_no)
);

create index if not exists idx_expert_playbook_status
    on expert_handling_playbook (status, review_status);

create index if not exists idx_expert_playbook_scenario
    on expert_handling_playbook (scenario_key);

create index if not exists idx_expert_playbook_primary_leaf
    on expert_handling_playbook (primary_leaf_code);

create index if not exists idx_expert_playbook_priority
    on expert_handling_playbook (priority);

create index if not exists idx_expert_playbook_trigger_keywords_gin
    on expert_handling_playbook using gin (trigger_keywords);

comment on table expert_handling_playbook is '专家处理剧本表，存储人工案例沉淀的可执行工单处理经验';
comment on column expert_handling_playbook.scenario_key is '专家剧本场景键，用于规则或召回匹配';
comment on column expert_handling_playbook.trigger_keywords is '触发关键词 JSON 数组';
comment on column expert_handling_playbook.verify_steps is '先核实事实步骤 JSON 数组';
comment on column expert_handling_playbook.judgment_rules is '判断规则和责任 JSON 数组';
comment on column expert_handling_playbook.execution_steps is '执行处理动作 JSON 数组';
comment on column expert_handling_playbook.callback_requirements is '回访和回单要求 JSON 数组';
comment on column expert_handling_playbook.communication_tips is '沟通技巧 JSON 数组';
comment on column expert_handling_playbook.review_status is '审核状态：draft/reviewed/rejected';
comment on column expert_handling_playbook.status is '启用状态：active/inactive';
