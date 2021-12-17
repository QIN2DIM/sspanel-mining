from gevent import monkey

monkey.patch_all()
import os
import sys
from datetime import datetime

from src.apis import (
    create_env,
    run_collector,
    load_sspanel_hosts,
    SSPanelHostsClassifier,
    output_cleaning_dataset,
    PATH_DATASET_TEMPLATE,
    data_cleaning
)
from src.config import (
    DIR_OUTPUT_STORE_CLASSIFIER,
    TIME_ZONE_CN,
    logger
)


def demo(env: str = "development", silence: bool = None):
    """
    运行案例

    Usage: python main.py --env=production 在 GitHub Actions 中构建生产环境
    or: python main.py --silence=False 显式启动，在 linux 中运行时无效
    :param silence:
    :param env: within [development production]
    :return:
    """

    """
    TODO [√]启动参数调整
    -------------------
    """
    # 参数处理
    silence = True if silence is None else silence

    # 补全模版文件名
    path_file_txt = PATH_DATASET_TEMPLATE.format(
        str(datetime.now(TIME_ZONE_CN)).split(" ")[0]
    )

    # 初始化运行环境
    need_to_build_collector = create_env(path_file_txt)

    """
    TODO [√]启动采集器
    -------------------
    当程序初次运行时需要启动一次采集器挖掘站点。
    缓存的数据长时间内有效，而采集过程较为耗时，故不必频繁启用。
    """
    # 确保定时任务下每日至少采集一次
    # 生产环境下每次运行程序都要启动采集器
    if need_to_build_collector or env == "production":
        # 实例化并运行采集器
        run_collector(path_file_txt, silence=silence)
        # Collector 使用 `a` 指针方式插入新数据，此处使用 data_cleaning() 去重
        data_cleaning(path_file_txt)

    """
    TODO [√]启动分类器
    -------------------
    发动一次超高并发数的检测行为。
    刷新运行缓存，并对采集到的链接进行清洗、分类、二级存储。
    """
    # 导入数据集，也即识别并读回 Collector 的输出
    urls = load_sspanel_hosts()

    # 数据清洗
    sug = SSPanelHostsClassifier(docker=urls)
    sug.go()

    """
    TODO [√]分类简述
    -------------------
    #   - 分类数据将以 .csv 文件形式存储在 `/database/staff_hosts/classifier` 中
    #   - 分为以下几种类型（存在较小误判概率）：
    #       - Normal：无验证站点
    #       - Google reCAPTCHA：Google reCAPTCHA 人机验证
    #       - GeeTest Validation：极验滑块验证（绝大多数）/选择文字验证（极小概率）
    #       - Email Validation：邮箱验证（开放域名）
    #       - SMS：手机短信验证 [钓鱼执法？]
    #       - CloudflareDefenseV2：站点正在被攻击 or 高防服务器阻断了爬虫流量
    #   - 存在以下几种限型实例：
    #       - 限制注册(邮箱)：要求使用指定域名的邮箱接收验证码
    #       - 限制注册(邀请)：要求必须使用有效邀请码注册
    #       - 请求异常(ERROR:STATUS_CODE)：请求异常，携带相应状态码
    #       - 拒绝注册：管理员关闭注册接口
    #       - 危险通信：HTTP 直连站点
    """
    # 存储分类结果
    docker = sug.offload()
    path_output = output_cleaning_dataset(
        dir_output=DIR_OUTPUT_STORE_CLASSIFIER,
        docker=docker,
    )

    # Windows 系统下自动打开洗好的导出文件
    if path_output:
        if "win" in sys.platform:
            os.startfile(path_output)
        logger.success("清洗完毕 - path={}".format(path_output))
    else:
        logger.error("数据异常 - docker={}".format(docker))
