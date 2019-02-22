# 故障自愈 发布部署

这里介绍下改动后的源码如何打包，以及如何在社区版环境下安装

# 1. web_app打包安装

## 1.1 修改版本号
源码修改后，请务必修改 `app.yml` 文件中 `version` 版本号。

## 1.2 打包
在源码根目录下执行以下命令 VERSION填入当前版本号
```bash
bash bin/build.sh web_app {VERSION}
```
> 注意，该脚本会把项目依赖的 python 包都下载到生成的版本包中，请务必保证把项目依赖的 python 包都加入到 requirements.txt 文件中。
> 打包完成后会在当前目录下生成一个名为 `bk_fta_solutions-当前时间串-{VERSION}.tar,gz` 格式的文件，即版本包。

## 1.3 上传版本并部署
前往你部署的蓝鲸社区版平台，在"开发者中心"点击"S-mart应用"，找到官方故障自愈应用并进入详情。在"上传版本"中，点击"上传文件"后选中上一步打包生成的版本包，等待上传完成。然后点击"发布部署"，你就可以在测试环境或者正式环境部署你最新的版本包了。



# 2 后台安装

## 2.1 打包 
在源码根目录下执行以下命令 VERSION填入当前版本号
```bash
bash bin/build.sh server {VERSION}
```
> 注意，该脚本会把项目依赖的 python 包都下载到生成的版本包中，请务必保证把项目依赖的 python 包都加入到 requirements.txt 文件中。
> 打包完成后会在当前目录下生成一个名为 `fta-当前时间串-{VERSION}.tar,gz` 格式的文件，即版本包。

## 2.2 上传 
将打好包上传到蓝鲸基础服务器的中控机上

## 2.3 停止原fta进程
```bash
cd /data/install/
./bkcec stop fta #停止原fta进程
./bkcec status fta  #查看状态是否为EXIT
  ```
  
## 2.4 备份
```bash
cd /data/src/
mv fta fta.bak
  ```
  
## 2.5 解压开源版fta包
```bash
tar xf fta_solutions-x.x.tar.gz  -C /data/src/
```

## 2.6 恢复support-files目录
```bash
cp -a /data/src/fta.bak/support-files   /data/src/fta/
```

## 2.7 开始更新
```bash
cd /data/install
./bkcec sync fta
./bkcec install fta 
./bkcec start fta
./bkcec status fta
```
