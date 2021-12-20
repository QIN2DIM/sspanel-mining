from gevent import monkey

monkey.patch_all()
import unittest

from src.apis import (
    load_sspanel_hosts_remote,
    SSPanelHostsClassifier
)


class SpawnUnitTest(unittest.TestCase):

    def test_classifier(self):
        # 获取母仓库历史1天的缓存数据
        urls = load_sspanel_hosts_remote(batch=1)

        # 性能测试
        sug = SSPanelHostsClassifier(docker=urls)
        sug.go(power=16)

        # 缓存卸载
        self.assertNotEqual([], sug.offload())


if __name__ == "__main__":
    unittest.main()
