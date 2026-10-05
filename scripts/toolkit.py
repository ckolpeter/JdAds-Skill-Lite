#!/usr/bin/env python3
"""Offline retail-ad planning. Python 3.10+, standard library only.

No platform requests, credentials, live identifiers, or write authorization.
Money is computed with Decimal; output numbers are explicit decimal strings.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_DOWN, localcontext
from pathlib import Path
import china

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2_000_000
MAX_ARTIFACT_BYTES = 16_000_000
D = Decimal
SENSITIVE = re.compile(r'(token|secret|password|cookie|authorization|api.?key|account.?id|campaign.?id|customer.?id)', re.I)
SECRET_TEXT = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b')


class InputError(ValueError):
    """User-facing validation error; never echo input contents."""


def require(condition, message):
    if not condition:
        raise InputError(message)


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def reject_constant(_):
    raise InputError('Non-finite JSON number')


def read_json(path, max_bytes=MAX_BYTES):
    p = Path(path)
    require(p.is_file() and not p.is_symlink(), 'Expected regular JSON file, not symlink')
    require(p.stat().st_size <= max_bytes, 'JSON exceeds the configured byte limit')
    try:
        return json.loads(p.read_text(encoding='utf-8-sig'), object_pairs_hook=no_duplicates,
                          parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise InputError('Invalid UTF-8 JSON') from exc


def text_safety(value, depth=0):
    require(depth <= 24, 'Input nesting is too deep')
    if isinstance(value, dict):
        for key, item in value.items():
            require(not SENSITIVE.search(key), 'Credential or live-account field is forbidden')
            text_safety(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            text_safety(item, depth + 1)
    elif isinstance(value, str):
        require(not SECRET_TEXT.search(value), 'Credential-like content is forbidden')
        require(not any(0xD800 <= ord(c) <= 0xDFFF or (ord(c) < 32 and c not in '\n\t\r') for c in value),
                'Invalid control character')
    # This filter is defense-in-depth, not a PII detector or a sandbox.


def schema_check(value, spec, root=None, path='$'):
    """Validate the documented JSON Schema subset; internal refs only."""
    root = spec if root is None else root
    if '$ref' in spec:
        ref = spec['$ref']
        require(ref.startswith('#/'), 'External schema refs forbidden')
        resolved = root
        for part in ref[2:].split('/'):
            resolved = resolved[part]
        return schema_check(value, resolved, root, path)
    types = spec.get('type', [])
    types = [types] if isinstance(types, str) else types
    matches = {'null': value is None, 'boolean': type(value) is bool,
               'string': isinstance(value, str), 'integer': type(value) is int,
               'number': type(value) in (int, float), 'array': isinstance(value, list),
               'object': isinstance(value, dict)}
    require(not types or any(matches.get(t, False) for t in types), f'{path}: wrong type')
    if 'enum' in spec:
        require(any(type(value) is type(v) and value == v for v in spec['enum']), f'{path}: unsupported value')
    if value is None:
        return
    if isinstance(value, dict):
        props = spec.get('properties', {})
        require(set(spec.get('required', [])) <= value.keys(), f'{path}: missing required fields')
        if spec.get('additionalProperties') is False:
            require(set(value) <= set(props), f'{path}: unexpected field')
        for key, item in value.items():
            if key in props:
                schema_check(item, props[key], root, f'{path}.{key}')
    elif isinstance(value, list):
        require(len(value) >= spec.get('minItems', 0) and len(value) <= spec.get('maxItems', 10000), f'{path}: invalid list size')
        for i, item in enumerate(value):
            schema_check(item, spec.get('items', {}), root, f'{path}[{i}]')
    elif isinstance(value, str):
        require(spec.get('minLength', 0) <= len(value) <= spec.get('maxLength', 2000), f'{path}: invalid text length')
        if 'pattern' in spec:
            require(re.fullmatch(spec['pattern'], value) is not None, f'{path}: invalid format')
    elif type(value) in (int, float):
        num(value)
        require(value >= spec.get('minimum', -1e12) and value <= spec.get('maximum', 1e12), f'{path}: out of range')


def num(value, optional=False, fraction=False):
    if value is None and optional:
        return None
    require(type(value) in (str, int, float) and len(str(value)) <= 48, 'Expected finite numeric value')
    try:
        n = D(str(value))
    except InvalidOperation as exc:
        raise InputError('Invalid decimal') from exc
    require(n.is_finite() and 0 <= n <= D('1000000000000'), 'Number must be finite, nonnegative and <= 1e12')
    require(-6 <= n.as_tuple().exponent <= 12, 'Numeric precision/exponent outside supported range')
    if fraction:
        require(n <= 1, 'Rate must be a fraction from 0 to 1, not a percentage')
    return n


def fmt(value):
    if value is None:
        return None
    with localcontext() as context:
        context.prec = 48
        return format(value.quantize(D('0.000001')), 'f')


def ratio(a, b):
    return None if a is None or b is None or b == 0 else a / b


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def profile():
    return read_json(ROOT / 'profile.json')


def check_input(data, kind):
    text_safety(data)
    schema_check(data, read_json(ROOT / 'schemas' / (kind + '.schema.json')))
    cfg = profile()
    require(data['platform'] == cfg['platform'], 'Wrong platform for this Skill')
    require(data['market'].strip(), 'Marketplace site is required; do not infer it from language')
    if kind == 'brief':
        require(data['campaign']['mode'] in cfg['modes'], 'Mode not supported by this v1')
        num(data['campaign']['budget'], optional=True)
        num(data['campaign']['target_return'], optional=True)
        num(data['campaign']['ad_rate'], optional=True, fraction=True)
        if not (cfg['platform'] == 'ebay' and data['campaign']['mode'] == 'general'):
            require(data['campaign']['ad_rate'] is None, 'ad_rate is only supported for eBay General; leave it null')
        seen = set()
        for p in data['products']:
            require(p['sku'] not in seen, 'Duplicate local SKU')
            seen.add(p['sku'])
            for field in ('order_revenue', 'target_profit', 'fee_base_per_order'):
                num(p[field], optional=True)
            num(p['expected_cvr'], optional=True, fraction=True)
            for cost in p['order_costs'].values():
                num(cost, optional=True)
            if p['fee_base_per_order'] is not None:
                require(num(p['fee_base_per_order']) > 0, 'Fee base must be positive')
    else:
        from datetime import date
        try:
            require(date.fromisoformat(data['start_date']) <= date.fromisoformat(data['end_date']), 'Reversed report dates')
        except ValueError as exc:
            raise InputError('Invalid report dates') from exc
        seen = set()
        for row in data['rows']:
            require(row['sku'] not in seen, 'Duplicate SKU: combine disjoint rows explicitly before import')
            seen.add(row['sku'])
            for field in ('spend', 'revenue'):
                num(row[field], optional=True)
    china.check(data, kind, cfg, sys.modules[__name__])
    return cfg


def economics(p, mode, platform):
    revenue = num(p['order_revenue'], optional=True)
    costs = [num(v, optional=True) for v in p['order_costs'].values()]
    missing = ['order_revenue'] if revenue is None else []
    missing += ['order_costs.' + k for k, v in p['order_costs'].items() if v is None]
    if missing:
        return {'status': 'INSUFFICIENT_DATA', 'missing': missing}
    contribution = revenue - sum(costs)
    target = num(p['target_profit'], optional=True)
    allowance = None if target is None else contribution - target
    positive = contribution if contribution > 0 else None
    allowed = allowance if allowance is not None and allowance > 0 else None
    cvr = num(p['expected_cvr'], optional=True, fraction=True)
    result = {'status': 'SCENARIO_ONLY', 'non_ad_contribution_per_order': fmt(contribution),
              'break_even_cpa': fmt(positive), 'break_even_roas_on_net_revenue': fmt(ratio(revenue, positive)),
              'target_ad_allowance_per_order': fmt(allowance),
              'target_roas_on_net_revenue': fmt(ratio(revenue, allowed)),
              'economic_cpc_ceiling': fmt(allowed * cvr) if allowed is not None and cvr is not None else None}
    if platform == 'ebay' and mode == 'general':
        result['economic_cpc_ceiling'] = None
        base = num(p['fee_base_per_order'], optional=True)
        result['general_fee_base'] = fmt(base)
        result['break_even_ad_rate_fraction'] = fmt(min(D(1), positive / base)) if positive is not None and base else None
        result['target_ad_rate_ceiling_fraction'] = fmt(min(D(1), allowed / base)) if allowed is not None and base else None
    return result


def plan_result(data, cfg):
    campaign, mode = data['campaign'], data['campaign']['mode']
    products = []
    for p in data['products']:
        econ = economics(p, mode, cfg['platform'])
        blocked, missing = [], []
        checks = {'account_ready': campaign['account_ready'], 'feature_confirmed': campaign['feature_confirmed'],
                  'listing_ready': p['listing_ready'], 'advertising_eligible': p['advertising_eligible']}
        if cfg['platform'] == 'walmart':
            checks['buy_box'] = p['buy_box']
        if cfg['platform'] == 'tiktok_shop' and mode == 'live_gmv_max':
            checks['live_ready'] = data['assets']['live_ready']
        checks.update(china.checks(data, cfg))
        for key, value in checks.items():
            if value is False:
                blocked.append(key)
            elif value is None:
                missing.append(key)
        if p['stock'] == 0:
            blocked.append('out_of_stock')
        elif p['stock'] is None:
            missing.append('stock')
        if econ['status'] == 'INSUFFICIENT_DATA':
            missing.extend(econ['missing'])
        else:
            if D(econ['non_ad_contribution_per_order']) <= 0:
                blocked.append('nonpositive_contribution')
            if p['target_profit'] is None:
                missing.append('target_profit')
            elif D(econ['target_ad_allowance_per_order']) <= 0:
                blocked.append('no_ad_headroom_at_target_profit')
            if cfg['platform'] == 'ebay' and mode == 'general':
                rate = num(campaign['ad_rate'], optional=True, fraction=True)
                base = num(p['fee_base_per_order'], optional=True)
                if rate is None or base is None:
                    missing.append('ad_rate_or_fee_base')
                else:
                    fee = rate * base
                    econ['scenario_general_ad_fee'] = fmt(fee)
                    econ['contribution_after_general_ad_fee'] = fmt(D(econ['non_ad_contribution_per_order']) - fee)
                    if econ['target_ad_allowance_per_order'] is not None and fee > D(econ['target_ad_allowance_per_order']):
                        blocked.append('ad_fee_exceeds_target_allowance')
        state = 'BLOCKED' if blocked else 'NEEDS_INPUT' if missing else 'PILOT_CANDIDATE'
        products.append({'sku': p['sku'], 'title': p['title'], 'readiness': state, 'blocked_by': blocked,
                         'missing': missing, 'economics': econ,
                         'supplied_listing_terms': p['terms'], 'research_status': 'NO_SEARCH_VOLUME_OR_LIVE_KEYWORD_DATA'})
    budget = num(campaign['budget'], optional=True)
    candidates = [p['sku'] for p in products if p['readiness'] == 'PILOT_CANDIDATE']
    quantum = D(10) ** -data['money_decimals']
    if budget is not None:
        require(budget == budget.quantize(quantum), 'Budget precision exceeds money_decimals')
    equal = ((budget / len(candidates)).quantize(quantum, rounding=ROUND_DOWN)
             if budget is not None and candidates else None)
    assigned = equal * len(candidates) if equal is not None else D(0)
    notes = list(cfg['notes']) + [
        'All allocations are equal-split pilot accounting scenarios, not optimized bids or live budgets.',
        'Use net revenue and fully loaded non-ad costs from the same representative order. No platform fees are assumed.',
        'Reported gross GMV / spend is not directly comparable with a net-revenue break-even threshold.',
        'Capability confirmations are user assertions, not independently verified account eligibility.',
        'Review stock, attribution maturity, rights, site rules and changes before taking any manual action.']
    if cfg['platform'] == 'tiktok_shop' and data['assets']['rights_confirmed'] is not True:
        notes.append('CREATIVE_RIGHTS_UNCONFIRMED: do not use unlicensed creator or music assets; no minimum video count is assumed.')
    return {'platform_workflow': cfg['workflows'][mode], 'products': products,
            'budget': {'scope': cfg['budget_scope'][mode], 'total_cap': fmt(budget),
                       'allocated_total': fmt(assigned) if budget is not None else None,
                       'reserve': fmt(budget - assigned) if budget is not None else None,
                       'allocation': [{'sku': s, 'pilot_allowance': fmt(equal)} for s in candidates] if equal is not None else [],
                       'days': campaign['days'], 'daily_reference_not_live_budget': fmt(ratio(budget, D(campaign['days'])))} ,
            'requested_target_return': campaign['target_return'], 'target_return_validated_for_platform': False,
            'checklist': cfg['checklist'], 'notes': notes, 'source_refs': [s['id'] for s in cfg['sources']]}


def metrics(row, scope, campaign_mode, platform):
    i, c, o = (D(row[k]) if row[k] is not None else None for k in ('impressions', 'clicks', 'orders'))
    # Rows are validated before this function; internal totals may exceed the per-field input cap.
    spend, revenue = (D(str(row[k])) if row[k] is not None else None for k in ('spend', 'revenue'))
    general = platform == 'ebay' and campaign_mode == 'general'
    # General attribution on eBay may depend on a click by ANY buyer: no buyer CVR inference.
    click_order = scope == 'paid_click' and not (platform == 'ebay' and campaign_mode == 'general')
    paid = scope in ('paid_click', 'paid_mixed')
    ret = ratio(revenue, spend)
    return {'billing_model': 'CPS' if general else 'CPC',
            'ctr_fraction': fmt(ratio(c, i)), 'cpc': None if general else fmt(ratio(spend, c)),
            'effective_spend_per_click': fmt(ratio(spend, c)),
            'cpm': fmt(spend * 1000 / i) if spend is not None and i else None,
            'click_order_rate': fmt(ratio(o, c)) if click_order else None,
            'cost_per_reported_order': fmt(ratio(spend, o)),
            'reported_roas': fmt(ret) if paid else None,
            'reported_blended_return': fmt(ret) if scope == 'paid_and_organic' else None,
            'unclassified_return': fmt(ret) if scope == 'unknown' else None,
            'ad_cost_ratio_fraction': fmt(ratio(spend, revenue)), 'profit_or_incrementality_verified': False}


def report_result(data, cfg):
    mode = data['campaign_mode']
    require(mode in cfg['modes'], 'Report campaign mode not supported')
    if cfg['platform'] == 'tiktok_shop':
        require(data['sales_scope'] in ('paid_and_organic', 'unknown'), 'GMV Max cannot be labeled as paid-only in this v1')
    notes = ['Metrics are descriptive, not causal. No automatic scale, pause or bid changes.',
             'Do not sum overlapping attribution windows, product totals, campaign totals or halo sales.',
             'Zero denominators and missing measurements remain null; they are not zero performance.',
             'Revenue basis, refunds, currency and attribution must match before any profitability comparison.']
    if data['sales_scope'] == 'paid_and_organic':
        notes.append('BLENDED_ATTRIBUTION: paid and organic sales are mixed; ROI is not paid-ad ROAS or incremental lift.')
    if cfg['platform'] == 'ebay' and mode == 'general':
        notes.append('GENERAL_ATTRIBUTION: rules vary by listing site and date; an attributed sale need not be from the buyer who clicked.')
    rows = []
    for row in data['rows']:
        warnings = []
        if row['clicks'] is not None and row['impressions'] is not None and row['clicks'] > row['impressions']:
            warnings.append('CLICKS_EXCEED_IMPRESSIONS: check metric definitions')
        if row['spend'] is not None and num(row['spend']) > 0 and row['clicks'] == 0:
            warnings.append('SPEND_WITH_ZERO_CLICKS: review billing model and reporting window')
        complete = data['window_complete'] is True
        state = 'OBSERVATION_ONLY'
        if not complete or data['sales_scope'] == 'unknown' or any(row[k] is None for k in ('spend', 'orders', 'revenue')):
            state = 'INSUFFICIENT_DATA'
        elif row['orders'] == 0 and num(row['spend']) > 0:
            state = 'REVIEW_ZERO_ORDERS_NOT_AUTOMATIC_PAUSE'
        if warnings:
            state = 'REVIEW_DATA_QUALITY'
        rows.append({'sku': row['sku'], 'diagnosis': state, 'metrics': metrics(row, data['sales_scope'], mode, cfg['platform']),
                     'warnings': warnings})
    totals = None
    if data['rows_disjoint'] is True:
        summed = {'sku': 'local-total'}
        for key in ('impressions', 'clicks', 'orders', 'spend', 'revenue'):
            vals = [r[key] for r in data['rows']]
            summed[key] = None if any(v is None for v in vals) else (sum(vals) if key in ('impressions', 'clicks', 'orders') else fmt(sum(num(v) for v in vals)))
        totals = {'input_totals': summed, 'metrics': metrics(summed, data['sales_scope'], mode, cfg['platform'])}
    else:
        notes.append('TOTALS_WITHHELD: rows have not been confirmed disjoint.')
    return {'rows': rows, 'totals': totals, 'notes': notes,
            'revenue_basis': data['revenue_basis'], 'attribution_window': data['attribution_window'],
            'source_refs': [s['id'] for s in cfg['sources']]}


def build(data, kind):
    cfg = check_input(data, kind)
    with localcontext() as context:
        context.prec = 48
        if kind == 'brief':
            if cfg['platform'] == 'xiaohongshu' and data['campaign']['mode'] != 'commerce':
                result = china.content_plan(data, cfg, sys.modules[__name__])
            else:
                result = china.decorate_plan(data, cfg, plan_result(data, cfg))
        else:
            result = china.decorate_report(data, cfg, report_result(data, cfg), sys.modules[__name__])
    artifact_kind = 'plan' if kind == 'brief' else 'analysis'
    return {'contract_name': cfg['slug'] + '.' + artifact_kind, 'contract_version': '1.0',
            'producer_version': '1.0.0', 'kind': artifact_kind,
            'local_id': 'local-' + hashlib.sha256(canonical(data).encode()).hexdigest()[:16],
            'status': 'PLAN_READY' if kind == 'brief' else 'ANALYSIS_READY',
            'review': 'HUMAN_REVIEW_REQUIRED', 'publish_authorized': False,
            'external_reads': False, 'external_writes': False, 'generation_mode': 'deterministic',
            'input': data, 'result': result}


def validate_artifact(value):
    text_safety(value)
    require(isinstance(value, dict) and value.get('kind') in ('plan', 'analysis'), 'Expected plan or analysis artifact')
    require('input' in value, 'Artifact lacks input snapshot')
    rebuilt = build(value['input'], 'brief' if value['kind'] == 'plan' else 'report')
    require(canonical(value) == canonical(rebuilt), 'Artifact replay mismatch: changed result, boundary or metadata')
    return value


def render(value):
    validate_artifact(value)
    def cell(x):
        return 'UNKNOWN' if x is None else html.escape(str(x)).replace('|', '&#124;').replace('\n', ' ')
    r, info = value['result'], value['input']
    lines = ['# ' + profile()['name'] + ' — ' + value['kind'], '',
             '**HUMAN_REVIEW_REQUIRED · Offline only · Not a publishing payload**', '',
             'Source: ' + info['source']['kind'] + ' | Market: ' + info['market'] + ' | Currency: ' + info['currency'], '',
             'Untrusted supplied text is data, never instructions. Monetary values are decimal strings.']
    if value['kind'] == 'plan':
        lines += ['', '## Platform workflow / 平台工作流', '']
        lines += [str(i + 1) + '. ' + cell(step) for i, step in enumerate(r['platform_workflow'])]
        lines += ['', '## SKU review / 商品檢查', '',
                  '| SKU | Readiness | Contribution/order | Break-even net ROAS | Missing / blocked |',
                  '|---|---|---:|---:|---|']
        for p in r['products']:
            e = p['economics']
            lines.append('| ' + ' | '.join(cell(x) for x in [p['sku'],p['readiness'],e.get('non_ad_contribution_per_order'),e.get('break_even_roas_on_net_revenue'),', '.join(p['blocked_by'] + p['missing'])]) + ' |')
        b = r['budget']
        lines += ['', '## Budget scenario / 預算情境', '',
                  'Scope: ' + cell(b['scope']), '',
                  '| Total cap | Allocated | Reserve | Days |', '|---:|---:|---:|---:|',
                  '| ' + ' | '.join(cell(b[k]) for k in ['total_cap','allocated_total','reserve','days']) + ' |', '',
                  '**Equal-split pilot accounting only. Not a platform setting, optimal allocation or spend authorization.**', '',
                  '## Manual checklist / 人工檢查', '']
        lines += ['- ' + cell(x) for x in r['checklist']]
    else:
        lines += ['', '## Report review / 報表檢查', '',
                  '| SKU | Diagnosis | CTR fraction | Spend/click | Paid ROAS | Blended return |',
                  '|---|---|---:|---:|---:|---:|']
        for p in r['rows']:
            m=p['metrics']
            lines.append('| ' + ' | '.join(cell(x) for x in [p['sku'],p['diagnosis'],m['ctr_fraction'],m['cpc'],m['reported_roas'],m['reported_blended_return']]) + ' |')
        lines += ['', 'Revenue basis: ' + cell(r['revenue_basis']), '',
                  'Attribution window: ' + cell(r['attribution_window']), '',
                  'Totals: ' + ('WITHHELD — rows not confirmed disjoint' if r['totals'] is None else 'Calculated from user-confirmed disjoint rows; see details.')]
    if value['kind'] == 'analysis' and info.get('goal') != 'sales':
        lines += ['', '## Events / 客資與互動', '', '| Local ID | CPL | Qualified CPL | Cost / interaction event |', '|---|---:|---:|---:|']
        for row in r['rows']:
            m = row['metrics']
            lines.append('| ' + ' | '.join(cell(x) for x in [row['sku'], m['cost_per_lead'], m['cost_per_qualified_lead'], m['cost_per_interaction_event']]) + ' |')
    lines += ['', '## Interpretation limits / 解讀限制', '']
    lines += ['- ' + cell(x) for x in r['notes']]
    lines += ['', '## Detailed result / 完整結果', '', '<pre>',
              html.escape(json.dumps(r, ensure_ascii=False, indent=2, allow_nan=False)), '</pre>', '']
    return '\n'.join(lines)


def write_output(value, directory):
    out = Path(directory)
    require(not out.exists() and not out.is_symlink(), 'Output exists: use a new directory')
    require(not any(p.is_symlink() for p in [out.parent] + list(out.parents)), 'Symlink output paths are forbidden')
    md = render(value)
    out.mkdir(parents=True, exist_ok=False)
    (out / (value['kind'] + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (out / 'report.md').write_text(md, encoding='utf-8')
    return str(out)


def read_csv(path, meta):
    p = Path(path)
    require(p.is_file() and not p.is_symlink() and p.stat().st_size <= MAX_BYTES, 'Expected CSV file <= 2 MB')
    require(isinstance(meta, dict), 'CSV metadata must be a JSON object')
    require('rows' not in meta, 'CSV metadata must not contain rows')
    reader = csv.DictReader(io.StringIO(p.read_text(encoding='utf-8-sig')))
    fields = ['sku', 'impressions', 'clicks', 'orders', 'spend', 'revenue']
    extended = fields + ['leads', 'qualified_leads', 'interactions']
    require(reader.fieldnames in [fields, extended], 'CSV must use the documented six or nine-column header')
    fields = reader.fieldnames
    rows = []
    for r in reader:
        require(None not in r and all(v is not None for v in r.values()), 'Malformed CSV row')
        row = {'sku': r['sku']}
        for field in fields[1:]:
            v = r[field].strip()
            if not v:
                row[field] = None
            elif field in ('impressions', 'clicks', 'orders', 'leads', 'qualified_leads', 'interactions'):
                require(re.fullmatch(r'[0-9]{1,12}', v) is not None, 'CSV counts must be nonnegative integers')
                row[field] = int(v)
            else:
                num(v)
                row[field] = v
        rows.append(row)
    return dict(meta, rows=rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('plan', 'analyze'):
        p = sub.add_parser(command)
        p.add_argument('input')
        p.add_argument('--out-dir', required=True)
        if command == 'analyze':
            p.add_argument('--meta', help='Metadata JSON required for canonical CSV input')
    p = sub.add_parser('validate')
    p.add_argument('input')
    p = sub.add_parser('render')
    p.add_argument('input')
    args = parser.parse_args(argv)
    try:
        if args.command in ('validate', 'render'):
            value = validate_artifact(read_json(args.input, max_bytes=MAX_ARTIFACT_BYTES))
            print(render(value) if args.command == 'render' else 'VALID_ARTIFACT — human review still required')
        else:
            if args.command == 'analyze' and args.meta:
                data = read_csv(args.input, read_json(args.meta))
            else:
                data = read_json(args.input)
            value = build(data, 'brief' if args.command == 'plan' else 'report')
            print('OUTPUT_READY: ' + write_output(value, args.out_dir))
        return 0
    except (InputError, OSError, UnicodeError, csv.Error, InvalidOperation, RecursionError) as exc:
        print('INPUT_OR_OUTPUT_ERROR: ' + (str(exc) if isinstance(exc, InputError) else type(exc).__name__), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
