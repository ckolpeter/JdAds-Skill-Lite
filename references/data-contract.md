# China Ads Lite data contract 1.0

This is a local planning/analysis contract, not an advertising API payload or approval record.
The JSON schemas are authoritative for types/required fields; semantic checks add constraints.
CN/CNY only. No exchange-rate conversion or site eligibility inference. Local SKUs/note aliases, never live account IDs.

## Brief

Use templates/brief.json. Required: platform, market, currency, source, money_decimals, campaign, products, assets, china_context.
source.kind is synthetic or user_provided; source.note identifies the supplied material, not a verified provenance signature.
campaign: mode (profile-local labels), days 1..366, budget (total cap, not daily), account_ready/feature_confirmed (user assertions), target_return (nullable scenario), ad_rate (null compatibility field).
products: sku, title, stock, listing_ready, advertising_eligible, order_revenue, order_costs, target_profit, expected_cvr, terms. buy_box and fee_base_per_order are legacy fields and must be null in China v1.
order_costs keys are cogs, platform_fees, fulfilment, other. All must be explicitly known for economic readiness. Include commissions, expected return handling, non-ad service fees and taxes as appropriate, once. Unknown != zero.
order_revenue is net revenue from one representative order. Refunds/coupons already removed here must not be subtracted twice. Costs and revenue must refer to the same order/cohort.
assets: rights_confirmed, live_ready, creative_supply_ready, lead_followup_ready, consent_process_ready; booleans or null.
china_context: storefront (profile-specific), stage (new/growth/mature/unknown), discount_refund_costs_confirmed, lead_economics.
The confirmations are user statements, not backend verification or legal certification.

## Financial scenarios

Contribution = order_revenue - sum(non-ad order_costs).
Positive contribution is break-even CPA; nonpositive contribution has no feasible positive ad allowance.
Break-even net-revenue ROAS = order_revenue / positive contribution.
Target ad allowance = contribution - target_profit. A missing target stays unknown.
Economic CPC ceiling = positive target ad allowance * assumed expected_cvr, not a live bid or platform-supported control.
expected_cvr and lead close_rate are fractions 0..1, not percentages. At most six decimal places; finite nonnegative inputs up to 1e12.
Money outputs are six-decimal strings. Budget allocations are rounded down to money_decimals; remainder is reserved. These are equal-split pilot accounting scenarios, never optimal allocation or authorization.
Negative contribution/target headroom blocks pilot allocation. Stock, listing, eligibility, feature, rights and creative readiness gaps also block or withhold candidates.
Live mode needs live_ready. JD new_product needs user-declared new stage. No minimum video count, fee rate or benchmark is invented.

## Xhs non-commerce planning

seeding/search/leads do not use SKU contribution or stock as content readiness. They produce note hypotheses and leave budget unallocated.
Use advertising_eligible for the promoted content and listing_ready for note/landing readiness. Campaign and rights confirmations are still required. leads also needs lead_followup_ready and consent_process_ready.
lead_economics is null, or four explicit values: contribution_per_sale, close_rate, handling_cost_per_lead, target_profit_per_lead.
Break-even CPL scenario = contribution_per_sale * close_rate - handling_cost_per_lead. Target ad allowance subtracts target_profit_per_lead. Missing inputs -> unknown. It is expected value, not realized revenue or guaranteed lead quality.
No private-message content, names, phones, cookies or contact records are accepted as structured fields.

## Canonical report

Required: platform, market, currency, source, campaign_mode, goal, start_date, end_date, attribution_window, window_complete, rows_disjoint, sales_scope, revenue_basis, measurement, rows.
goal is sales for JD/Tao/Pdd/Dou/Kua. Xhs: commerce→sales, seeding→engagement, leads→leads, search→traffic/leads/sales.
Dates YYYY-MM-DD must be real and start<=end. All rows share a single date range, currency, goal, export definition and aggregation unit.
sales_scope means the scope of reported outcome events (including leads): paid_click, paid_mixed, paid_and_organic, unknown. The field name is retained for compatibility. Non-unknown requires measurement.attribution_evidence, a supplied export-definition reference, not a proof of causality.
measurement: billing_model (cpc/cpm/ocpm/cpa/other/unknown), attribution_evidence, settlement_confirmed, row_unit (product/campaign/live_session/note).
revenue_basis: gross_reported/net_settled/unknown. Net settlement does not automatically establish profitability. Full-site/managed/live mode does not establish billing or attribution from its name.
Each row has sku, impressions, clicks, orders, spend, revenue; optional leads, qualified_leads, interactions. Counts are nonnegative integers or null. qualified_leads must be a subset of the same leads cohort.
Non-sales reports require orders/revenue null, never fabricated zero revenue. Zero denominators return null, not zero efficiency.
CTR = clicks/impressions. effective_spend_per_click = spend/clicks. cpc is populated only when billing_model=cpc; the quotient alone does not prove billing.
CPL = spend/leads; qualified CPL = spend/qualified_leads; qualification rate = qualified/leads; cost per interaction event = spend/interactions. Interaction events are not unique users; events/impressions may exceed one.
Paid scope yields descriptive reported_roas; blended scope yields reported_blended_return; unknown yields unclassified_return. Non-sales goals withhold all revenue-return fields.
No profit ROI, causality, or incrementality is inferred. Incomplete windows/missing metrics -> INSUFFICIENT_DATA. Zero orders/events -> review, not automatic pause. No automatic scale/hold/pause or bid changes.
Totals are withheld unless rows_disjoint=true. Never sum overlapping campaign/SKU/live totals or halo sales. A null summand keeps the total null; rates are recomputed from sums, not averaged.

## CSV

UTF-8 (BOM accepted), exact header:
`sku,impressions,clicks,orders,spend,revenue`
Or extended:
`sku,impressions,clicks,orders,spend,revenue,leads,qualified_leads,interactions`
Metadata is the report JSON without rows, passed through --meta. Blank cells are null. No arbitrary platform-export, Excel, unit-symbol, localized header or currency conversion support.

## Output and safety

<slug>.plan / <slug>.analysis version 1.0 contains input snapshot and deterministic result. PLAN_READY/ANALYSIS_READY always HUMAN_REVIEW_REQUIRED; publish_authorized/external_reads/external_writes false.
validate rebuilds from the input and compares canonical JSON. This detects changed result/flags, not forged source truth. Model interpretations belong in separate Markdown, never modify deterministic output.
Output directories must not exist; symlink paths are rejected. Input size capped at 2 MB; artifact validation 16 MB; at most 500 rows. Credentials-like fields are rejected. Filters are defense-in-depth, not full PII detection or a sandbox.
Only de-identified aggregates and synthetic examples may be public. Source snapshot is 2026-10-05; update verification before designing live integrations.
