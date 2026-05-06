--工单关键词抽取结果表
create table if not exists complaint_ticket_keyword_result (
    id                          bigserial primary key,
    ticket_id                   bigint not null,

    keyword                     varchar(200) not null,
    keyword_type                varchar(50) not null default 'text',
    weight                      numeric(10,4) null,
    source                      varchar(50) not null default 'ai',

    created_at                  timestamp not null default now()
);