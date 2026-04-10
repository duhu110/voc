create table if not exists complaint_ticket_match_detail (
    id                          bigserial primary key,
    ticket_id                   bigint not null,

    target_type                 varchar(20) not null check (target_type in ('category', 'tag')),
    target_id                   bigint not null,

    rule_type                   varchar(50) not null,
    rule_id                     bigint null,
    matched_text                text null,

    matched_score               numeric(10,4) null,
    matched_by                  varchar(50) not null,

    created_at                  timestamp not null default now()
);