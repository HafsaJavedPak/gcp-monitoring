with source as (
    select * from `emerald-energy-483903-f3`.`raw`.`work_orders`
),
deduped as (
    select *,
        row_number() over (
            partition by work_order_id order by updated_at desc
        ) as rn
    from source
)
select
    work_order_id,
    shop_id,
    customer_id,
    initcap(vehicle_make) as vehicle_make,
    vehicle_model,
    vehicle_year,
    service_type,
    lower(status) as status,
    labor_hours,
    parts_cost,
    labor_cost,
    total_cost,
    technician_id,
    created_at,
    updated_at
from deduped
where rn = 1
  and total_cost >= 0