from unittest import TestCase
from workfrontapi_plus import Workfront
from wfconfig import WorkfrontConfig

class TestWorkfront(TestCase):

    api = Workfront(WorkfrontConfig.subdomain, 'preview', api_key=WorkfrontConfig.api_key, test_mode=False)

    def test_bulk(self):
        dummy_list = list(range(2000))
        res = self.api.bulk('TASK', dummy_list)

        a = 0

    def test_search(self):
        params = {'name': 'cra',
                  'name_Mod': 'cicontains'}
        res = self.api.search('TASK', params)
        a=0

########

    def test_login(self):
        # Test with a password
        self.api._request = lambda x, y, z: {'sessionID': 'test',
                                             'userID': 'craig@test.com',
                                             'other': [x, y, z]}
        res = self.api.login('craig@test.com', 'abc123')
        golden = {'other': ['/login', {'username': 'craig@test.com', 'password': 'abc123'}, 'GET'], 'userID': 'craig@test.com', 'sessionID': 'test'}
        self.assertEqual(res, golden)
        self.assertEqual(self.api.session_id, 'test')
        self.assertEqual(self.api.user_id, 'craig@test.com')
        # Test without a password
        self.api._request = lambda x, y, z: {'sessionID': 'test',
                                             'userID': y,
                                             'other': [x, y, z]}
        res = self.api.login('craig@test.com')
        golden = {'other': ['/login', {'username': 'craig@test.com'}, 'GET'], 'sessionID': 'test', 'userID': {'username': 'craig@test.com'}}
        self.assertEqual(res, golden)

    def test_logout(self):
        self.api._request = lambda x, y, z: {'other': [x, y, z]}
        self.api.logout()
        self.assertEqual(self.api.session_id, None)
        self.assertEqual(self.api.user_id, None)

    def test_get_list(self):
        self.api._request = lambda x, y, z: {'other': [x, y, z]}
        res = self.api.get_list('task', ['1', '2', '3', '4'], ['test', 'test2'])
        self.assertEqual(res, {'other': ['/task', {'ids': '1,2,3,4'}, ['test', 'test2']]})

    def test_get_list(self):
        self.api._request = lambda x, y, z: {'other': [x, y, z]}
        res = self.api.get_list('task', ['1', '2', '3', '4'], ['test', 'test2'])
        self.assertEqual(res, {'other': ['/task', {'ids': '1,2,3,4'}, ['test', 'test2']]})
