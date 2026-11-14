import duckdb
D = "olist_data"
con = duckdb.connect("olist.duckdb")
tables = {
    "customers": "olist_customers_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}
for t, f in tables.items():
    con.execute(f"CREATE OR REPLACE TABLE {t} AS SELECT * FROM read_csv('{D}/{f}', header=true, all_varchar=false, ignore_errors=false, sample_size=-1)")

checks = {
 "orders total": "SELECT count(*) FROM orders",
 "distinct order_id": "SELECT count(DISTINCT order_id) FROM orders",
 "distinct customer_id": "SELECT count(DISTINCT customer_id) FROM customers",
 "distinct customer_unique_id": "SELECT count(DISTINCT customer_unique_id) FROM customers",
 "order status counts": "SELECT order_status, count(*) n FROM orders GROUP BY 1 ORDER BY 2 DESC",
 "orders w/o delivered date": "SELECT count(*) FROM orders WHERE order_delivered_customer_date IS NULL",
 "delivered but null date": "SELECT count(*) FROM orders WHERE order_status='delivered' AND order_delivered_customer_date IS NULL",
 "reviews rows": "SELECT count(*), count(DISTINCT order_id), count(DISTINCT review_id) FROM reviews",
 "review_score dist": "SELECT review_score, count(*) FROM reviews GROUP BY 1 ORDER BY 1",
 "orders with review": "SELECT count(DISTINCT o.order_id) FROM orders o JOIN reviews r USING(order_id)",
 "orders w/ payments": "SELECT count(DISTINCT order_id) FROM payments",
 "products w/o category": "SELECT count(*) FROM products WHERE product_category_name IS NULL",
 "purchase range": "SELECT min(order_purchase_timestamp), max(order_purchase_timestamp) FROM orders",
}
for name, q in checks.items():
    print("\n##", name)
    print(con.execute(q).fetchdf().to_string(index=False))
