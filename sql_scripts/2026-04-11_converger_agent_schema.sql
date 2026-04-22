alter table raw_complaint_tickets
add column if not exists converger_agent_status boolean not null default false;

comment on column raw_complaint_tickets.converger_agent_status
is '是否已被 converger_agent 分析过：FALSE=未分析，TRUE=已分析';

create table if not exists converger_agent_result (
    id bigserial primary key,
    ticket_id varchar(100) not null unique,
    primary_level1_code varchar(100) not null,
    primary_level1_name varchar(100) not null,
    primary_level2_code varchar(100) not null,
    primary_level2_name varchar(100) not null,
    primary_leaf_code varchar(100) not null,
    primary_leaf_name varchar(100) not null,
    request_tag_code varchar(100),
    request_tag_name varchar(100),
    emotion_tag_code varchar(100),
    emotion_tag_name varchar(100),
    risk_tag_code varchar(100),
    risk_tag_name varchar(100),
    product_tag_code varchar(100),
    product_tag_name varchar(100),
    line_category varchar(255),
    model_name varchar(100),
    taxonomy_version varchar(50) not null,
    agent_version varchar(50),
    status varchar(50) not null,
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp,
    constraint fk_converger_agent_result_ticket
        foreign key (ticket_id) references raw_complaint_tickets(ticket_id)
);

create index if not exists idx_converger_agent_result_primary_leaf_code
    on converger_agent_result(primary_leaf_code);

create index if not exists idx_converger_agent_result_request_tag_code
    on converger_agent_result(request_tag_code);

create index if not exists idx_converger_agent_result_emotion_tag_code
    on converger_agent_result(emotion_tag_code);

create index if not exists idx_converger_agent_result_risk_tag_code
    on converger_agent_result(risk_tag_code);

create index if not exists idx_converger_agent_result_product_tag_code
    on converger_agent_result(product_tag_code);

create table if not exists converger_resolution_summary_atomic (
    id bigserial primary key,
    source_ticket_id varchar(100) not null unique,
    primary_leaf_code varchar(100) not null,
    primary_leaf_name varchar(100) not null,
    product_tag_code varchar(100),
    product_tag_name varchar(100),
    request_tag_code varchar(100),
    request_tag_name varchar(100),
    risk_tag_code varchar(100),
    risk_tag_name varchar(100),
    emotion_tag_code varchar(100),
    emotion_tag_name varchar(100),
    line_category varchar(255),
    resolution_summary text not null,
    model_name varchar(100),
    taxonomy_version varchar(50) not null,
    agent_version varchar(50),
    status varchar(50) not null default 'active',
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp,
    constraint fk_converger_resolution_summary_ticket
        foreign key (source_ticket_id) references raw_complaint_tickets(ticket_id)
);

create index if not exists idx_converger_resolution_summary_leaf_code
    on converger_resolution_summary_atomic(primary_leaf_code);

create table if not exists converger_handling_advice (
    id bigserial primary key,
    primary_leaf_code varchar(100) not null,
    primary_leaf_name varchar(100) not null,
    product_tag_code varchar(100),
    product_tag_name varchar(100),
    request_tag_code varchar(100),
    request_tag_name varchar(100),
    risk_tag_code varchar(100),
    risk_tag_name varchar(100),
    emotion_tag_code varchar(100),
    emotion_tag_name varchar(100),
    line_category varchar(255),
    advice_title varchar(255) not null,
    advice_content text not null,
    applicability_note text,
    normalized_advice_hash varchar(64) not null,
    source_summary_count int not null default 1,
    latest_source_ticket_id varchar(100),
    status varchar(50) not null default 'active',
    created_at timestamp not null default current_timestamp,
    updated_at timestamp not null default current_timestamp,
    constraint fk_converger_handling_advice_ticket
        foreign key (latest_source_ticket_id) references raw_complaint_tickets(ticket_id)
);

create index if not exists idx_converger_handling_advice_leaf_code
    on converger_handling_advice(primary_leaf_code);

create index if not exists idx_converger_handling_advice_status
    on converger_handling_advice(status);

create unique index if not exists idx_converger_handling_advice_scope
    on converger_handling_advice(
        primary_leaf_code,
        coalesce(product_tag_code, ''),
        coalesce(request_tag_code, ''),
        normalized_advice_hash
    );
