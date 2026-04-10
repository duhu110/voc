with recursive category_tree as (
    select
        id,
        parent_id,
        name,
        code,
        level,
        id::text as path_ids,
        name::text as path_names
    from complaint_category
    where parent_id is null

    union all

    select
        c.id,
        c.parent_id,
        c.name,
        c.code,
        c.level,
        ct.path_ids || '/' || c.id::text,
        ct.path_names || '/' || c.name
    from complaint_category c
    join category_tree ct on c.parent_id = ct.id
)
update complaint_category t
set
    path = ct.path_ids,
    full_name = ct.path_names,
    updated_at = now()
from category_tree ct
where t.id = ct.id;