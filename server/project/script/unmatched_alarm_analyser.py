# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
import re
from collections import namedtuple

import arrow

from fta.storage import tables
from fta.storage.mysql import session
from fta.utils import logging
from fta.utils.decorator import redis_lock
from fta.utils.fta_collections import TransferTable
from project.hooks.match_alarm import persist_cached_archives

logger = logging.getLogger(__name__)


class ArchiveAnalyser(object):
    WORD_SPLIT_RE = re.compile(r"([A-Z]*[a-z]*)")
    FUNC_MAPPINGS = TransferTable()
    HANDLER_SCORE_THRESHOLD = 0.2
    HandlerScoreItem = namedtuple("HandlerScoreItem", ["handler", "score"])
    STOP_WORDS = {
        "zabbix", "open", "falcon", "openfalcon",
        "aws", "prometheus", "icinga", "nagios",
        "rest", "api", "custom", "mail", "email",
        "fta", "default", "qcloud", "blueking",
        "on", "off", "at",
    }
    SOLUTION_CODENAME_CPU_DEFAULT = "cpu_proc_top10"
    SOLUTION_CODENAME_MEM_DEFAULT = "mem_proc_top10"

    @FUNC_MAPPINGS.decorator_with_value({
        "cpu", "load", "cpuutilization",
    })
    def handle_cpu_default(self):
        solution = self.get_solution_by_codename(
            self.SOLUTION_CODENAME_CPU_DEFAULT,
        )
        if solution:
            return {
                "suggested": True,
                "alarm_def_description": u"分析进程占用CPU",
                "solution_id": solution.id,
            }

    @FUNC_MAPPINGS.decorator_with_value(set([
        "mem", "memory", "swap",
    ]))
    def handle_mem_default(self):
        solution = self.get_solution_by_codename(
            self.SOLUTION_CODENAME_MEM_DEFAULT,
        )
        if solution:
            return {
                "suggested": True,
                "alarm_def_description": u"分析进程占用内存",
                "solution_id": solution.id,
            }

    @classmethod
    def split_words(cls, key):
        return [i.lower() for i in cls.WORD_SPLIT_RE.findall(key) if i]

    def __init__(self, archive, score_threshold=None):
        self.score_threshold = score_threshold or self.HANDLER_SCORE_THRESHOLD
        self.archive = archive
        words = self.split_words(archive.alarm_type)
        self.word_spaces = set(words) - self.STOP_WORDS
        super(ArchiveAnalyser, self).__init__()

    def get_solution_by_codename(self, codename, cc_biz_id=0):
        solution = session.query(tables.FtaSolutionsAppSolution).filter_by(
            codename=codename,
            cc_biz_id=cc_biz_id,
        ).first()
        if not solution:
            logger.warning("solution not found: %s", codename)
        return solution

    def analysis(self):
        word_spaces = self.word_spaces
        if not word_spaces:
            return

        handler_list = self.detect_archive_handler(word_spaces)
        if not handler_list:
            return

        item = max(handler_list, key=lambda x: x.score)
        if item.score < self.score_threshold:
            return

        suggestion = item.handler(self)
        if not suggestion or not suggestion.pop("suggested", False):
            return

        archive_extra = json.loads(self.archive.extra)
        archive_extra.update(suggestion)
        self.archive.extra = json.dumps(archive_extra)
        now = arrow.now()
        session.query(tables.FtaSolutionsAppOutofscopearchive).filter(
            tables.FtaSolutionsAppOutofscopearchive.id == self.archive.id,
        ).update({
            "extra": self.archive.extra,
            "updated_on": now.naive,
            "status": "suggest",
        })
        return suggestion

    def get_ident_vector(self, word_spaces, dimensions):
        return [int(i in dimensions) for i in word_spaces]

    def get_dimensions_score(self, word_spaces, dimensions):
        # vector is only contains 1 or 0
        vector = self.get_ident_vector(word_spaces, dimensions)
        norm_a = sum(vector)
        norm_b = len(vector)

        if norm_a <= 0 or norm_b <= 0:
            return 0.0
        return norm_a / ((norm_a * norm_b) ** 0.5)

    def detect_archive_handler(self, word_spaces):
        score_list = []
        for handler, dimensions in self.FUNC_MAPPINGS.items():
            score = self.get_dimensions_score(word_spaces, dimensions)
            if score:
                score_list.append(self.HandlerScoreItem(handler, score))
        return score_list


@redis_lock("unmatched_alarm_analyser", 15 * 60)
def main():
    try:
        persist_cached_archives()
    except Exception as err:
        logger.exception("persist archives error: %s", err)

    one_week_ago = arrow.now().replace(days=-7).format("YYYY-MM-DD")
    archives = session.query(tables.FtaSolutionsAppOutofscopearchive).filter(
        tables.FtaSolutionsAppOutofscopearchive.status == "new",
        tables.FtaSolutionsAppOutofscopearchive.updated_on >= one_week_ago,
    )
    for archive in archives:
        try:
            analyser = ArchiveAnalyser(archive)
            suggestion = analyser.analysis()
            logger.info(
                "make suggestion for archive[%s] in biz[%s]: %s",
                archive.id, archive.cc_biz_id, suggestion,
            )
        except Exception as error:
            logger.exception("analysis archive error: %s", error)


if __name__ == '__main__':
    main()
