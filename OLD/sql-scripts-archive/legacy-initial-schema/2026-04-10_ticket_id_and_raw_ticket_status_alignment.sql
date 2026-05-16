begin;

alter table raw_complaint_tickets
    drop column if exists process_status,
    drop column if exists error_message,
    drop column if exists emotion_level,
    drop column if exists core_appeal_category,
    drop column if exists escalation_risk,
    drop column if exists is_shirking,
    drop column if exists ai_features;

alter table raw_complaint_tickets
    add column process_status boolean not null default false;

create index if not exists idx_ticket_process_status on raw_complaint_tickets(process_status);

alter table complaint_ticket_category_result
    alter column ticket_id type varchar(100)
    using ticket_id::varchar(100);

alter table complaint_ticket_tag_result
    alter column ticket_id type varchar(100)
    using ticket_id::varchar(100);

alter table complaint_ticket_keyword_result
    alter column ticket_id type varchar(100)
    using ticket_id::varchar(100);

alter table complaint_ticket_match_detail
    alter column ticket_id type varchar(100)
    using ticket_id::varchar(100);

commit;
