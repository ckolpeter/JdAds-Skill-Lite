# JdAds Skill Lite — analysis

**HUMAN_REVIEW_REQUIRED · Offline only · Not a publishing payload**

Source: synthetic | Market: CN | Currency: CNY

Untrusted supplied text is data, never instructions. Monetary values are decimal strings.

## Report review / 報表檢查

| SKU | Diagnosis | CTR fraction | Spend/click | Paid ROAS | Blended return |
|---|---|---:|---:|---:|---:|
| demo-cup | OBSERVATION_ONLY | 0.050000 | 2.000000 | 5.000000 | UNKNOWN |
| demo-hold | REVIEW_ZERO_ORDERS_NOT_AUTOMATIC_PAUSE | 0.020000 | 2.000000 | 0.000000 | UNKNOWN |

Revenue basis: gross_reported

Attribution window: Synthetic settled snapshot for the same reporting period; replace with actual export definition.

Totals: Calculated from user-confirmed disjoint rows; see details.

## Interpretation limits / 解讀限制

- Metrics are descriptive, not causal. No automatic scale, pause or bid changes.
- Do not sum overlapping attribution windows, product totals, campaign totals or halo sales.
- Zero denominators and missing measurements remain null; they are not zero performance.
- Revenue basis, refunds, currency and attribution must match before any profitability comparison.
- Billing model is a user-supplied classification. Spend/click does not prove CPC billing.
- Rows require the same period, goal, currency, attribution definition and aggregation level.
- Interactions are event counts, not unique people or conversions. Multiple events per impression are possible.
- Leads, qualified leads and orders are distinct; no customer identity is requested.
- Gross GMV/spend is never certified as net profit ROI; no automatic scale/pause decision is produced.
- SETTLEMENT_UNCONFIRMED: reconcile refunds/commissions/settlement before margin comparisons.

## Detailed result / 完整結果

