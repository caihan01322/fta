# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow
from jinja2 import Template

from fta import settings
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppKpicache, FtaSolutionsAppOutofscopearchive
from fta.utils import logging, send, split_list
from fta.utils.conf import get_fta_admin_list
from fta.utils.decorator import func_cache
from fta.utils.i18n import _
from fta.utils.people import get_biz_responsible
from project.utils import query_cc

logger = logging.getLogger('utils')

EXTRA_RECEIVER = get_fta_admin_list()


def mail(biz_advices_dict, advice_def_dict):
    logger.info('notify_advice: %s', biz_advices_dict.keys())

    for cc_biz_id, biz_advices in biz_advices_dict.iteritems():

        addl_biz_info = get_addl_biz_info(cc_biz_id)

        cc_biz_name = query_cc.get_app_name(cc_biz_id)

        title = _("[Auto-recovery Notification] Health Daily {} {} {} new risk point(s)").format(
            cc_biz_name, arrow.now().format(_("MM Month DD Day")), len(biz_advices))

        cur_year = arrow.now().format("YYYY")

        mail_content = render_advice_mail(
            cc_biz_id=cc_biz_id,
            cc_biz_name=cc_biz_name,
            biz_advices=biz_advices,
            advice_def_dict=advice_def_dict,
            cur_year=cur_year,
            app_url_prod=settings.APP_URL_PROD,
            addl_biz_info=addl_biz_info)

        if hasattr(settings, "VERIFIER"):
            receiver = settings.VERIFIER
        else:
            receiver = split_list(get_biz_responsible(cc_biz_id))

        send.mail(receiver, mail_content, title)


def get_addl_biz_info(cc_biz_id):
    return {'out_of_scope_7d': get_out_of_scope(str(cc_biz_id)), 'kpi_7d': get_kpi_dict().get(str(cc_biz_id))}


@func_cache()
def get_kpi_dict():
    kpis = session.query(FtaSolutionsAppKpicache).filter_by(kpi_type=7)
    return {
        str(k['cc_biz_id']): int(100 * k['tnm_success'] / k['tnm_total']) if k['tnm_total'] else 0
        for k in orm_2_dict(kpis)
    }


def get_out_of_scope(cc_biz_id):
    one_week_ago = arrow.utcnow().replace(days=-7).format("YYYY-MM-DD")
    attr_counts = orm_2_dict(
        session.query(FtaSolutionsAppOutofscopearchive)
        .filter(FtaSolutionsAppOutofscopearchive.cc_biz_id == cc_biz_id)
        .filter(FtaSolutionsAppOutofscopearchive.created_on >= one_week_ago)
        .group_by(FtaSolutionsAppOutofscopearchive.alarm_type)
        .order_by(FtaSolutionsAppOutofscopearchive.sub_count.desc())
    )
    for a in attr_counts:
        a['attr_name'] = '-'
        a['attr_id'] = '' if not a['attr_id'] else a['attr_id']

    return attr_counts


def render_advice_mail(**kwargs):
    with open('fta/advice/advice.html') as f:
        content = f.read()
    template = Template(content)
    return template.render(**kwargs)
