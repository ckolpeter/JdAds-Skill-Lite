"""China marketplace extensions; no network and no live platform payloads.

Local mode labels are workflow categories, never API enums. The toolkit is
passed explicitly to keep Decimal, validation and artifact replay identical.
"""
from __future__ import annotations


def check(data, kind, cfg, h):
    h.require(data['market'] == 'CN' and data['currency'] == 'CNY',
              'v1 supports mainland China/CNY only; do not infer locale or convert currencies')
    if kind == 'brief':
        c = data['china_context']
        if cfg['platform'] == 'xiaohongshu' and data['campaign']['mode'] != 'commerce':
            h.require(data['campaign']['target_return'] is None, 'Non-commerce plans do not accept a revenue-return target')
        h.require(c['storefront'] in cfg['storefronts'], 'Storefront belongs to another Skill')
        h.require(all(p['buy_box'] is None and p['fee_base_per_order'] is None for p in data['products']),
                  'Legacy compatibility fields buy_box/fee_base_per_order must remain null')
        if c['lead_economics'] is not None:
            h.require(cfg['platform'] == 'xiaohongshu' and data['campaign']['mode'] == 'leads',
                      'Lead economics only applies to Xhs leads planning')
            for k, v in c['lead_economics'].items():
                h.num(v, optional=True, fraction=(k == 'close_rate'))
    else:
        h.require(data['goal'] in cfg['report_goals'], 'Goal is not supported by this Skill')
        h.require(data['campaign_mode'] in cfg['modes'], 'Unknown local report mode')
        if cfg['platform'] == 'xiaohongshu':
            allowed = {'commerce': ['sales'], 'leads': ['leads'],
                       'seeding': ['engagement'], 'search': ['traffic', 'leads', 'sales']}
            h.require(data['goal'] in allowed[data['campaign_mode']], 'Xhs goal/mode mismatch')
        h.require(data['sales_scope'] == 'unknown' or data['measurement']['attribution_evidence'].strip(),
                  'A non-unknown scope needs a supplied attribution-definition reference')
        for row in data['rows']:
            leads, qualified = row.get('leads'), row.get('qualified_leads')
            h.require(qualified is None or leads is None or qualified <= leads,
                      'Qualified leads must be a subset of leads in this canonical format')
        if data['goal'] != 'sales':
            h.require(all(r['revenue'] is None and r['orders'] is None for r in data['rows']),
                      'Non-sales reports keep orders and revenue null; do not invent lead revenue')


def checks(data, cfg):
    c, a, mode = data['china_context'], data['assets'], data['campaign']['mode']
    result = {'discount_refund_costs_confirmed': c['discount_refund_costs_confirmed'],
              'creative_rights': a['rights_confirmed'], 'creative_supply_ready': a['creative_supply_ready']}
    if mode == 'live':
        result['live_ready'] = a['live_ready']
    if mode == 'new_product':
        result['new_product_stage'] = None if c['stage'] == 'unknown' else c['stage'] == 'new'
    return result


def decorate_plan(data, cfg, result):
    c, mode = data['china_context'], data['campaign']['mode']
    result['planning_mode_is_api_enum'] = False
    result['storefront'] = c['storefront']
    result['stage_user_declared'] = c['stage']
    result['content_tasks'] = cfg['creative_tasks'][mode]
    result['notes'] += [
        'China modes are local workflow categories, not current backend/API settings or eligibility assertions.',
        'Coupon discounts and refunds already removed from order_revenue must not be deducted again in costs.',
        'Include creator commissions, returned-goods losses, fulfilment and service costs once in non-ad costs.',
        'Full-site or managed totals may include organic/halo sales. Use supplied export definitions, not a mode name.',
        'Reported ROI may mean revenue/spend, not profit ROI. No profitability or incrementality is certified.']
    if cfg['platform'] in ('douyin', 'kuaishou'):
        result['notes'].append('Live-room totals and product rows may overlap; never sum them without reconciliation.')
    if cfg['platform'] == 'pinduoduo':
        result['notes'].append('Low selling price is not sufficient: reconcile promotion discounts and actual settlement. Legacy manual keywords are not assumed available.')
    return result


def lead_economics(values, h):
    if values is None or any(v is None for v in values.values()):
        return {'status': 'INSUFFICIENT_DATA', 'break_even_cpl': None,
                'target_ad_allowance_per_lead': None}
    contribution = h.num(values['contribution_per_sale'])
    close_rate = h.num(values['close_rate'], fraction=True)
    handling = h.num(values['handling_cost_per_lead'])
    retained = h.num(values['target_profit_per_lead'])
    available = contribution * close_rate - handling
    return {'status': 'SCENARIO_ONLY',
            'break_even_cpl': h.fmt(available) if available > 0 else None,
            'target_ad_allowance_per_lead': h.fmt(available - retained),
            'assumed_close_rate_fraction': h.fmt(close_rate),
            'warning': 'Expected-value scenario, not realized sales or guaranteed lead value.'}


