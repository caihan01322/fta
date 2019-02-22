# Blueking Fault Auto-recovery（Community Version）

![](docs/resource/img/fta.png)
---
[![license](https://img.shields.io/badge/license-mit-brightgreen.svg?style=flat)](https://github.com/Tencent/bk-fta-solutions/blob/master/LICENSE)
[![Release Version](https://img.shields.io/badge/release-5.1.3-brightgreen.svg)](https://github.com/Tencent/bk-fta-solutions/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Tencent/bk-fta-solutions/pulls)

[(Chinese Documents Available)](README.md)


Blueking Fault Auto-recovery(FTA) is a solution of fault automatic processing that improves the service availability of the enterprise and reduces the manpower input of fault handling, and realizes the change of self-healing from "manual processing" to "unattended"!

FTA saves manpower by automating processing, and make the recovery process more reliable through a scheduled recovery process, and achieve faster fault location and recovery through parallel analysis.

Summarized in one sentence for FTA: real-time discovery of alarms, pre-diagnosis analysis, automatic recovery of faults, and opening of closed loops for the entire process.

## Overview

* [Architecture](docs/overview/architecture.md)
* [Code Directory](docs/overview/code_framework.md)
* [Features](docs/overview/advantage.md)
* [Solutions](docs/overview/Integrated/Many_Solutions.md)
* [Integrated Monitoring Products](docs/overview/Integrated/Integrated_Monitoring_Products.md)
* [Usecase](docs/overview/usecase.md)

## Features

* Alarm Products ：TFA integrates bk_monitor, Zabbix, OpenFalcon, Nagios, Icinga, AWS, email alarm access, and can pull and push alarms through REST API.
* Alarm Solutions：FTA supports to perform task on the third platform through API
* Alarm Convergence and Defense：FTA supports to converge multiple associated alarms to the event according to the predetermined convergence and defense rules.
* Combination Solutions：FTA supports user to combine different solutions according to a certain processe flow。
* Health Diagnosis：Based on the strategy of early warning FTA, trace back to the processed alarms at 8am every morning, and analyze the potential risks and handle them.
* Early Warning: the extention of health diagnosis, it will solve the problem that discovered by the health diagnosis 
* Operation Audit: Recording any operations of FTA to ensure the operational safety and problems can be traced back.
* Custom Solutions：FTA provides multiple built-in solutions, such as disk cleaning，notify，approvel by wechat etc.
* FTA Helper： It analyzes the relationship between alrams and solutions, and generate some recommended solutions. 

If you want to know the detail description of FTA, please read [Production Manual](http://docs.bk.tencent.com/product_white_paper/fta)

## Getting started

* [Download & Install](docs/install/installation.md)
* [Deploy](docs/install/source_compile.md)
* [Extention Of Alarm Source](docs/overview/Integrated/integrated_monitor_extension.md)
* [Extention Of Soulutions](docs/overview/Integrated/solution_extension.md)

## Version plan

* [Version Guidlines](docs/VERSION.md)

## Support

1. Refer to the FTA installation document[Installation Docs](docs/install/installation.md)
2. Read [source(in Chinese)](https://github.com/Tencent/bk-fta-solutions/tree/master)
3. Read the [wiki(in Chinese)](https://github.com/Tencent/bk-fta-solutions/wiki/)
4. Contact us, technical exchange QQ group:

<img src="docs/resource/img/bk_qq_group.png" width="250" hegiht="250" align=center />


## Contributing

For FTA branch management, issues, and pr specifications, read the [bk-fta-solutions Contributing Guide](docs/CONTRIBUTING.md)。

If you are interested in contributing, check out the [CONTRIBUTING.md], also join our [Tencent OpenSource Plan](https://opensource.tencent.com/contribution).

## FAQ

https://github.com/Tencent/bk-fta-solutions/wiki/FAQ

## License
FTA is based on the MIT protocol. Please refer to [LICENSE](LICENSE.txt) for details.
