
  
    

    create or replace table `emerald-energy-483903-f3`.`staging_marts`.`revenue_by_shop_daily`
      
    
    

    
    OPTIONS()
    as (
      select
    shop_id,
    date(created_at) as order_date,
    count(*) as work_orders,
    sum(total_cost) as revenue,
    avg(labor_hours) as avg_labor_hours
from `emerald-energy-483903-f3`.`staging_staging`.`stg_work_orders`
where status = 'completed'
group by 1, 2
    );
  