--第一批：先建分类表
-- 1. 投诉分类表
create table if not exists complaint_category (
    id                  bigserial primary key,
    code                varchar(64) not null unique,
    name                varchar(200) not null,
    parent_id           bigint null references complaint_category(id) on delete restrict,
    level               integer not null check (level between 1 and 4),
    path                varchar(500) null,
    full_name           varchar(1000) null,
    description         text null,
    keywords            text null,
    sort_order          integer not null default 0,
    is_enabled          boolean not null default true,
    created_at          timestamp not null default now(),
    updated_at          timestamp not null default now()
);

comment on table complaint_category is '投诉分类主数据表';
comment on column complaint_category.code is '分类编码，建议分层编码，如 FEE / FEE_PACKAGE / FEE_PACKAGE_MONTHLY';
comment on column complaint_category.name is '分类名称';
comment on column complaint_category.parent_id is '父级分类ID';
comment on column complaint_category.level is '分类层级，1-4';
comment on column complaint_category.path is '分类路径ID串，如 1/12/35';
comment on column complaint_category.full_name is '完整名称，如 资费与收费争议/套餐收费争议/套餐月费不认可';
comment on column complaint_category.description is '分类定义';
comment on column complaint_category.keywords is '典型关键词，逗号分隔或自然语言均可';
comment on column complaint_category.sort_order is '排序';
comment on column complaint_category.is_enabled is '是否启用';

create index if not exists idx_complaint_category_parent_id on complaint_category(parent_id);
create index if not exists idx_complaint_category_level on complaint_category(level);
create index if not exists idx_complaint_category_enabled on complaint_category(is_enabled);

-- 2. 标签组表
create table if not exists complaint_tag_group (
    id                  bigserial primary key,
    code                varchar(64) not null unique,
    name                varchar(200) not null,
    description         text null,
    sort_order          integer not null default 0,
    is_enabled          boolean not null default true,
    created_at          timestamp not null default now(),
    updated_at          timestamp not null default now()
);

comment on table complaint_tag_group is '投诉标签组表';
comment on column complaint_tag_group.code is '标签组编码，如 PRODUCT / CHANNEL / ROOT_CAUSE / RISK';
comment on column complaint_tag_group.name is '标签组名称';
comment on column complaint_tag_group.description is '标签组说明';

create index if not exists idx_complaint_tag_group_enabled on complaint_tag_group(is_enabled);

-- 3. 标签值表
create table if not exists complaint_tag (
    id                  bigserial primary key,
    group_id            bigint not null references complaint_tag_group(id) on delete restrict,
    code                varchar(64) not null,
    name                varchar(200) not null,
    description         text null,
    sort_order          integer not null default 0,
    is_enabled          boolean not null default true,
    created_at          timestamp not null default now(),
    updated_at          timestamp not null default now(),
    constraint uq_complaint_tag_group_code unique (group_id, code),
    constraint uq_complaint_tag_group_name unique (group_id, name)
);

comment on table complaint_tag is '投诉标签值表';
comment on column complaint_tag.group_id is '所属标签组ID';
comment on column complaint_tag.code is '标签编码，如 MOBILE / BROADBAND / HALL / MISLEADING';
comment on column complaint_tag.name is '标签名称';
comment on column complaint_tag.description is '标签说明';

create index if not exists idx_complaint_tag_group_id on complaint_tag(group_id);
create index if not exists idx_complaint_tag_enabled on complaint_tag(is_enabled);