"""
Copyright 2017, Integrated Device Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Authors: Roshan Bal, Craig Lathrop
"""

from unittest import TestCase
from workfrontapi_plus import Api

from wfconfig import WorkfrontConfig

import hashlib, json, requests
from nose.tools import assert_true

'''https://realpython.com/blog/python/testing-third-party-apis-with-mocks/'''


class TestWorkfront(TestCase):
    api = Api(WorkfrontConfig.subdomain, 'preview', api_key=WorkfrontConfig.api_key, test_mode=True)

    ######## UTILITY METHODS ##########
    @staticmethod
    def hash_dict(some_dict, make_list=False):
        dict_string = json.dumps(some_dict, sort_keys=True)
        dict_string = dict_string.encode('ascii', 'ignore')
        res = hashlib.sha1(dict_string).hexdigest()
        return [res] if make_list else res

    @staticmethod
    def api_response(data, dest):
        params_dict = {}
        data = str(data)
        data_list = data.split("&")
        for item in data_list:
            key_value_split = item.split("=")
            # str() because some stuff is byte vale b"..."
            params_dict[str(key_value_split[0])] = str(key_value_split[1])

        params_dict['path'] = dest

        json_out = json.dumps(params_dict)

        return json_out

        # @staticmethod
        # def test_api():
        #     res = requests.get()

    ########  LIVE E2E TESTS #############

    def e2e_controller(self):
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





            ########  BEGIN UNIT TESTS ###########

    def test_login(self):
        # Test with a password
        self.api._request = lambda x, y, z: {'sessionID': 'test',
                                             'userID': 'craig@test.com',
                                             'output_data': [x, y, z]}
        res = self.api.login('craig@test.com', 'abc123')
        golden = {'output_data': ['/login', {'username': 'craig@test.com', 'password': 'abc123'}, 'GET'],
                  'userID': 'craig@test.com', 'sessionID': 'test'}
        self.assertEqual(res, golden)
        self.assertEqual(self.api.session_id, 'test')
        self.assertEqual(self.api.user_id, 'craig@test.com')
        # Test without a password
        self.api._request = lambda x, y, z: {'sessionID': 'test',
                                             'userID': y,
                                             'output_data': [x, y, z]}
        res = self.api.login('craig@test.com')
        golden = {'output_data': ['/login', {'username': 'craig@test.com'}, 'GET'], 'sessionID': 'test',
                  'userID': {'username': 'craig@test.com'}}
        self.assertEqual(res, golden)

    def test_logout(self):
        self.api._request = lambda x, y, z: {'output_data': [x, y, z]}
        self.api.logout()
        self.assertEqual(self.api.session_id, None)
        self.assertEqual(self.api.user_id, None)

    def test_get_list(self):
        self.api._request = lambda x, y, z: {'output_data': [x, y, z]}
        res = self.api.get_list('task', ['1', '2', '3', '4'], ['test', 'test2'])
        self.assertEqual(res, {'output_data': ['/task', {'ids': '1,2,3,4'}, ['test', 'test2']]})

    def test_put(self):
        # With fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        res = self.api.put('task', 'ABC123', {'a': 'b', 'c': 'd'}, ['test', 'test2'])
        self.assertEqual(res, {'output_data': ['/task/ABC123', {'a': 'b', 'c': 'd'}, 'PUT', ['test', 'test2']]})

        # Without fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        res = self.api.put('task', 'ABC123', {'a': 'b', 'c': 'd'})
        self.assertEqual(res, {'output_data': ['/task/ABC123', {'c': 'd', 'a': 'b'}, 'PUT', None]})

    def test_action(self):
        # Without obj ID
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        res = self.api.action('task', 'doSomething', {'a': 'b', 'c': 'd'}, ['test', 'test2'])
        # self.assertEqual(res, {'output_data': ['/task', {'action': 'doSomething', 'a': 'b', 'c': 'd'}, 'PUT', ['test', 'test2']]})

        # With Obj ID
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        res = self.api.action('task', 'doSomething', {'a': 'b', 'c': 'd'}, ['test', 'test2'], 'obj_id')
        self.assertEqual(res, {
            'output_data': ['/task/obj_id', {'action': 'doSomething', 'a': 'b', 'c': 'd'}, 'PUT', ['test', 'test2']]})

    def test__bulksegmenter(self):
        # Check bulk and bulk_create. These have an 'updates' key.
        # Check less than 100 items
        parameters = [{'ID': 'abc', 'name': 'Change me'}, {'ID': 'def', 'name': 'Change me'}]
        bulk_method = lambda updates: updates
        golden = [{'ID': 'abc', 'name': 'Change me'}, {'ID': 'def', 'name': 'Change me'}]
        res = self.api._bulk_segmenter(bulk_method, updates=parameters)
        self.assertEqual(golden, res)

        test_list = []
        bulk_method = lambda updates: self.hash_dict(updates, True)
        for x in range(316):
            test_list.append({'ID': str(x * 5), 'name': 'blarg'})
        res = self.api._bulk_segmenter(bulk_method, updates=test_list)
        golden = ['6c4d278c1c1d0c12675c6e2a4fe0c71fbcd41dc7', 'd15ca064a3541f295c6cd6ca4626e388b164a3ef',
                  'a19776674a17917ea8799e3c489a9c629709ee14', 'df6ec7bdfa83ec8ff867a60e3fc46533a04dfec5']
        self.assertEqual(res, golden)

        parameters = [{'ID': 'abc', 'name': 'Change me'}, {'ID': 'def', 'name': 'Change me'}]
        bulk_method = lambda objids: objids
        golden = [{'ID': 'abc', 'name': 'Change me'}, {'ID': 'def', 'name': 'Change me'}]
        res = self.api._bulk_segmenter(bulk_method, objids=parameters)
        self.assertEqual(golden, res)

        test_list = []
        bulk_method = lambda objids: self.hash_dict(objids, True)
        for x in range(316):
            test_list.append({'ID': str(x * 5), 'name': 'blarg'})
        res = self.api._bulk_segmenter(bulk_method, objids=test_list)
        golden = ['6c4d278c1c1d0c12675c6e2a4fe0c71fbcd41dc7', 'd15ca064a3541f295c6cd6ca4626e388b164a3ef',
                  'a19776674a17917ea8799e3c489a9c629709ee14', 'df6ec7bdfa83ec8ff867a60e3fc46533a04dfec5']
        self.assertEqual(res, golden)

    def test_bulk(self):
        updates = []
        for x in range(316):
            updates.append({'ID': str(x * 5), 'name': 'blarg'})
        # With fields
        self.api._request = lambda path, objcode, updates, fields: [self.hash_dict(updates)]
        res = self.api.bulk('task', updates, ['a', 'b'])
        golden = ['f9a286972b357196d92e8f239303f794fee6167a', 'f9a286972b357196d92e8f239303f794fee6167a',
                  'f9a286972b357196d92e8f239303f794fee6167a', 'f9a286972b357196d92e8f239303f794fee6167a']
        self.assertEqual(res, golden)
        # Check the path
        updates = [1, 2]
        self.api._request = lambda path, objcode, updates, fields: path
        res = self.api.bulk('task', updates, ['a', 'b'])
        path = "/task"
        self.assertEqual(res, path)

        updates = []
        for x in range(82):
            updates.append({'ID': str(x * 5), 'name': 'blarg'})
        # With fields
        self.api._request = lambda x, objcode, updates, fields: [self.hash_dict(updates)]
        res = self.api.bulk('task', updates, ['a', 'b'])
        golden = ['f9a286972b357196d92e8f239303f794fee6167a']
        self.assertEqual(res, golden)

    def test_bulk_create(self):
        updates = []
        for x in range(316):
            updates.append({'ID': str(x * 5), 'name': 'blarg'})
        # With fields
        self.api._request = lambda x, objcode, updates, fields: [self.hash_dict(updates)]
        res = self.api.bulk_create('task', updates, ['a', 'b'])
        golden = ['3e93a477bcf2f542c3efe96111eb92cd57f75fb3', '3e93a477bcf2f542c3efe96111eb92cd57f75fb3',
                  '3e93a477bcf2f542c3efe96111eb92cd57f75fb3', '3e93a477bcf2f542c3efe96111eb92cd57f75fb3']
        self.assertEqual(res, golden)

        # Check the path
        updates = [1, 2]
        self.api._request = lambda path, objcode, updates, fields: path
        res = self.api.bulk_create('task', updates, ['a', 'b'])
        path = "/task"
        self.assertEqual(res, path)

        updates = []
        for x in range(82):
            updates.append({'ID': str(x * 5), 'name': 'blarg'})
        # With fields
        self.api._request = lambda x, objcode, updates, fields: [self.hash_dict(updates)]
        res = self.api.bulk_create('task', updates, ['a', 'b'])
        golden = ['3e93a477bcf2f542c3efe96111eb92cd57f75fb3']
        self.assertEqual(res, golden)

    def test_post(self):
        # With fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        golden = {'output_data': ['/task', {'c': 'd', 'a': 'b'}, 'POST', ['test', 'test2']]}
        res = self.api.post('task', {'a': 'b', 'c': 'd'}, ['test', 'test2'])
        self.assertEqual(res, golden)

        # With fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        golden = {'output_data': ['/task', {'a': 'b', 'c': 'd'}, 'POST', None]}
        res = self.api.post('task', {'a': 'b', 'c': 'd'})
        self.assertEqual(res, golden)

    def test_get(self):
        # With fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        golden = {'output_data': ['/task/abc123', None, 'GET', ['test', 'test2']]}
        res = self.api.get('task', 'abc123', ['test', 'test2'])
        self.assertEqual(res, golden)

        # With fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        golden = {'output_data': ['/task/abc123', None, 'GET', None]}
        res = self.api.get('task', 'abc123', )
        self.assertEqual(res, golden)

    def test_delete(self):

        self.api._request = lambda w, x, y: {'output_data': [w, x, y]}
        golden = {'output_data': ['/task/abc123', {'force': True}, 'DELETE']}
        res = self.api.delete('task', 'abc123', True)
        self.assertEqual(res, golden)

        self.api._request = lambda w, x, y: {'output_data': [w, x, y]}
        golden = {'output_data': ['/task/abc123', {'force': True}, 'DELETE']}
        res = self.api.delete('task', 'abc123')
        self.assertEqual(res, golden)

        self.api._request = lambda w, x, y: {'output_data': [w, x, y]}
        golden = {'output_data': ['/task/abc123', {'force': False}, 'DELETE']}
        res = self.api.delete('task', 'abc123', False)
        self.assertEqual(res, golden)

    def test_bulk_delete(self):
        obj_ids = []
        for x in range(316):
            obj_ids.append(str(x * 5))
        # With fields
        self.api._request = lambda path, objcode, objids: [self.hash_dict(objids)]
        res = self.api.bulk_delete('task', obj_ids, ['a', 'b'])
        golden = ['3c37ef8e02b141e11835637d278ea545974728b6', '3c37ef8e02b141e11835637d278ea545974728b6',
                  '3c37ef8e02b141e11835637d278ea545974728b6', '3c37ef8e02b141e11835637d278ea545974728b6']
        self.assertEqual(res, golden)

        # Check the path
        obj_ids = [1, 2]
        self.api._request = lambda path, objcode, objids: path
        res = self.api.bulk_delete('task', obj_ids, ['a', 'b'])
        path = "/task"
        self.assertEqual(res, path)

        obj_ids = []
        for x in range(82):
            obj_ids.append({'ID': str(x * 5), 'name': 'blarg'})
        # With fields
        self.api._request = lambda path, objcode, objids: [self.hash_dict(objids)]
        res = self.api.bulk_delete('task', obj_ids, ['a', 'b'])
        golden = ['3c37ef8e02b141e11835637d278ea545974728b6']
        self.assertEqual(res, golden)

    def test_search(self):
        # Test without limit or get_all
        self.api._request = lambda path, params, method, fields: {'path': path,
                                                                  'params': params,
                                                                  'method': method,
                                                                  'fields': fields}
        golden = {'fields': ['f1', 'f2'], 'method': 'GET', 'path': '/task/search', 'params': {'a': 'x', 'b': 'x'}}
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'])

        self.assertEqual(golden, res)

        # Test without limit or get_all or fields
        self.api._request = lambda path, params, method, fields: {'path': path,
                                                                  'params': params,
                                                                  'method': method,
                                                                  'fields': fields}
        golden = {'method': 'GET', 'fields': None, 'path': '/task/search', 'params': {'b': 'x', 'a': 'x'}}
        res = self.api.search('task', {'a': 'x', 'b': 'x'})
        self.assertEqual(golden, res)

        # Test with get_all - 2500 results
        self.api._count = lambda objcode, params: 2500
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]
        golden = [
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 500, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 500, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 500, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 500, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 500, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], get_all=True)

        self.assertEqual(golden, res)

        # Test with get_all - 6120 results
        self.api._count = lambda objcode, params: 6120
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]
        golden = [{'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}},
                  {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search',
                   'params': {'b': 'x', '$$FIRST': 6000, 'a': 'x', '$$LIMIT': 120}}]

        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], get_all=True)

        self.assertEqual(golden, res)

        # Test with get_all - 413 results
        self.api._count = lambda objcode, params: 413
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]
        golden = [{'path': '/task/search', 'method': 'GET', 'fields': ['f1', 'f2'],
                   'params': {'$$LIMIT': 413, 'b': 'x', 'a': 'x', '$$FIRST': 0}}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], get_all=True)

        self.assertEqual(golden, res)

        # Test with limit count over limit
        self.api._count = lambda objcode, params: 6120
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]

        golden = [{'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'},
                  {'fields': ['f1', 'f2'], 'params': {'$$FIRST': 4000, 'a': 'x', 'b': 'x', '$$LIMIT': 10},
                   'path': '/task/search', 'method': 'GET'}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], limit=4010)

        self.assertEqual(golden, res)

        # Test with limit count over limit
        self.api._count = lambda objcode, params: 2100
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]
        golden = [
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 100, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 100, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 100, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 100, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']},
            {'path': '/task/search', 'params': {'b': 'x', '$$FIRST': 2000, '$$LIMIT': 100, 'a': 'x'}, 'method': 'GET',
             'fields': ['f1', 'f2']}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], limit=4000)

        self.assertEqual(golden, res)
        # Test with limit and get_all

    def test_count(self):
        pass

    def test_report(self):
        pass

    def test_make_update_as_user(self):
        pass

    def test__parse_parameter_lists(self):

        params = {'status': ['CUR', 'PLN', 'APP'],
                  'status_Mod': 'in'}
        res = self.api._parse_parameter_lists(params)
        # Convert to a list so there can be a stable order to the elements. Without this Python will somewhat
        # randomly re-order the elements.
        res = sorted(res.split("&"))
        golden = ['status=APP', 'status=CUR', 'status=PLN', 'status_Mod=in']
        self.assertEqual(res, golden)

        params = {}
        params['assignedToID_Mod'] = "notblank"
        params['percentComplete'] = "100"
        params['percentComplete_Mod'] = "lt"

        params['canStart'] = ['true', 'false', 'maybe']
        params['canStart_Mod'] = 'in'

        params['plannedStartDate'] = '$$TODAY+5d'
        params['plannedStartDate_Mod'] = 'lt'

        params['project:statusEquatesWith'] = ['CUR', 'PLN', 'TST']
        params['project:statusEquatesWith_Mod'] = 'in'

        params['DE:project:Clover Notifications'] = 'On'
        params['DE:project:Clover Notifications_Mod'] = 'eq'

        params['DE:Send Notifications for This Task'] = 'Yes'
        params['DE:Send Notifications for This Task_Mod'] = 'eq'
        res = self.api._parse_parameter_lists(params)
        res = sorted(res.split("&"))
        golden = ['DE:Send Notifications for This Task=Yes', 'DE:Send Notifications for This Task_Mod=eq',
                  'DE:project:Clover Notifications=On', 'DE:project:Clover Notifications_Mod=eq',
                  'assignedToID_Mod=notblank', 'canStart=false', 'canStart=maybe', 'canStart=true', 'canStart_Mod=in',
                  'percentComplete=100', 'percentComplete_Mod=lt', 'plannedStartDate=$$TODAY+5d',
                  'plannedStartDate_Mod=lt', 'project:statusEquatesWith=CUR', 'project:statusEquatesWith=PLN',
                  'project:statusEquatesWith=TST', 'project:statusEquatesWith_Mod=in']

        self.assertEqual(res, golden)

    def test__make_request(self):
        path = '/task/abc123'
        params = {'a': 'b'}
        method = self.api.GET
        fields = ['a', 'b', 'c']

        self.api._open_api_connection = self.api_response

        res = self.api._request(path, params, method, fields)
        res = sorted(res)
        self.assertEqual(1, 1)
