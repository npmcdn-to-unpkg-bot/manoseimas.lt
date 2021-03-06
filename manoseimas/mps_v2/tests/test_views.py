# coding: utf-8

from __future__ import unicode_literals

from django.core import management

from django_webtest import WebTest

from manoseimas.scrapy.spiders.mps import MpsSpider
from manoseimas.scrapy.spiders.sittings import SittingsSpider
from manoseimas.scrapy.spiders.stenograms import StenogramSpider
from manoseimas.scrapy.pipelines import ManoseimasPipeline, ManoSeimasModelPersistPipeline
from manoseimas.scrapy.tests.utils import crawl


class TestViews(WebTest):

    maxDiff = None

    def test_mp_profile(self):
        crawl(
            Pipeline=ManoSeimasModelPersistPipeline, spider=MpsSpider(),
            param='p_asm_id', method='parse_person', path='mp_%s.html', urls=[
                'http://www3.lrs.lt/pls/inter/w5_show?p_r=6113&p_k=1&p_a=5&p_asm_id=53911&p_kade_id=6',
            ],
        )

        crawl(
            Pipeline=ManoseimasPipeline, spider=SittingsSpider(),
            param='p_svarst_kl_stad_id', method='parse_question', path='questions/%s.html', urls=[
                'http://www3.lrs.lt/pls/inter/w5_sale_new.klaus_stadija?p_svarst_kl_stad_id=-9209',
            ],
        )

        crawl(
            Pipeline=ManoseimasPipeline, spider=SittingsSpider(),
            param='p_bals_id', method='parse_person_votes', path='votings/%s.html', urls=[
                'http://www3.lrs.lt/pls/inter/w5_sale_new.bals?p_bals_id=-10765',
            ],
        )

        crawl(
            Pipeline=ManoSeimasModelPersistPipeline, spider=StenogramSpider(),
            param='p_id', method='parse_stenogram', path='stenogram_%s.html', urls=[
                'http://www3.lrs.lt/pls/inter2/dokpaieska.showdoc_l?p_id=395116',
            ],
        )

        management.call_command('recompute_stats', verbosity=0)

        self.app.get('/mp/parliamentarian/antanas-nedzinskas/')
