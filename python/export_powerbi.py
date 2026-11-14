import os, duckdb
os.makedirs("powerbi", exist_ok=True)
con = duckdb.connect("olist.duckdb")
con.execute("COPY (SELECT * FROM orders_enriched) TO 'powerbi/orders_enriched.csv' (HEADER)")
con.execute("""COPY (WITH f AS (SELECT customer_unique_id, min(purchased_at) first_at FROM orders_enriched WHERE order_status='delivered' GROUP BY 1),
 n AS (SELECT customer_unique_id, count(*) n_orders FROM orders_enriched WHERE order_status='delivered' GROUP BY 1)
 SELECT f.customer_unique_id, date_trunc('quarter', f.first_at) cohort_quarter, n.n_orders, (n.n_orders>=2) is_repeat
 FROM f JOIN n USING(customer_unique_id)) TO 'powerbi/customers_cohorts.csv' (HEADER)""")
con.execute("""COPY (SELECT customer_state, count(*) delivered_orders, round(100.0*avg(CASE WHEN days_late>0 THEN 1 ELSE 0 END),2) late_pct
 FROM orders_enriched WHERE order_status='delivered' AND days_late IS NOT NULL GROUP BY 1) TO 'powerbi/state_late_rates.csv' (HEADER)""")
print("exported to powerbi/")
