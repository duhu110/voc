--分类-关键词统计表

create table if not exists complaint_category_keyword_stat (
    id                              bigserial primary key,
    category_id                     bigint not null references complaint_category(id) on delete cascade,

    keyword                         varchar(200) not null,
    sample_count                    integer not null default 0,
    hit_count                       integer not null default 0,
    confidence_score                numeric(10,4) null,

    source                          varchar(50) not null default 'mining',
    last_calculated_at              timestamp null,

    created_at                      timestamp not null default now(),
    updated_at                      timestamp not null default now(),

    constraint uq_category_keyword_stat unique (category_id, keyword)
);