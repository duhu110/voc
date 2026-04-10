# 数据库设计

本文档基于当前仓库中的 `sql_scripts/` 梳理数据库表设计，说明每张表的作用，并给出带注释的 DDL 参考。

说明：

- 文档优先反映当前数据库实际结构
- 个别结果表的 `updated_at`、唯一约束和索引属于后续巡检修复后补齐，不完全等同于最初脚本版本
- `raw_complaint_tickets` 为业务已有表，当前仓库不负责初始化

## 设计分层

当前数据库按 5 类表来理解最清晰：

1. 源数据层：历史原始工单
2. 主数据层：分类、标签、基线关系
3. 规则层：分类规则、标签规则
4. 结果层：AI 分类、标签、关键词、命中明细
5. 统计与编排层：统计关系、统计表、处理建议

## 1. 源数据层

### raw_complaint_tickets

作用：

- 存放历史原始投诉工单
- 作为 AI 批量分类、打标、关键词提取的输入源
- 作为规则挖掘和效果评估的原始样本来源

说明：

- 当前仓库 `sql_scripts/` 中没有这张表的建表脚本
- 这张表是项目已有业务表，不由当前仓库初始化
- 当前已知主键语义字段为 `ticket_id`

## 2. 主数据层

### complaint_category

作用：

- 存放投诉分类树
- 支持 1 到 4 级分类
- 通过 `parent_id`、`level`、`path`、`full_name` 维护树结构

来源脚本：

- `sql_scripts/建分类表.sql`
- `sql_scripts/初始化分类数据.sql`
- `sql_scripts/二级分类.sql`
- `sql_scripts/三级分类.sql`
- `sql_scripts/四级分类.sql`
- `sql_scripts/回填full_namepath.sql`

DDL：

```sql
create table if not exists complaint_category (
    id                  bigserial primary key,                -- 分类ID
    code                varchar(64) not null unique,          -- 分类编码
    name                varchar(200) not null,                -- 分类名称
    parent_id           bigint null references complaint_category(id) on delete restrict, -- 父级分类
    level               integer not null check (level between 1 and 4), -- 层级
    path                varchar(500) null,                    -- 路径ID串
    full_name           varchar(1000) null,                   -- 完整层级名称
    description         text null,                            -- 分类定义
    keywords            text null,                            -- 典型关键词
    sort_order          integer not null default 0,           -- 排序
    is_enabled          boolean not null default true,        -- 是否启用
    created_at          timestamp not null default now(),     -- 创建时间
    updated_at          timestamp not null default now()      -- 更新时间
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
```

### complaint_tag_group

作用：

- 管理标签组
- 当前标签组包括产品、渠道、根因、责任条线、诉求、风险、情绪、结果等

来源脚本：

- `sql_scripts/建分类表.sql`
- `sql_scripts/初始化标签组数据.sql`

DDL：

```sql
create table if not exists complaint_tag_group (
    id                  bigserial primary key,                -- 标签组ID
    code                varchar(64) not null unique,          -- 标签组编码
    name                varchar(200) not null,                -- 标签组名称
    description         text null,                            -- 标签组说明
    sort_order          integer not null default 0,           -- 排序
    is_enabled          boolean not null default true,        -- 是否启用
    created_at          timestamp not null default now(),     -- 创建时间
    updated_at          timestamp not null default now()      -- 更新时间
);

comment on table complaint_tag_group is '投诉标签组表';
comment on column complaint_tag_group.code is '标签组编码，如 PRODUCT / CHANNEL / ROOT_CAUSE / RISK';
comment on column complaint_tag_group.name is '标签组名称';
comment on column complaint_tag_group.description is '标签组说明';

create index if not exists idx_complaint_tag_group_enabled on complaint_tag_group(is_enabled);
```

### complaint_tag

作用：

- 存放具体标签值
- 通过 `group_id` 归属于标签组

来源脚本：

- `sql_scripts/建分类表.sql`
- `sql_scripts/初始化常用标签值.sql`

DDL：

```sql
create table if not exists complaint_tag (
    id                  bigserial primary key,                -- 标签ID
    group_id            bigint not null references complaint_tag_group(id) on delete restrict, -- 标签组ID
    code                varchar(64) not null,                -- 标签编码
    name                varchar(200) not null,               -- 标签名称
    description         text null,                           -- 标签说明
    sort_order          integer not null default 0,          -- 排序
    is_enabled          boolean not null default true,       -- 是否启用
    created_at          timestamp not null default now(),    -- 创建时间
    updated_at          timestamp not null default now(),    -- 更新时间
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
```

