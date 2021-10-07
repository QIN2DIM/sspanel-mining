import os
from os.path import dirname, join, exists, abspath
from sys import platform

from loguru import logger
import pytz
# ---------------------------------------------------
# TODO (√)CHROMEDRIVER_PATH -- ChromeDriver的路径
#  本项目依赖google-chrome驱动插件，请确保您的开发环境中已经安装chrome以及对应版本的chromedriver

# 1. 配置google-chrome开发环境
# 1.1 安装Chrome
# 若无特殊需求请直接拉取最近版程序
# >> Windows -> https://www.google.cn/chrome/index.html
# >> Linux -> https://shimo.im/docs/5bqnroJYDbU4rGqy/

# 1.2 安装chromedriver
# 查看chrome版本并安装对应版本的匹配操作系统的chromedriver。
# >> http://npm.taobao.org/mirrors/chromedriver/

# 1.3 配置环境变量
# （1）将下载好的对应版本的chromedriver放到工程`./sspanel-mining/src`目录下
# （2）或配置Chrome环境变量，Windows编辑系统环境变量Path，定位到Application文件夹为止，示例如下：
#      C:\Program Files\Google\Chrome\Application

# 2. 注意事项
#   -- 本项目基于Windows环境开发测试，Linux环境部署运行，若您的系统基于MacOS或其他，请根据报错提示微调启动参数。
#   -- 若您的Chrome安装路径与上文所述不一致，请适当调整。
#   -- 若您不知如何查看Chrome版本或在参考blog后仍遇到预料之外的问题请在issue中留言或通过检索解决。
#       >> Project：https://github.com/QIN2DIM/sspanel-mining
# ---------------------------------------------------
if "win" in platform:
    # 定位chromedriver根目录
    CHROMEDRIVER_PATH = "./chromedriver.exe"
    # 定位工程根目录 SERVER_DIR_PROJECT
    SERVER_DIR_PROJECT = dirname(__file__)
else:
    CHROMEDRIVER_PATH = dirname(__file__) + "/chromedriver"
    SERVER_DIR_PROJECT = abspath(".")

# 文件数据库 目录根
SERVER_DIR_DATABASE = join(SERVER_DIR_PROJECT, "database")

# 服务器日志文件路径
SERVER_DIR_DATABASE_LOG = join(SERVER_DIR_DATABASE, "logs")
logger.add(
    join(SERVER_DIR_DATABASE_LOG, "runtime.log"),
    level="DEBUG",
    rotation="1 day",
    retention="20 days",
    encoding="utf8",
)
logger.add(
    join(SERVER_DIR_DATABASE_LOG, "error.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
)

# 采集器默认并发数
DEFAULT_POWER = os.cpu_count()
# 若chromedriver不在CHROMEDRIVER_PATH指定的路径下 尝试从环境变量中查找路径
if not exists(CHROMEDRIVER_PATH):
    CHROMEDRIVER_PATH = "chromedriver"
# 时区
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")
TIME_ZONE_NY = pytz.timezone("America/New_York")