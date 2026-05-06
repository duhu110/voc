--分类-标签统计关系表

create table if not exists complaint_category_tag_stat_relation (
    id                              bigserial primary key,
    category_id                     bigint not null references complaint_category(id) on delete cascade,
    tag_id                          bigint not null references complaint_tag(id) on delete cascade,

    sample_count                    integer not null default 0,
    cooccurrence_count              integer not null default 0,
    cooccurrence_rate               numeric(10,4) null,
    confidence_score                numeric(10,4) null,

    relation_strength               numeric(10,4) null,
    last_calculated_at              timestamp null,

    created_at                      timestamp not null default now(),
    updated_at                      timestamp not null default now(),

    constraint uq_category_tag_stat_relation unique (category_id, tag_id)
);