### complaint_category_tag_relation

作用：

- 存放分类与标签之间的人工基线关系
- 用于 AI 打标签时的推荐、校验和后续修正
- 当前比聊天中后续精简版略重，包含 `is_required`、`is_default`、`source`

来源脚本：

- `sql_scripts/分类标签基线关系表.sql`

DDL：

```sql
create table if not exists complaint_category_tag_relation (
    id                          bigserial primary key,        -- 关系ID
    category_id                 bigint not null references complaint_category(id) on delete cascade, -- 分类ID
    tag_id                      bigint not null references complaint_tag(id) on delete cascade,       -- 标签ID
    relation_type               varchar(50) not null default 'manual_baseline', -- 关系类型
    recommended_weight          numeric(10,4) not null default 1.0000,           -- 推荐权重
    is_required                 boolean not null default false,                  -- 是否强关联
    is_default                  boolean not null default false,                  -- 是否默认推荐
    is_enabled                  boolean not null default true,                   -- 是否启用
    source                      varchar(50) not null default 'manual',           -- 来源
    notes                       text null,                                       -- 备注
    created_at                  timestamp not null default now(),                -- 创建时间
    updated_at                  timestamp not null default now(),                -- 更新时间
    constraint uq_category_tag_relation unique (category_id, tag_id, relation_type)
);
```

## 3. 规则层

### complaint_category_rule

作用：

- 存放分类命中规则
- 支持关键词、短语、正则、否定规则、权重和优先级
- 也可作为后续从历史工单中反向沉淀出来的规则候选载体

来源脚本：

- `sql_scripts/分类关键词规则表.sql`

DDL：

```sql
create table if not exists complaint_category_rule (
    id                          bigserial primary key,        -- 规则ID
    category_id                 bigint not null references complaint_category(id) on delete cascade, -- 分类ID
    rule_type                   varchar(50) not null default 'keyword',  -- 规则类型
    rule_operator               varchar(50) not null default 'contains', -- 操作符
    rule_content                text not null,                           -- 规则内容
    weight                      numeric(10,4) not null default 1.0000,   -- 权重
    priority                    integer not null default 100,            -- 优先级
    is_negative                 boolean not null default false,          -- 否定规则
    is_enabled                  boolean not null default true,           -- 是否启用
    source                      varchar(50) not null default 'manual',   -- 规则来源
    sample_count                integer not null default 0,              -- 样本量
    hit_count                   integer not null default 0,              -- 命中次数
    correct_hit_count           integer not null default 0,              -- 正确命中次数
    created_at                  timestamp not null default now(),        -- 创建时间
    updated_at                  timestamp not null default now()         -- 更新时间
);
```

### complaint_tag_rule

作用：

- 存放标签命中规则
- 结构与分类规则表对称

来源脚本：

- `sql_scripts/标签关键词规则表.sql`

DDL：

```sql
create table if not exists complaint_tag_rule (
    id                          bigserial primary key,        -- 规则ID
    tag_id                      bigint not null references complaint_tag(id) on delete cascade, -- 标签ID
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
```

## 4. 结果层

### complaint_ticket_category_result

作用：

- 存放工单分类结果
- 支持 AI、规则、人工等多来源结果并存
- 支持候选排序、最终结果标记、人工确认和轻量评估状态

来源脚本：

- `sql_scripts/工单分类结果表.sql`

DDL：

```sql
create table if not exists complaint_ticket_category_result (
    id                          bigserial primary key,        -- 结果ID
    ticket_id                   bigint not null,              -- 工单ID
    category_id                 bigint not null references complaint_category(id) on delete restrict, -- 分类ID
    result_source               varchar(50) not null,         -- 结果来源
    model_version               varchar(100) null,            -- 模型版本
    rule_version                varchar(100) null,            -- 规则版本
    confidence_score            numeric(10,4) null,           -- 置信度
    ranking_no                  integer not null default 1,   -- 候选排序
    is_final                    boolean not null default false, -- 是否最终结果
    is_manual_confirmed         boolean not null default false, -- 是否人工确认
    manual_confirmed_by         varchar(100) null,            -- 确认人
    manual_confirmed_at         timestamp null,               -- 确认时间
    matched_by                  varchar(50) not null default 'ai', -- 命中方式
    explanation                 text null,                    -- 解释说明
    created_at                  timestamp not null default now(),   -- 创建时间
    updated_at                  timestamp not null default now(),   -- 更新时间
    evaluation_status           varchar(50) null              -- 评估状态
);
```

