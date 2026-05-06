create table if not exists complaint_tag_rule (
    id                          bigserial primary key,
    tag_id                      bigint not null references complaint_tag(id) on delete cascade,

    rule_type                   varchar(50) not null default 'keyword',
    rule_operator               varchar(50) not null default 'contains',
    rule_content                text not null,

    weight                      numeric(10,4) not null default 1.0000,
    priority                    integer not null default 100,
    is_negative                 boolean not null default false,
    is_enabled                  boolean not null default true,

    source                      varchar(50) not null default 'manual',
    sample_count                integer not null default 0,
    hit_count                   integer not null default 0,
    correct_hit_count           integer not null default 0,

    created_at                  timestamp not null default now(),
    updated_at                  timestamp not null default now()
);