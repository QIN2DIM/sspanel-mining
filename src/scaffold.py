import random

from gevent import monkey

monkey.patch_all()
import os

from src.apis import (
    run_collector,
    run_classifier,
    load_classified_hosts,
    SSPanelStaffChecker,
)


class Scaffold:

    @staticmethod
    def mining(
            env: str = "development",
            silence: bool = True,
            power: int = 16,
            collector: bool = False,
            classifier: bool = False,
            source: str = "local",
            batch: int = 1,
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
            run_collector(env=env, silence=silence)

        if classifier:
            run_classifier(power=power, source=source, batch=batch)

    @staticmethod
    def _deep_mining(
            power: int = 16
    ):
        """
        [dev]
        运行 Checker 生成维度更多的标签数据集

        > Checker 能够生成相交于 Classifier 维度更多的标签，也即 Checker 需要运行于 Classifier 之后。
        > Checker 能够检查目标站点 `/tos` `/staff` 以及 `elements` 的健康状态，
            也即可通过 Checker 检查 SSPanel-Uim 站点是否缺失`staff footer` statement；

        Usage: python main.py deep_mining

        :param power: Checker 运行功率
        :return:
        """

        """
        TODO [√]启动参数调整
        -------------------
        """
        # 校准检查器运行功率
        power = power if isinstance(power, int) else max(os.cpu_count(), 4)
        power = os.cpu_count() * 2 if os.cpu_count() >= power else power

        """
        TODO [√]启动检查器
        -------------------
        发动一次超高并发数的检测行为。
        刷新运行缓存，并对采集到的链接进行清洗、分类、二级存储。
        """
        # 导入本地数据集并滤除状态异常的站点
        urls = load_classified_hosts(filter_=True)

        # 数据抽样
        urls = list({random.choice(urls) for _ in range(30)})

        # 实例化检查器
        sug = SSPanelStaffChecker(docker=urls, debug=False)

        # 数据增强，增加广度搜索模式下的并发量，提高并发效率
        sug.preload()

        # 运行实例
        sug.go(power=power)

        # 存储分类结果
        docker: list = sug.offload()
        for i in docker:
            print(i)
