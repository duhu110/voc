--11. 标签统计表

create table if not exists complaint_tag_stats (
    id                              bigserial primary key,
    tag_id                          bigint not null references complaint_tag(id) on delete cascade,
    stat_date                       date not null,

    total_predicted_count           integer not null default 0,
    total_final_count               integer not null default 0,
    total_manual_confirmed_count    integer not null default 0,
    total_correct_count             integer not null default 0,
    total_wrong_count               integer not null default 0,

    avg_confidence_score            numeric(10,4) null,
    hit_rate                        numeric(10,4) null,
    accuracy_rate                   numeric(10,4) null,

    created_at                      timestamp not null default now(),

    constraint uq_tag_stats unique (tag_id, stat_date)
);