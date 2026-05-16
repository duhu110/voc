create table if not exists complaint_ticket_tag_result (
    id                          bigserial primary key,
    ticket_id                   bigint not null,
    tag_id                      bigint not null references complaint_tag(id) on delete restrict,

    result_source               varchar(50) not null,
    model_version               varchar(100) null,
    rule_version                varchar(100) null,

    confidence_score            numeric(10,4) null,
    ranking_no                  integer not null default 1,

    is_final                    boolean not null default false,
    is_manual_confirmed         boolean not null default false,
    manual_confirmed_by         varchar(100) null,
    manual_confirmed_at         timestamp null,

    matched_by                  varchar(50) not null default 'ai',
    explanation                 text null,

    created_at                  timestamp not null default now(),

    constraint uq_ticket_tag_result unique (ticket_id, tag_id, result_source, ranking_no)
);


alter table complaint_ticket_tag_result
add column if not exists evaluation_status varchar(50) null;

--evaluation_status 可为：
--pending
--confirmed_correct
--confirmed_wrong
--partially_correct