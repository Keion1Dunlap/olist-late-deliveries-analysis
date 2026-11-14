# Late Deliveries Drive Low Ratings on Olist, and Repeat Buying Is Rare

## The question
Olist is a Brazilian marketplace connecting small sellers to customers. Two questions matter for growth: how many customers come back, and what makes buyers unhappy enough to leave a bad review?

## Data
The public Olist dataset (Kaggle, "Brazilian E-Commerce Public Dataset by Olist"): 99,441 orders placed from September 2016 to October 2018, across nine related tables.

Cleaning decisions:
- **Customer identity:** Each order gets a new `customer_id`, so repeat purchases are counted on `customer_unique_id` (96,096 distinct people).
- **Duplicate reviews:** 551 extra review rows. I kept the most recent review per order.
- **Delivery timing:** Days late = delivered date minus estimated delivery date. Zero or negative counts as on time, including early deliveries.
- **Excluded:** Orders that were not delivered, and the 8 delivered orders with no delivery date.

## Findings

**1. Repeat purchases are rare.** Of 93,358 customers with a delivered order, 2,801 (3.0%) bought more than once. Within 90 days of a first purchase, repeat rates were about 2% across cohorts from late 2016 through mid-2018, with no clear upward or downward trend.

**2. Late deliveries drive low ratings.** Among 95,824 delivered orders with a review and delivery dates, 6,381 arrived after the estimated date.
- On-time orders averaged 4.29 stars. Late orders averaged 2.27 stars.
- The gap is -2.02 stars (95% bootstrap CI: -2.06 to -1.98). A Mann-Whitney test gives p < 0.001, with a rank-biserial effect size of 0.64, a large effect.

**3. The longer the delay, the worse the rating.**

| Delivery vs. estimate | Orders | Avg. stars | Share rating 1–2 stars |
|---|---|---|---|
| On time or early | 89,443 | 4.29 | 9.3% |
| 1–3 days late | 1,852 | 3.29 | 32.1% |
| 4–7 days late | 1,748 | 2.10 | 67.7% |
| 8+ days late | 2,781 | 1.70 | 79.3% |

**4. Lateness varies by region.** Among states with at least 1,000 delivered orders, late rates ranged from 8.2% (SC) to 13.8% (CE), with RJ, a high-volume state, at 12.1%.

## Recommendation
Repeat buying is low across the board, so the bigger lever is delivery reliability. Late orders cut ratings by roughly half, and ratings are the most visible signal buyers see. I'd prioritize delivery-estimate accuracy and carrier performance in the highest-late regions (CE, BA, RJ), and measure whether fixing lateness moves 90-day repeat rates.

## Limitations
- **Correlation, not causation.** Late orders may differ in other ways, such as product category, seller, or distance. This analysis doesn't control for those.
- **Repeat purchase vs. delivery not yet tested.** The data shows delivery hurts ratings. It doesn't show whether late deliveries reduce return purchases, which is the real retention question. That's the natural next step.
- **Observational sample, not a random experiment.** Reviews are self-selected, so the ratings describe the buyers who chose to leave one.
- **Dataset age.** The data covers 2016–2018. Marketplace behavior may have changed since then.
