from gevent import monkey

monkey.patch_all()
from typing import Optional

from apis.scaffold import (
    mining,
    install
)


class Scaffold:

    @staticmethod
    def install(cdn: Optional[bool] = None):
        """
        下载项目运行所需的配置。

        ## Basic Usage

        Usage: python main.py install
        _________________________________________________________________
        or: python main.py install --cdn       |使用CDN下载模型
        _________________________________________________________________

        ## Intro

        本指令不拉取 `requirements.txt`，需要手动操作。

        :return:
        """
        install.run(cdn=cdn)

    @staticmethod
    def mining(
            env: Optional[str] = "development",
            silence: Optional[bool] = True,
            power: Optional[int] = 16,
            collector: Optional[bool] = False,
            classifier: Optional[bool] = False,
            source: Optional[str] = "local",
            batch: Optional[int] = 1,
    ):
        """
        运行 Collector 以及 Classifier 采集并过滤基层数据

        Usage: python main.py mining --silence=False                           |显式启动，在 linux 中运行时无效
        or: python main.py mining --power=4                                 |指定分类器运行功率
        or: python main.py mining --classifier --source=local               |启动分类器，指定数据源为本地缓存
        or: python main.py mining --classifier --source=remote --batch=1    |启动分类器，指定远程数据源
        or: python main.py mining --collector                               |启动采集器

        GitHub Actions Production
        -------------------------
        python main.py mining --env=production --collector --classifier --source=local

        :param source: within [local remote] 指定数据源，仅对分类器生效
            - local：使用本地 Collector 采集的数据进行分类
            - remote：使用 SSPanel-Mining 母仓库数据进行分类（需要下载数据集）
        :param batch: batch 应是自然数，仅在 source==remote 时生效，用于指定拉取的数据范围。
            - batch=1 表示拉取昨天的数据（默认），batch=2 表示拉取昨天+前天的数据，以此类推往前堆叠
            - 显然，当设置的 batch 大于母仓库存储量时会自动调整运行了逻辑，防止溢出。
        :param env: within [development production]
        :param silence: 采集器是否静默启动，默认静默。
        :param power: 分类器运行功率。
        :param collector: 采集器开启权限，默认关闭。
        :param classifier: 分类器控制权限，默认关闭。
        :return:
        """
        if collector:
            mining.run_collector(env=env, silence=silence)

        if classifier:
            mining.run_classifier(power=power, source=source, batch=batch)
