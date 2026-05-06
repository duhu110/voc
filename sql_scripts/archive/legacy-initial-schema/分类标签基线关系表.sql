-- 分类标签基线关系表
create table if not exists complaint_category_tag_relation (
    id                          bigserial primary key,
    category_id                 bigint not null references complaint_category(id) on delete cascade,
    tag_id                      bigint not null references complaint_tag(id) on delete cascade,

    relation_type               varchar(50) not null default 'manual_baseline',
    recommended_weight          numeric(10,4) not null default 1.0000,
    is_required                 boolean not null default false,
    is_default                  boolean not null default false,
    is_enabled                  boolean not null default true,

    source                      varchar(50) not null default 'manual',
    notes                       text null,

    created_at                  timestamp not null default now(),
    updated_at                  timestamp not null default now(),

    constraint uq_category_tag_relation unique (category_id, tag_id, relation_type)
);