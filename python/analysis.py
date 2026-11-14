import duckdb, numpy as np
from scipy import stats
con = duckdb.connect("olist.duckdb", read_only=True)

print("## Repeat purchase rate (delivered orders)")
print(con.execute("""
WITH per_cust AS (
  SELECT customer_unique_id, count(*) n_orders
  FROM orders_enriched WHERE order_status='delivered'
  GROUP BY 1)
SELECT count(*) customers,
       sum(CASE WHEN n_orders>=2 THEN 1 ELSE 0 END) repeat_customers,
       round(100.0*avg(CASE WHEN n_orders>=2 THEN 1 ELSE 0 END),2) repeat_pct
FROM per_cust""").fetchdf().to_string(index=False))

print("\n## Repeat rate by first-purchase quarter (cohort)")
print(con.execute("""
WITH firsts AS (
  SELECT customer_unique_id, min(purchased_at) first_at, count(*) n
  FROM orders_enriched WHERE order_status='delivered' GROUP BY 1)
SELECT date_trunc('quarter', first_at) cohort_q, count(*) customers,
       round(100.0*avg(CASE WHEN n>=2 THEN 1 ELSE 0 END),2) repeat_pct
FROM firsts GROUP BY 1 ORDER BY 1""").fetchdf().to_string(index=False))

print("\n## Late vs on-time delivery and review score")
df = con.execute("""
SELECT days_late, review_score FROM orders_enriched
WHERE order_status='delivered' AND review_score IS NOT NULL AND days_late IS NOT NULL
""").fetchdf()
df["late"] = df.days_late > 0
g = df.groupby("late").review_score.agg(["count","mean","median"])
print(g.round(3).to_string())
a = df.loc[df.late,"review_score"]; b = df.loc[~df.late,"review_score"]
u = stats.mannwhitneyu(a,b, alternative="less")
# rank-biserial effect size
r = 1 - 2*u.statistic/(len(a)*len(b))
print(f"Mann-Whitney U={u.statistic:.0f}, p={u.pvalue:.3g}, rank-biserial r={r:.3f}")
# bootstrap CI for difference in means
rng=np.random.default_rng(0); diffs=[]
av=a.values; bv=b.values
for _ in range(2000):
    diffs.append(rng.choice(av,len(av)).mean()-rng.choice(bv,len(bv)).mean())
print(f"Mean diff (late - on-time) = {av.mean()-bv.mean():.3f}, 95% CI [{np.percentile(diffs,2.5):.3f}, {np.percentile(diffs,97.5):.3f}]")

print("\n## Late rate by days_late bucket")
print(con.execute("""
SELECT CASE WHEN days_late<=0 THEN '0 on time'
            WHEN days_late<=3 THEN '1 1-3 days late'
            WHEN days_late<=7 THEN '2 4-7 days late'
            ELSE '3 8+ days late' END bucket,
       count(*) n, round(avg(review_score),2) avg_score,
       round(100.0*avg(CASE WHEN review_score<=2 THEN 1 ELSE 0 END),1) pct_1_2_stars
FROM orders_enriched WHERE order_status='delivered' AND review_score IS NOT NULL AND days_late IS NOT NULL
GROUP BY 1 ORDER BY 1""").fetchdf().to_string(index=False))
