select
    shop_id,
    date(created_at) as order_date,
    count(*) as work_orders,
    sum(total_cost) as revenue,
    avg(labor_hours) as avg_labor_hours
from {{ ref('stg_work_orders') }}
where status = 'completed'
group by 1, 2