### complaint_ticket_tag_result

作用：

- 存放工单多标签结果
- 支持同一工单多个标签候选

来源脚本：

- `sql_scripts/工单标签结果表.sql`

DDL：

```sql
create table if not exists complaint_ticket_tag_result (
    id                          bigserial primary key,
    ticket_id                   bigint not null,              -- 工单ID
    tag_id                      bigint not null references complaint_tag(id) on delete restrict, -- 标签ID
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
    updated_at                  timestamp not null default now(),
    evaluation_status           varchar(50) null,
    constraint uq_ticket_tag_result unique (ticket_id, tag_id, result_source, ranking_no)
);
```

### complaint_ticket_keyword_result

作用：

- 存放从工单原文中抽取出的关键词
- 为规则沉淀和统计分析提供原始候选

来源脚本：

- `sql_scripts/工单关键词抽取结果表.sql`

DDL：

```sql
create table if not exists complaint_ticket_keyword_result (
    id                          bigserial primary key,
    ticket_id                   bigint not null,              -- 工单ID
    keyword                     varchar(200) not null,        -- 关键词
    keyword_type                varchar(50) not null default 'text', -- 关键词类型
    weight                      numeric(10,4) null,           -- 权重
    source                      varchar(50) not null default 'ai', -- 来源
    created_at                  timestamp not null default now(),
    updated_at                  timestamp not null default now()
);
```

### complaint_ticket_match_detail

作用：

- 存放规则或 AI 命中明细
- 用来解释“为什么命中了这个分类或标签”

来源脚本：

- `sql_scripts/8. 工单规则命中明细表.sql`

DDL：

```sql
create table if not exists complaint_ticket_match_detail (
    id                          bigserial primary key,
    ticket_id                   bigint not null,              -- 工单ID
    target_type                 varchar(20) not null check (target_type in ('category', 'tag')), -- 命中目标类型
    target_id                   bigint not null,              -- 目标ID
    rule_type                   varchar(50) not null,         -- 规则类型
    rule_id                     bigint null,                  -- 规则ID
    matched_text                text null,                    -- 命中文本
    matched_score               numeric(10,4) null,           -- 命中分数
    matched_by                  varchar(50) not null,         -- 命中来源
    created_at                  timestamp not null default now(),
    updated_at                  timestamp not null default now()
);
```

## 5. 统计与编排层

### complaint_category_stats

作用：按天汇总分类命中和准确率。

来源脚本：`sql_scripts/分类统计表.sql`

```sql
create table if not exists complaint_category_stats (
    id                              bigserial primary key,    -- 统计ID
    category_id                     bigint not null references complaint_category(id) on delete cascade, -- 分类ID
    stat_date                       date not null,            -- 统计日期
    total_predicted_count           integer not null default 0, -- 预测次数
    total_final_count               integer not null default 0, -- 最终采纳次数
    total_manual_confirmed_count    integer not null default 0, -- 人工确认次数
    total_correct_count             integer not null default 0, -- 正确次数
    total_wrong_count               integer not null default 0, -- 错误次数
    avg_confidence_score            numeric(10,4) null,       -- 平均置信度
    hit_rate                        numeric(10,4) null,       -- 命中率
    accuracy_rate                   numeric(10,4) null,       -- 准确率
    created_at                      timestamp not null default now(), -- 创建时间
    constraint uq_category_stats unique (category_id, stat_date)
);
```

### complaint_tag_stats

作用：按天汇总标签命中和准确率。

来源脚本：`sql_scripts/11. 标签统计表.sql`

```sql
create table if not exists complaint_tag_stats (
    id                              bigserial primary key,    -- 统计ID
    tag_id                          bigint not null references complaint_tag(id) on delete cascade, -- 标签ID
    stat_date                       date not null,            -- 统计日期
    total_predicted_count           integer not null default 0, -- 预测次数
    total_final_count               integer not null default 0, -- 最终采纳次数
    total_manual_confirmed_count    integer not null default 0, -- 人工确认次数
    total_correct_count             integer not null default 0, -- 正确次数
    total_wrong_count               integer not null default 0, -- 错误次数
    avg_confidence_score            numeric(10,4) null,       -- 平均置信度
    hit_rate                        numeric(10,4) null,       -- 命中率
    accuracy_rate                   numeric(10,4) null,       -- 准确率
    created_at                      timestamp not null default now(), -- 创建时间
    constraint uq_tag_stats unique (tag_id, stat_date)
);
```

### complaint_category_tag_stat_relation

