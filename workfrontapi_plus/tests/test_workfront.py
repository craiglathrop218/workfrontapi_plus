from unittest import TestCase
from workfrontapi_plus import Workfront
from wfconfig import WorkfrontConfig

class TestWorkfront(TestCase):

    api = Workfront(WorkfrontConfig.subdomain, 'sb01', api_key=WorkfrontConfig.api_key, test_mode=False)

    def test_bulk(self):
        dummy_list = list(range(2000))
        res = self.api.bulk('TASK', dummy_list)

        a = 0

    def test_search(self):
        params = {'name': 'cra',
                  'name_Mod': 'cicontains'}
        res = self.api.search('TASK', params)
        a=0

