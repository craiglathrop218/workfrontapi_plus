from unittest import TestCase
from workfrontapi_plus import Workfront

from wfconfig import WorkfrontConfig

import hashlib, json, requests
from nose.tools import assert_true


'''https://realpython.com/blog/python/testing-third-party-apis-with-mocks/'''

class TestWorkfrontE2E(TestCase):

    api = Workfront(WorkfrontConfig.subdomain, 'preview', api_key=WorkfrontConfig.api_key, test_mode=True)

########  LIVE E2E TESTS #############

    def e2e_controller(self):
        # Make a project

        # Make a bunch of tasks 
        pass

    def test_live_search(self):
        self.api._request = self.api._make_request
        res = self.api.search('task', {'name': 'cra', 'name_Mod': 'cicontains'}, ['name'])
        print(res[0])
        assert_true(isinstance(res, list))

    def test_make_error(self):
        self.api._request = self.api._make_request
        with self.assertRaises(Exception) as context:
            res = self.api.search('task', {'namea': 'cra', 'name_Mod': 'cicontains'}, ['name'])


