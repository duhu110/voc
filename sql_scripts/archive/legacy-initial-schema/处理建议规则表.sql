--15. 处理建议规则表
create table if not exists complaint_disposition_rule (
    id                              bigserial primary key,

    category_id                     bigint null references complaint_category(id) on delete cascade,
    tag_id                          bigint null references complaint_tag(id) on delete cascade,

    rule_name                       varchar(200) not null,
    action_type                     varchar(100) not null,
    action_config                   jsonb null,

    priority                        integer not null default 100,
    is_enabled                      boolean not null default true,

    notes                           text null,
    created_at                      timestamp not null default now(),
    updated_at                      timestamp not null default now()
);