create table if not exists rag_knowledge_bases (
    id bigserial primary key,
    logical_name varchar(100) not null unique,
    rag_kb_id uuid not null unique,
    display_name varchar(200) not null,
    description text,
    metadata jsonb not null default '{}'::jsonb,
    status varchar(20) not null default 'active',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists rag_documents (
    id bigserial primary key,
    knowledge_base_id bigint not null references rag_knowledge_bases(id),
    rag_document_id uuid not null,
    rag_task_id uuid,
    external_id varchar(300) not null,
    source_table varchar(100) not null,
    source_id varchar(100) not null,
    source_version varchar(80) not null default 'v1',
    content_hash varchar(128),
    title text,
    metadata jsonb not null default '{}'::jsonb,
    task_status varchar(30) not null default 'queued',
    status varchar(20) not null default 'active',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (knowledge_base_id, external_id),
    unique (source_table, source_id, source_version)
);

create table if not exists rag_ingestion_tasks (
    id bigserial primary key,
    rag_task_id uuid not null unique,
    rag_document_id uuid,
    rag_kb_id uuid not null,
    source_table varchar(100),
    source_id varchar(100),
    task_status varchar(30) not null default 'queued',
    progress_current integer not null default 0,
    progress_total integer not null default 4,
    error_message text,
    raw_task jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    completed_at timestamptz
);

create table if not exists rag_retrieval_logs (
    id bigserial primary key,
    ticket_id varchar(100),
    request_id varchar(100),
    knowledge_base_logical_name varchar(100),
    rag_kb_id uuid,
    query text not null,
    top_k integer not null,
    result_count integer not null default 0,
    results jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_rag_documents_source
    on rag_documents (source_table, source_id);

create index if not exists idx_rag_documents_task_status
    on rag_documents (task_status);

create index if not exists idx_rag_ingestion_tasks_status
    on rag_ingestion_tasks (task_status);

create index if not exists idx_rag_retrieval_logs_ticket_id
    on rag_retrieval_logs (ticket_id);

comment on table rag_knowledge_bases is '本系统知识库与 embedding-service knowledge base 的映射';
comment on table rag_documents is '业务对象与 embedding-service document/task 的映射';
comment on table rag_ingestion_tasks is 'RAG 文档入库任务状态快照';
comment on table rag_retrieval_logs is 'AGENT 生成建议时的 RAG 召回日志';
