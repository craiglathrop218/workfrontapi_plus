from unittest import TestCase
from workfrontapi_plus import Workfront
from wfconfig import WorkfrontConfig

class TestWorkfront(TestCase):

    api = Workfront(WorkfrontConfig.subdomain, api_key=WorkfrontConfig.api_key, test_mode=True)

    def test_bulk(self):
        dummy_list = list(range(2000))
        res = self.api.bulk('TASK', dummy_list)

        a = 0

