import duckdb
con = duckdb.connect("olist.duckdb")
con.execute("""
CREATE OR REPLACE VIEW reviews_dedup AS
SELECT * EXCLUDE (rn) FROM (
  SELECT *, row_number() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC, review_creation_date DESC) rn
  FROM reviews
) WHERE rn = 1;
""")
con.execute("""
CREATE OR REPLACE VIEW orders_enriched AS
SELECT
  o.order_id,
  c.customer_unique_id,
  c.customer_state,
  o.order_status,
  CAST(o.order_purchase_timestamp AS TIMESTAMP) AS purchased_at,
  CAST(o.order_delivered_customer_date AS TIMESTAMP) AS delivered_at,
  CAST(o.order_estimated_delivery_date AS TIMESTAMP) AS estimated_delivery_at,
  date_diff('day', CAST(o.order_purchase_timestamp AS TIMESTAMP), CAST(o.order_delivered_customer_date AS TIMESTAMP)) AS delivery_days,
  date_diff('day', CAST(o.order_estimated_delivery_date AS TIMESTAMP), CAST(o.order_delivered_customer_date AS TIMESTAMP)) AS days_late,
  r.review_score,
  i.items_value,
  i.freight_value
FROM orders o
JOIN customers c USING (customer_id)
LEFT JOIN reviews_dedup r USING (order_id)
LEFT JOIN (
  SELECT order_id, sum(price) items_value, sum(freight_value) freight_value
  FROM order_items GROUP BY order_id
) i USING (order_id);
""")
print(con.execute("SELECT count(*), count(review_score), count(delivery_days) FROM orders_enriched").fetchdf().to_string(index=False))
print(con.execute("SELECT count(DISTINCT customer_unique_id) FROM orders_enriched WHERE order_status='delivered'").fetchdf().to_string(index=False))