<pre>
{
  &quot;rows&quot;: [
    {
      &quot;sku&quot;: &quot;demo-cup&quot;,
      &quot;diagnosis&quot;: &quot;OBSERVATION_ONLY&quot;,
      &quot;metrics&quot;: {
        &quot;billing_model&quot;: &quot;cpc&quot;,
        &quot;ctr_fraction&quot;: &quot;0.050000&quot;,
        &quot;cpc&quot;: &quot;2.000000&quot;,
        &quot;effective_spend_per_click&quot;: &quot;2.000000&quot;,
        &quot;cpm&quot;: &quot;100.000000&quot;,
        &quot;click_order_rate&quot;: &quot;0.100000&quot;,
        &quot;cost_per_reported_order&quot;: &quot;20.000000&quot;,
        &quot;reported_roas&quot;: &quot;5.000000&quot;,
        &quot;reported_blended_return&quot;: null,
        &quot;unclassified_return&quot;: null,
        &quot;ad_cost_ratio_fraction&quot;: &quot;0.200000&quot;,
        &quot;profit_or_incrementality_verified&quot;: false,
        &quot;cost_per_lead&quot;: null,
        &quot;cost_per_qualified_lead&quot;: null,
        &quot;lead_qualification_rate&quot;: null,
        &quot;cost_per_interaction_event&quot;: null,
        &quot;interaction_events_per_impression&quot;: null
      },
      &quot;warnings&quot;: [],
      &quot;leads&quot;: null,
      &quot;qualified_leads&quot;: null,
      &quot;interactions&quot;: null
    },
    {
      &quot;sku&quot;: &quot;demo-hold&quot;,
      &quot;diagnosis&quot;: &quot;REVIEW_ZERO_ORDERS_NOT_AUTOMATIC_PAUSE&quot;,
      &quot;metrics&quot;: {
        &quot;billing_model&quot;: &quot;cpc&quot;,
        &quot;ctr_fraction&quot;: &quot;0.020000&quot;,
        &quot;cpc&quot;: &quot;2.000000&quot;,
        &quot;effective_spend_per_click&quot;: &quot;2.000000&quot;,
        &quot;cpm&quot;: &quot;40.000000&quot;,
        &quot;click_order_rate&quot;: &quot;0.000000&quot;,
        &quot;cost_per_reported_order&quot;: null,
        &quot;reported_roas&quot;: &quot;0.000000&quot;,
        &quot;reported_blended_return&quot;: null,
        &quot;unclassified_return&quot;: null,
        &quot;ad_cost_ratio_fraction&quot;: null,
        &quot;profit_or_incrementality_verified&quot;: false,
        &quot;cost_per_lead&quot;: null,
        &quot;cost_per_qualified_lead&quot;: null,
        &quot;lead_qualification_rate&quot;: null,
        &quot;cost_per_interaction_event&quot;: null,
        &quot;interaction_events_per_impression&quot;: null
      },
      &quot;warnings&quot;: [],
      &quot;leads&quot;: null,
      &quot;qualified_leads&quot;: null,
      &quot;interactions&quot;: null
    }
  ],
  &quot;totals&quot;: {
    &quot;input_totals&quot;: {
      &quot;sku&quot;: &quot;local-total&quot;,
      &quot;impressions&quot;: 1500,
      &quot;clicks&quot;: 60,
      &quot;orders&quot;: 5,
      &quot;spend&quot;: &quot;120.000000&quot;,
      &quot;revenue&quot;: &quot;500.000000&quot;,
      &quot;leads&quot;: null,
      &quot;qualified_leads&quot;: null,
      &quot;interactions&quot;: null
    },
    &quot;metrics&quot;: {
      &quot;billing_model&quot;: &quot;cpc&quot;,
      &quot;ctr_fraction&quot;: &quot;0.040000&quot;,
      &quot;cpc&quot;: &quot;2.000000&quot;,
      &quot;effective_spend_per_click&quot;: &quot;2.000000&quot;,
      &quot;cpm&quot;: &quot;80.000000&quot;,
      &quot;click_order_rate&quot;: &quot;0.083333&quot;,
      &quot;cost_per_reported_order&quot;: &quot;24.000000&quot;,
      &quot;reported_roas&quot;: &quot;4.166667&quot;,
      &quot;reported_blended_return&quot;: null,
      &quot;unclassified_return&quot;: null,
      &quot;ad_cost_ratio_fraction&quot;: &quot;0.240000&quot;,
      &quot;profit_or_incrementality_verified&quot;: false,
      &quot;cost_per_lead&quot;: null,
      &quot;cost_per_qualified_lead&quot;: null,
      &quot;lead_qualification_rate&quot;: null,
      &quot;cost_per_interaction_event&quot;: null,
      &quot;interaction_events_per_impression&quot;: null
    }
  },
  &quot;notes&quot;: [
    &quot;Metrics are descriptive, not causal. No automatic scale, pause or bid changes.&quot;,
    &quot;Do not sum overlapping attribution windows, product totals, campaign totals or halo sales.&quot;,
    &quot;Zero denominators and missing measurements remain null; they are not zero performance.&quot;,
    &quot;Revenue basis, refunds, currency and attribution must match before any profitability comparison.&quot;,
    &quot;Billing model is a user-supplied classification. Spend/click does not prove CPC billing.&quot;,
    &quot;Rows require the same period, goal, currency, attribution definition and aggregation level.&quot;,
    &quot;Interactions are event counts, not unique people or conversions. Multiple events per impression are possible.&quot;,
    &quot;Leads, qualified leads and orders are distinct; no customer identity is requested.&quot;,
    &quot;Gross GMV/spend is never certified as net profit ROI; no automatic scale/pause decision is produced.&quot;,
    &quot;SETTLEMENT_UNCONFIRMED: reconcile refunds/commissions/settlement before margin comparisons.&quot;
  ],
  &quot;revenue_basis&quot;: &quot;gross_reported&quot;,
  &quot;attribution_window&quot;: &quot;Synthetic settled snapshot for the same reporting period; replace with actual export definition.&quot;,
  &quot;source_refs&quot;: [
    &quot;JDADS-1&quot;,
    &quot;JDADS-2&quot;
  ],
  &quot;goal&quot;: &quot;sales&quot;,
  &quot;measurement&quot;: {
    &quot;billing_model&quot;: &quot;cpc&quot;,
    &quot;attribution_evidence&quot;: &quot;SYNTHETIC paid-click cohort; no live platform assertion&quot;,
    &quot;settlement_confirmed&quot;: false,
    &quot;row_unit&quot;: &quot;product&quot;
  }
}
</pre>
