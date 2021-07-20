from src.apis import staff_api
from src.config import DEFAULT_POWER


def demo():
    # 判断是否是初次运行
    use_collector = staff_api.is_first_run()

    # 开启采集器
    classify_dir, staff_info = staff_api.go(
        # debug：执行模式 仅影响日志输出形式 不影响行为
        debug=False,

        # silence：Selenium启动模式。True：静默启动（默认）False：显式启动
        silence=True,

        # power：采集器功率。用于配置gevent协程架构的并发数。
        power=DEFAULT_POWER * 2,

        # identity_recaptcha：是否嵌入reCAPTCHA人机验证。
        #   - True：开启验证模式。采集器行为结束后，对未设geetest的站点进行一次iframe扫描（耗时较大）。
        #   - False：关闭验证模式（默认）。
        identity_recaptcha=False,

        # use_collector：是否启动采集器。
        #   - True：开启采集器。当程序初次运行时需要启动一次采集器挖掘站点，
        #           采集到的数据长时间内有效，而采集过程较为耗时，故不必重复使用。
        #   - False：关闭采集器。
        use_collector=use_collector,

        # use_checker：是否使用检查器（分类器）。
        #   - True：开启检查器（默认）。发动一次超高并发数的爬虫行为。
        #           刷新运行缓存，并对采集到的链接进行清洗、分类，是模块的核心功能，请务必开启。
        #   - False：关闭检查器。
        # description：
        #   - 分类数据将以.txt文件形式存储在/database/staff_hosts/classifier中
        #   - 当前版本的分类较为粗糙，主要分为以下几种类型（存在误判概率）：
        #       - staff_arch_general：常规arch站点，不采用验证注册
        #       - staff_arch_reCAPTCHA：使用Google-reCAPTCHA人机验证
        #       - staff_arch_slider：使用geetest滑块验证
        #       - verity_email：使用邮箱验证
        #       - verity_sms：使用（真实）手机短信验证 [???]
        #       - other_arch：其他非arch站点（依然基于sspanel但高度diy或魔改）
        use_checker=True,

        # use_generator：是否使用生成器。
        #   - True：开启生成器。根据站点特性，生成能自适应目标网站特性的
        #           集自动化注册、订阅获取、订阅池维护分发为一体的高性能爬虫代码。
        #   - False：关闭生成器（默认）。
        # [注意] 该功能因侵略性较强，待测试稳定后再开放使用。
        use_generator=False,
    )
    # 链接去重
    staff_api.refresh_cache(mode='de-dup')
    # 预览缓存数据
    print(f"\n\nSTAFF INFO\n{'_' * 32}")
    for element in staff_info.items():
        for i, tag in enumerate(element[-1]):
            print(f">>> [{i + 1}/{len(element[-1])}]{element[0]}: {tag}")
    print(f">>> 文件导出目录: {classify_dir}")
