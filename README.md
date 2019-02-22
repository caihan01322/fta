# 蓝鲸智云故障自愈（社区版）

![](docs/resource/img/fta.png)
---
[![license](https://img.shields.io/badge/license-mit-brightgreen.svg?style=flat)](https://github.com/Tencent/bk-fta-solutions/blob/master/LICENSE)
[![Release Version](https://img.shields.io/badge/release-5.1.3-brightgreen.svg)](https://github.com/Tencent/bk-fta-solutions/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Tencent/bk-fta-solutions/pulls)

[(English Documents Available)](README_EN.md)


故障自愈是腾讯蓝鲸体系产品的一款SaaS应用，是行业优秀的"故障自动化处理"解决方案，故障自愈提升了企业的服务可用性和降低了故障处理的人力投入，实现了故障从"人工处理"到"无人值守"的变革!

一句话概括：故障自愈实现了实时发现告警、预诊断分析及自动恢复故障，并打通周边系统实现整个流程的闭环。

## Overview

* [架构设计](docs/overview/architecture.md)
* [代码目录](docs/overview/code_framework.md)
* [特点优势](docs/overview/advantage.md)
* [处理套餐](docs/overview/Integrated/Many_Solutions.md)
* [告警源接入](docs/overview/Integrated/Integrated_Monitoring_Products.md)
* [场景案例](docs/overview/usecase.md)

## Features

* 获取告警：告警源集成蓝鲸监控、4款主流开源监控产品Zabbix、OpenFalcon、Nagios、Icinga，及AWS、邮件的告警接入，更能通过REST API 拉取、推送告警
* 告警处理：故障处理支持作业平台、标准运维流程
* 告警收敛和防御：系统预定收敛和防御规则，对异常告警事件进行收敛，更能通过收敛审批功能对异常的执行做审批
* 支持组合套餐，把自定义自愈套餐通过FTA（故障树分析）处理流程，组装成解决复杂场景的组合套餐
* 健康诊断，根据系统内置的健康诊断策略，周期性回溯异常事件，并通过邮件方式推送出来
* 预警自愈，是健康诊断功能的延伸，把健康诊断发现的问题通过自愈方案解决，完成异常事件的闭环
* 操作审计，感知故障自愈的每一次改动，确保运营安全，问题可回溯
* 丰富的处理套餐：除支持作业平台、标准运维外，还支持快捷套餐类（磁盘清理、汇总、检测CPU使用率TOP10等）、组合套餐类（获取故障机备机、通知、审批等）
* 自愈小助手：分析告警和套餐关联，决策推荐自愈方案方案，降低配置成本

如果想了解以上功能的详细说明，请参考[产品说明](http://docs.bk.tencent.com/product_white_paper/fta)

## Getting started

* [下载安装](docs/install/installation.md)
* [发布部署](docs/install/source_compile.md)
* [告警源接入扩展开发](docs/overview/Integrated/integrated_monitor_extension.md)
* [自定义套餐扩展开发](docs/overview/Integrated/solution_extension.md)

## Version plan

* [版本迭代规则](docs/VERSION.md)

## Support

1. 参考安装文档 [安装文档](docs/install/installation.md)
2. 阅读 [源码](https://github.com/Tencent/bk-fta-solutions/tree/master)
3. 阅读 [wiki](https://github.com/Tencent/bk-fta-solutions/wiki/) 或者寻求帮助
4. 联系我们，技术交流QQ群：

<img src="docs/resource/img/bk_qq_group.png" width="250" hegiht="250" align=center />


## Contributing

关于  分支管理、issue 以及 pr 规范，请阅读 [bk-fta-solutions Contributing Guide](docs/CONTRIBUTING.md)。

[腾讯开源激励计划](https://opensource.tencent.com/contribution) 鼓励开发者的参与和贡献，期待你的加入。

## FAQ

[https://github.com/Tencent/bk-fta-solutions/wiki/FAQ](https://github.com/Tencent/bk-fta-solutions/wiki/FAQ)

## License

故障自愈 是基于 MIT 协议， 详细请参考 [LICENSE](LICENSE.txt) 。