def content_plan(data, cfg, h):
    """Non-commerce Xhs content planning deliberately has no SKU ROAS ranking."""
    mode, c, a = data['campaign']['mode'], data['china_context'], data['assets']
    checks_ = {'account_ready': data['campaign']['account_ready'],
               'feature_confirmed': data['campaign']['feature_confirmed'],
               'creative_rights': a['rights_confirmed'], 'creative_supply_ready': a['creative_supply_ready']}
    if mode == 'leads':
        checks_.update(lead_followup_ready=a['lead_followup_ready'], consent_process_ready=a['consent_process_ready'])
    rows = []
    for p in data['products']:
        conditions = dict(checks_, advertising_eligible=p['advertising_eligible'], content_ready=p['listing_ready'])
        blocked = [k for k,v in conditions.items() if v is False]
        missing = [k for k,v in conditions.items() if v is None]
        rows.append({'sku': p['sku'], 'title': p['title'],
                     'readiness': 'BLOCKED' if blocked else 'NEEDS_INPUT' if missing else 'PILOT_CANDIDATE',
                     'blocked_by': blocked, 'missing': missing,
                     'economics': {'status': 'NOT_APPLICABLE_TO_CONTENT_GOAL'},
                     'supplied_listing_terms': p['terms'],
                     'research_status': 'USER_SUPPLIED_TOPICS_NOT_LIVE_SEARCH_DATA'})
    budget = h.num(data['campaign']['budget'], optional=True)
    if budget is not None:
        h.require(budget == budget.quantize(h.D(10) ** -data['money_decimals']), 'Budget precision exceeds money_decimals')
    result = {'platform_workflow': cfg['workflows'][mode], 'products': rows,
              'budget': {'scope': 'content_campaign_scenario_not_live_settings', 'total_cap': h.fmt(budget),
                         'allocated_total': h.fmt(h.D(0)) if budget is not None else None,
                         'reserve': h.fmt(budget), 'allocation': [], 'days': data['campaign']['days'],
                         'daily_reference_not_live_budget': h.fmt(h.ratio(budget,h.D(data['campaign']['days'])))},
              'requested_target_return': None, 'target_return_validated_for_platform': False,
              'checklist': cfg['checklist'], 'notes': list(cfg['notes']) + [
                  'Content drafts are note hypotheses, not testimonials, keyword search volumes or targeting options.',
                  'Budget is deliberately unallocated; this content goal has no evidence for SKU profit allocation.',
                  'Leads and interactions are not orders. Stock and order-margin fields are not used for content readiness.',
                  'No personal contact details are collected. Only aggregated counts and local note identifiers are accepted.'],
              'source_refs': [s['id'] for s in cfg['sources']]}
    if mode == 'leads':
        result['lead_economics'] = lead_economics(c['lead_economics'], h)
    return decorate_plan(data, cfg, result)


def decorate_report(data, cfg, result, h):
    goal, measurement = data['goal'], data['measurement']
    def extra_metrics(raw, m):
        def count(key):
            v = raw.get(key)
            return None if v is None else h.D(v)
        spend = None if raw['spend'] is None else h.D(str(raw['spend']))
        leads, qualified, interactions = count('leads'), count('qualified_leads'), count('interactions')
        m['billing_model'] = measurement['billing_model']
        m['cpc'] = m['effective_spend_per_click'] if measurement['billing_model'] == 'cpc' else None
        m.update(cost_per_lead=h.fmt(h.ratio(spend, leads)),
                 cost_per_qualified_lead=h.fmt(h.ratio(spend, qualified)),
                 lead_qualification_rate=h.fmt(h.ratio(qualified, leads)),
                 cost_per_interaction_event=h.fmt(h.ratio(spend, interactions)),
                 interaction_events_per_impression=h.fmt(h.ratio(interactions, count('impressions'))))
        if goal != 'sales':
            for k in ['reported_roas','reported_blended_return','unclassified_return',
                      'cost_per_reported_order','click_order_rate','ad_cost_ratio_fraction']:
                m[k] = None
        return m
    for raw, out in zip(data['rows'], result['rows']):
        extra_metrics(raw, out['metrics'])
        for f in ['leads','qualified_leads','interactions']:
            out[f] = raw.get(f)
        if goal != 'sales':
            event = 'leads' if goal == 'leads' else 'interactions' if goal == 'engagement' else 'clicks'
            out['diagnosis'] = ('INSUFFICIENT_DATA' if data['window_complete'] is not True or raw.get(event) is None
                                or raw['spend'] is None or data['sales_scope'] == 'unknown'
                                else 'REVIEW_ZERO_EVENTS_NOT_AUTOMATIC_PAUSE' if raw[event] == 0 and h.num(raw['spend']) > 0
                                else 'OBSERVATION_ONLY')
        if out['warnings']:
            out['diagnosis'] = 'REVIEW_DATA_QUALITY'
    if result['totals'] is not None:
        summed = result['totals']['input_totals']
        for field in ['leads','qualified_leads','interactions']:
            values = [r.get(field) for r in data['rows']]
            summed[field] = None if any(v is None for v in values) else sum(values)
        extra_metrics(summed, result['totals']['metrics'])
    result['goal'] = goal
    result['measurement'] = measurement
    result['notes'] += [
        'Billing model is a user-supplied classification. Spend/click does not prove CPC billing.',
        'Rows require the same period, goal, currency, attribution definition and aggregation level.',
        'Interactions are event counts, not unique people or conversions. Multiple events per impression are possible.',
        'Leads, qualified leads and orders are distinct; no customer identity is requested.',
        'Gross GMV/spend is never certified as net profit ROI; no automatic scale/pause decision is produced.']
    if measurement['settlement_confirmed'] is not True:
        result['notes'].append('SETTLEMENT_UNCONFIRMED: reconcile refunds/commissions/settlement before margin comparisons.')
    return result
