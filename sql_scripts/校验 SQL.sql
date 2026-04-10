--看各层级数量：
select level, count(*) as cnt
from complaint_category
group by level
order by level;


--看树是否完整：
select
    code,
    name,
    level,
    parent_id,
    full_name
from complaint_category
order by level, sort_order, id;


--查看某个一级分类下的全量结构，例如资费类：
select
    c1.name as l1,
    c2.name as l2,
    c3.name as l3,
    c4.name as l4
from complaint_category c1
left join complaint_category c2 on c2.parent_id = c1.id and c2.level = 2
left join complaint_category c3 on c3.parent_id = c2.id and c3.level = 3
left join complaint_category c4 on c4.parent_id = c3.id and c4.level = 4
where c1.code = 'FEE'
order by c2.sort_order, c3.sort_order, c4.sort_order;