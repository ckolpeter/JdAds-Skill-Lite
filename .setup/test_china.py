"""China-specific and event-goal regressions. No live platform requests."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import toolkit as t
import china

class ChinaTests(unittest.TestCase):
    def setUp(self):
        self.b=t.read_json(ROOT/'examples/brief.synthetic.json')
        self.r=t.read_json(ROOT/'examples/report.synthetic.json')
        self.cfg=t.profile()
    def plan(self):return t.build(self.b,'brief')['result']
    def report(self):return t.build(self.r,'report')['result']
    def reject(self,value,kind):
        with self.assertRaises(t.InputError):t.build(value,kind)
    def test_cn_scope(self):
        for market,currency in [('TW','TWD'),('SG','CNY'),('CN','USD')]:
            b=copy.deepcopy(self.b);b.update(market=market,currency=currency);self.reject(b,'brief')
    def test_foreign_report(self):self.r['market']='US';self.reject(self.r,'report')
    def test_wrong_storefront(self):self.b['china_context']['storefront']='other';self.reject(self.b,'brief')
    def test_context_required(self):del self.b['china_context'];self.reject(self.b,'brief')
    def test_unknown_discount_refund_withholds(self):
        self.b['china_context']['discount_refund_costs_confirmed']=None
        self.assertEqual(self.plan()['budget']['allocation'],[])
    def test_false_discount_refund_blocks(self):
        self.b['china_context']['discount_refund_costs_confirmed']=False
        self.assertEqual(self.plan()['products'][0]['readiness'],'BLOCKED')
    def test_rights_unknown(self):
        self.b['assets']['rights_confirmed']=None
        self.assertIn('creative_rights',self.plan()['products'][0]['missing'])
    def test_rights_false(self):
        self.b['assets']['rights_confirmed']=False
        self.assertEqual(self.plan()['products'][0]['readiness'],'BLOCKED')
    def test_creative_supply_unknown(self):
        self.b['assets']['creative_supply_ready']=None
        self.assertEqual(self.plan()['budget']['allocation'],[])
    def test_buybox_not_used(self):self.b['products'][0]['buy_box']=True;self.reject(self.b,'brief')
    def test_ebay_fee_not_used(self):self.b['products'][0]['fee_base_per_order']='10';self.reject(self.b,'brief')
    def test_no_live_enums(self):self.assertFalse(self.plan()['planning_mode_is_api_enum'])
    def test_all_modes_have_workflow(self):
        for m in self.cfg['modes']:
            self.b['campaign']['mode']=m
            self.assertEqual(self.plan()['platform_workflow'],self.cfg['workflows'][m])
            self.assertGreater(len(self.plan()['content_tasks']),0)
    def test_missing_billing_definition(self):del self.r['measurement'];self.reject(self.r,'report')
    def test_unknown_billing_not_inferred(self):
        self.r['measurement']['billing_model']='unknown';m=self.report()['rows'][0]['metrics']
        self.assertIsNone(m['cpc']);self.assertEqual(m['effective_spend_per_click'],'2.000000')
    def test_ocpm_not_cpc(self):
        self.r['measurement']['billing_model']='ocpm'
        self.assertIsNone(self.report()['rows'][0]['metrics']['cpc'])
    def test_scope_needs_evidence(self):self.r['measurement']['attribution_evidence']='';self.reject(self.r,'report')
    def test_unknown_scope_permitted(self):
        self.r['sales_scope']='unknown';self.r['measurement']['attribution_evidence']=''
        self.assertIsNone(self.report()['rows'][0]['metrics']['reported_roas'])
    def test_settlement_unconfirmed(self):self.assertTrue(any('SETTLEMENT_UNCONFIRMED' in x for x in self.report()['notes']))
    def test_settlement_confirmed_not_profit_claim(self):
        self.r['measurement']['settlement_confirmed']=True
        self.assertFalse(self.report()['rows'][0]['metrics']['profit_or_incrementality_verified'])
    def test_qualified_subset(self):
        self.r['rows'][0].update(leads=1,qualified_leads=2);self.reject(self.r,'report')
    def test_negative_leads(self):self.r['rows'][0]['leads']=-1;self.reject(self.r,'report')
    def test_boolean_leads(self):self.r['rows'][0]['leads']=True;self.reject(self.r,'report')
    def test_extended_counts_and_totals(self):
        for row in self.r['rows']:row.update(leads=10,qualified_leads=5,interactions=100)
        r=self.report();self.assertEqual(r['totals']['input_totals']['leads'],20)
        self.assertEqual(r['rows'][0]['metrics']['cost_per_lead'],'10.000000')
        self.assertEqual(r['rows'][0]['metrics']['lead_qualification_rate'],'0.500000')
    def test_missing_extended_not_zero(self):
        self.r['rows'][0]['leads']=10
        self.assertIsNone(self.report()['totals']['input_totals']['leads'])
    def test_zero_leads_null(self):
        self.r['rows'][0].update(leads=0,qualified_leads=0,interactions=0)
        m=self.report()['rows'][0]['metrics'];self.assertIsNone(m['cost_per_lead']);self.assertIsNone(m['cost_per_interaction_event'])
    def test_event_rate_not_unique_person_rate(self):
        self.r['rows'][0]['interactions']=2000
        self.assertEqual(self.report()['rows'][0]['metrics']['interaction_events_per_impression'],'2.000000')
    def test_extended_csv(self):
        meta=copy.deepcopy(self.r);del meta['rows']
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv';p.write_text('sku,impressions,clicks,orders,spend,revenue,leads,qualified_leads,interactions\nx,1000,50,5,100,500,10,5,30\n',encoding='utf-8')
            result=t.build(t.read_csv(p,meta),'report')['result']
            self.assertEqual(result['rows'][0]['metrics']['cost_per_qualified_lead'],'20.000000')
    def test_lead_math(self):
        e=china.lead_economics({'contribution_per_sale':'200','close_rate':'0.1','handling_cost_per_lead':'2','target_profit_per_lead':'3'},t)
        self.assertEqual(e['break_even_cpl'],'18.000000');self.assertEqual(e['target_ad_allowance_per_lead'],'15.000000')
    def test_missing_lead_math(self):self.assertEqual(china.lead_economics(None,t)['status'],'INSUFFICIENT_DATA')
    def test_zero_lead_headroom(self):
        e=china.lead_economics({'contribution_per_sale':'10','close_rate':'0','handling_cost_per_lead':'2','target_profit_per_lead':'0'},t)
        self.assertIsNone(e['break_even_cpl'])
    def test_non_xhs_lead_values_rejected(self):
        self.b['china_context']['lead_economics']={'contribution_per_sale':'200','close_rate':'0.1','handling_cost_per_lead':'2','target_profit_per_lead':'3'}
        self.reject(self.b,'brief')
    def test_live_guard_or_new_stage(self):
        if 'live' in self.cfg['modes']:
            self.b['campaign']['mode']='live';self.b['assets']['live_ready']=None
            self.assertIn('live_ready',self.plan()['products'][0]['missing'])
        elif 'new_product' in self.cfg['modes']:
            self.b['campaign']['mode']='new_product';self.b['china_context']['stage']='mature'
            self.assertIn('new_product_stage',self.plan()['products'][0]['blocked_by'])
        else:
            self.b['campaign']['feature_confirmed']=None
            self.assertEqual(self.plan()['budget']['allocation'],[])
    def test_tao_storefronts_or_foreign_scope(self):
        if self.cfg['platform']=='taobao_tmall':
            for storefront in ['taobao','tmall']:
                self.b['china_context']['storefront']=storefront;self.assertEqual(self.plan()['storefront'],storefront)
        else:
            self.b['china_context']['storefront']='taobao';self.reject(self.b,'brief')
    def test_snapshot_source_status(self):
        self.assertTrue(all(s['verification'] in ['scope_verified','portal_only','blocked_403','fetch_failed'] for s in self.cfg['sources']))
    def test_docs_do_not_claim_real_account_tests(self):
        self.assertIn('NOT_RUN', (ROOT/'docs/TEST_REPORT.md').read_text())

class XhsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if t.profile()['platform']!='xiaohongshu':raise unittest.SkipTest('Xhs-only content behavior')
    def setUp(self):
        self.b=t.read_json(ROOT/'examples/content.brief.json');self.r=t.read_json(ROOT/'examples/content.report.json')
    def test_content_no_econ_ranking(self):
        a=t.build(self.b,'brief');self.assertEqual(a['result']['budget']['allocation'],[])
        self.assertEqual(a['result']['products'][0]['economics']['status'],'NOT_APPLICABLE_TO_CONTENT_GOAL');t.validate_artifact(a)
    def test_stock_not_content_criterion(self):
        self.b['products'][0]['stock']=0
        self.assertEqual(t.build(self.b,'brief')['result']['products'][0]['readiness'],'PILOT_CANDIDATE')
    def test_followup_required(self):
        self.b['assets']['lead_followup_ready']=None
        self.assertIn('lead_followup_ready',t.build(self.b,'brief')['result']['products'][0]['missing'])
    def test_consent_required(self):
        self.b['assets']['consent_process_ready']=False
        self.assertEqual(t.build(self.b,'brief')['result']['products'][0]['readiness'],'BLOCKED')
    def test_no_fake_roas(self):
        a=t.build(self.r,'report');m=a['result']['rows'][0]['metrics']
        self.assertIsNone(m['reported_roas']);self.assertEqual(m['cost_per_lead'],'10.000000')
        self.assertEqual(a['result']['rows'][0]['diagnosis'],'OBSERVATION_ONLY');t.validate_artifact(a)
    def test_non_sales_revenue_rejected(self):
        self.r['rows'][0]['revenue']='0'
        with self.assertRaises(t.InputError):t.build(self.r,'report')
    def test_mode_goal_mismatch(self):
        self.r['campaign_mode']='commerce'
        with self.assertRaises(t.InputError):t.build(self.r,'report')
    def test_missing_leads(self):
        del self.r['rows'][0]['leads']
        self.assertEqual(t.build(self.r,'report')['result']['rows'][0]['diagnosis'],'INSUFFICIENT_DATA')
    def test_zero_leads_not_pause(self):
        self.assertEqual(t.build(self.r,'report')['result']['rows'][1]['diagnosis'],'REVIEW_ZERO_EVENTS_NOT_AUTOMATIC_PAUSE')
    def test_seeding_goal(self):
        self.r.update(campaign_mode='seeding',goal='engagement')
        m=t.build(self.r,'report')['result']['rows'][0]['metrics']
        self.assertEqual(m['cost_per_interaction_event'],'3.333333');self.assertIsNone(m['reported_roas'])
    def test_traffic_search(self):
        self.r.update(campaign_mode='search',goal='traffic')
        self.assertEqual(t.build(self.r,'report')['result']['rows'][0]['diagnosis'],'OBSERVATION_ONLY')
    def test_lead_value_is_scenario(self):
        e=t.build(self.b,'brief')['result']['lead_economics']
        self.assertEqual(e['status'],'SCENARIO_ONLY');self.assertEqual(e['break_even_cpl'],'18.000000')
    def test_close_rate_percent_rejected(self):
        self.b['china_context']['lead_economics']['close_rate']='10'
        with self.assertRaises(t.InputError):t.build(self.b,'brief')
    def test_content_render(self):
        self.assertIn('NOT_APPLICABLE_TO_CONTENT_GOAL', t.render(t.build(self.b,'brief')))

def load_tests(loader, tests, pattern):
    suite=loader.loadTestsFromTestCase(ChinaTests)
    if t.profile()['platform']=='xiaohongshu':
        suite.addTests(loader.loadTestsFromTestCase(XhsTests))
    return suite

if __name__=='__main__':unittest.main()