作用：统计分类和标签的共现关系，用于动态推荐和校正基线关系。

来源脚本：`sql_scripts/分类-标签统计关系表.sql`

```sql
create table if not exists complaint_category_tag_stat_relation (
    id                              bigserial primary key,    -- 关系统计ID
    category_id                     bigint not null references complaint_category(id) on delete cascade, -- 分类ID
    tag_id                          bigint not null references complaint_tag(id) on delete cascade, -- 标签ID
    sample_count                    integer not null default 0, -- 样本数
    cooccurrence_count              integer not null default 0, -- 共现次数
    cooccurrence_rate               numeric(10,4) null,       -- 共现率
    confidence_score                numeric(10,4) null,       -- 置信度
    relation_strength               numeric(10,4) null,       -- 关系强度
    last_calculated_at              timestamp null,           -- 最近计算时间
    created_at                      timestamp not null default now(), -- 创建时间
    updated_at                      timestamp not null default now(), -- 更新时间
    constraint uq_category_tag_stat_relation unique (category_id, tag_id)
);
```

### complaint_category_keyword_stat

作用：统计分类与关键词关系。

来源脚本：`sql_scripts/分类-关键词统计表.sql`

```sql
create table if not exists complaint_category_keyword_stat (
    id                              bigserial primary key,    -- 统计ID
    category_id                     bigint not null references complaint_category(id) on delete cascade, -- 分类ID
    keyword                         varchar(200) not null,    -- 关键词
    sample_count                    integer not null default 0, -- 样本数
    hit_count                       integer not null default 0, -- 命中次数
    confidence_score                numeric(10,4) null,       -- 置信度
    source                          varchar(50) not null default 'mining', -- 来源
    last_calculated_at              timestamp null,           -- 最近计算时间
    created_at                      timestamp not null default now(), -- 创建时间
    updated_at                      timestamp not null default now(), -- 更新时间
    constraint uq_category_keyword_stat unique (category_id, keyword)
);
```

### complaint_tag_keyword_stat

作用：统计标签与关键词关系。

来源脚本：`sql_scripts/14. 标签-关键词统计表.sql`

```sql
create table if not exists complaint_tag_keyword_stat (
    id                              bigserial primary key,    -- 统计ID
    tag_id                          bigint not null references complaint_tag(id) on delete cascade, -- 标签ID
    keyword                         varchar(200) not null,    -- 关键词
    sample_count                    integer not null default 0, -- 样本数
    hit_count                       integer not null default 0, -- 命中次数
    confidence_score                numeric(10,4) null,       -- 置信度
    source                          varchar(50) not null default 'mining', -- 来源
    last_calculated_at              timestamp null,           -- 最近计算时间
    created_at                      timestamp not null default now(), -- 创建时间
    updated_at                      timestamp not null default now(), -- 更新时间
    constraint uq_tag_keyword_stat unique (tag_id, keyword)
);
```

### complaint_disposition_rule

作用：根据分类和标签生成处理建议、派单动作或风险编排。

来源脚本：`sql_scripts/处理建议规则表.sql`

```sql
create table if not exists complaint_disposition_rule (
    id                              bigserial primary key,        -- 规则ID
    category_id                     bigint null references complaint_category(id) on delete cascade, -- 适用分类
    tag_id                          bigint null references complaint_tag(id) on delete cascade,       -- 适用标签
    rule_name                       varchar(200) not null,        -- 规则名称
    action_type                     varchar(100) not null,        -- 动作类型
    action_config                   jsonb null,                   -- 动作配置
    priority                        integer not null default 100, -- 优先级
    is_enabled                      boolean not null default true, -- 是否启用
    notes                           text null,                    -- 备注
    created_at                      timestamp not null default now(), -- 创建时间
    updated_at                      timestamp not null default now()  -- 更新时间
);
```

## 6. 初始化数据脚本说明

当前分类和标签初始化主要来自：

- `sql_scripts/初始化分类数据.sql`
- `sql_scripts/二级分类.sql`
- `sql_scripts/三级分类.sql`
- `sql_scripts/四级分类.sql`
- `sql_scripts/初始化标签组数据.sql`
- `sql_scripts/初始化常用标签值.sql`
- `sql_scripts/回填full_namepath.sql`

说明：

- `sql_scripts/一级分类.sql` 当前为空，一级分类实际写在 `初始化分类数据.sql`
- `回填full_namepath.sql` 依赖分类树已全部插入后执行
- 统计表和处理建议表当前更像后续阶段能力，但脚本已经准备完毕
