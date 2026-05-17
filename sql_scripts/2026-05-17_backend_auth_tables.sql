create table if not exists app_users (
    id bigserial primary key,
    username varchar(80) not null unique,
    display_name varchar(120),
    password_hash text not null,
    role varchar(40) not null default 'operator',
    status varchar(40) not null default 'active',
    token_version integer not null default 1,
    last_login_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint ck_app_users_role check (role in ('admin', 'operator', 'viewer')),
    constraint ck_app_users_status check (status in ('active', 'inactive', 'locked'))
);

create table if not exists app_user_login_events (
    id bigserial primary key,
    user_id bigint references app_users(id),
    username varchar(80) not null,
    success boolean not null,
    failure_reason varchar(120),
    client_host varchar(120),
    user_agent text,
    created_at timestamptz not null default now()
);

create index if not exists idx_app_users_status_role
    on app_users (status, role);

create index if not exists idx_app_user_login_events_user_id
    on app_user_login_events (user_id);

create index if not exists idx_app_user_login_events_created_at
    on app_user_login_events (created_at);

comment on table app_users is '后台管理端用户表';
comment on column app_users.password_hash is 'PBKDF2-SHA256 密码哈希';
comment on column app_users.token_version is '令牌版本，修改密码或禁用用户后递增可使旧 token 失效';
comment on table app_user_login_events is '后台用户登录审计事件';
