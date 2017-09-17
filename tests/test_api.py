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
    api = Api(WorkfrontConfig.subdomain, 'preview', api_key=WorkfrontConfig.api_key)

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
        data_output_list = []
        for item in data_list:
            key_value_split = item.split("=")
            # str() because some stuff is byte vale b"..."
            params_dict[str(key_value_split[0])] = str(key_value_split[1])
            data_output_list.append({key_value_split[0]: key_value_split[1]})

        params_dict['path'] = dest
        params_dict['data'] = data_output_list

        return params_dict

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

    # def test_make_error(self):
    #     self.api._request = self.api._make_request
    #     with self.assertRaises(Exception) as context:
    #         res = self.api.search('task', {'namea': 'cra', 'name_Mod': 'cicontains'}, ['name'])





            ########  BEGIN UNIT TESTS ###########

    def test_login(self):
        # Test with a password
        self.api._request = lambda x, y, z: {'sessionID': 'test',
                                             'userID': 'craig@test.com',
                                             'output_data': [x, y, z]}
        res = self.api.login('craig@test.com', 'abc123')
        golden = {'output_data': ['/login', {'username': 'craig@test.com', 'password': 'abc123'}, 'POST'],
                  'userID': 'craig@test.com', 'sessionID': 'test'}
        self.assertEqual(res, golden)
        self.assertEqual(self.api.session_id, 'test')
        self.assertEqual(self.api.user_id, 'craig@test.com')
        # Test without a password
        self.api._request = lambda x, y, z: {'sessionID': 'test',
                                             'userID': y,
                                             'output_data': [x, y, z]}
        res = self.api.login('craig@test.com')
        golden = {'output_data': ['/login', {'username': 'craig@test.com'}, 'POST'], 'sessionID': 'test',
                  'userID': {'username': 'craig@test.com'}}
        self.assertEqual(res, golden)

    def test_logout(self):
        self.api._request = lambda x, y, z: {'output_data': [x, y, z]}
        self.api.logout()
        self.assertEqual(self.api.session_id, None)
        self.assertEqual(self.api.user_id, None)

    def test_get_list(self):
        self.api._request = lambda x, y, z, a: {'output_data': [x, y, z, a]}
        res = self.api.get_list('task', ['1', '2', '3', '4'], ['test', 'test2'])
        self.assertEqual(res, {'output_data': ['/task', {'id': '1,2,3,4'}, 'GET', ['test', 'test2']]})

    def test_put(self):
        # With fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        res = self.api.put('task', 'ABC123', {'a': 'b', 'c': 'd'}, ['test', 'test2'])
        self.assertIsInstance(res['output_data'], list)

        # Without fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        res = self.api.put('task', 'ABC123', {'a': 'b', 'c': 'd'})
        self.assertIsInstance(res['output_data'], list)

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
        res = self.api._bulk_segmenter(bulk_method, updates=parameters, objs_per_loop=6)
        self.assertEqual(golden, res)

        test_list = []
        bulk_method = lambda updates: self.hash_dict(updates, True)
        for x in range(316):
            test_list.append({'ID': str(x * 5), 'name': 'blarg'})
        res = self.api._bulk_segmenter(bulk_method, updates=test_list, objs_per_loop=5)
        golden = ['d4da02f8bbc63a4bfdfdad5e4766f5a6d4df5e64', 'b1e5d798e124c498b93806965dec8d5bdf864f2e', 'f208050cffbd096fd6007cb65b2ddbde089e26a2', '3e55a10fb7fac9d3070573c29a7bbb8877da908b', '59d3d8ed5598effe28c8c58e447d447c686447b6', 'ef87bbca29e1800f83f77cd31b7c394476dfef7c', 'a5f3f4c0d0972371d0ecfced687fcaec3e7df9c4', '542c263190bd170548455f422c185662f9de9a3b', '8f18822216690b0b53209c831fc09f2df75172a2', '061eef2ee159440a45948f71b8d119e724cbb39b', '18c9a6d440d936e2da1a703bc28b363345f73d29', '4afcd003a69b8e16b742111a3b7f48caa0093d9f', 'ad889a553efdc9d12bacbd9cdfac8ce6195ef4e3', '32bcf872ea4d7b53fe29f5253135d364a5a32c12', '43e851739083280e1d605c6b49fa578c2681d5e6', '165806f65e1f47da53783d479c64380366edde67', '72d8af330b71cc0e8a9d720a314a5430de9a198f', 'a3b69771c0b32ff45174602a0b9b2c04d8f4de81', 'ab1dc2f16765365af7758041f7aede08e66eec79', '73f321e3c9e8cba646db693d8e92ad656362840f', 'd57eb94fe0c9610092852eaffd9d846819f4ff96', '834800f41ccda4cd860cafa8ada6d5ea3becf3f2', '88caad9365d90f7d1774cd02b7a4c37a497c9e07', '681832fb6faa3740bde7d80e560c3bb464462cf3', 'bbbae94974bfc90e08bc31f903a06fda387f5f67', 'cbeb91b7f7e1f20e6476c54aba635a00c64b1592', '51f82d87a449d76fee9abbb4e76cca344a5081cc', 'c71c756a9fd3fa948602c592634f6c91da85cf97', '69835a8ab76249798d80bedddde4a5139fd8b623', '3c04c981c5abcb3bf44bafa8d220d09ac2b77e71', '72ff546fdccf562100de0c405da350023465e964', '8528338b664b58328d7f4752233764914d7ab282', '1336e9711597440749a7fa8f9702f6355d1605a2', '364139384f674f0bd01df58378d9c56970cca09f', '711f49c529016015f8f217ac84e53f9c6314c775', '327355a7d9cc766b0c01cad1b5a93b611f0fb4bb', 'd945f91626e14257cb5f6056259c96c3724fd5cc', 'd5b53f60092cdc4b3c5e482d8af4f16e707570ee', '17fe0a43c5d5a116224ac9fc91a28764b2ba03c6', 'f89c14eeb4a2115ce2c490a6e142f939fb44b178', '4ead2cab5b087ba12cd3f03bdb9f30938bb225d7', '9a4cde024b3a2ad67b4ac7228586e33eb9be35da', '9b640d2cf399c76f19382fe3b39b15f332b67f2b', '8e184a93eee6e5d2ac8af0d08b0fa20922b308a1', '46d66820761b202ad10c89fb628aaf94b6a3c6c0', '6a14e93c50ad4cf6901c6e3408b6356e75c594ee', 'b145b7ac63be465fdaeaae4d03d2ce83d2087223', '67f24ff886e5b43eef1b967094f1c6c57ed4c897', '710f7a381fac90f74bf28351c55ce03edec240c6', '0ef3585bbcb046ee770793f7a980f385ed84149b', '83ad51f4548e52baa892ee64a61eddf4bc2e217b', '370ca6fd927e7a5b030ca3208b09663a1ba69c20', '0c37ac5fbcb2c0f051bd4dcd1615715fc1eaae47', 'a2643521bf057931d4318c72103b2bb39714b25e', '08d6f178330b395ec364ed956f5825903ed12982', '7361f022e6270818e8e4ed8a5be3a9a511624bf0', '26406b6bdb394e189672ad4168be732cb797cff4', '4d3011a1becb7c7c61471b08072a11e046f53012', 'de8ccc540533f803808eeea072e5e87495aec86d', '434edce24c99785658526588a894603dfb9f9393', '755e99dcfe367e9831148fd650fef5b464b3c5a1', 'f304d4e68da83ed63330b8f176457f37e60f6e25', 'f8635a249e32ad9d605599983d2ac7db6ab17c56', '9a97f647347765abcdfdb4c6fc098285625a7023']

        self.assertCountEqual(res, golden)

        parameters = [{'ID': 'abc', 'name': 'Change me'}, {'ID': 'def', 'name': 'Change me'}]
        bulk_method = lambda updates: updates
        golden = [{'ID': 'abc', 'name': 'Change me'}, {'ID': 'def', 'name': 'Change me'}]
        res = self.api._bulk_segmenter(bulk_method, updates=parameters, objs_per_loop=5)
        self.assertCountEqual(golden, res)

        test_list = []
        bulk_method = lambda obj_ids: self.hash_dict(obj_ids, True)
        for x in range(316):
            test_list.append({'ID': str(x * 5), 'name': 'blarg'})
        res = self.api._bulk_segmenter(bulk_method, obj_ids=test_list, objs_per_loop=100)
        golden = ['6c4d278c1c1d0c12675c6e2a4fe0c71fbcd41dc7', 'd15ca064a3541f295c6cd6ca4626e388b164a3ef',
                  'a19776674a17917ea8799e3c489a9c629709ee14', 'df6ec7bdfa83ec8ff867a60e3fc46533a04dfec5']
        self.assertCountEqual(res, golden)

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
        golden = {'output_data': ['/task', {'updates': '{"c": "d", "a": "b"}'}, 'POST', ['test', 'test2']]}
        res = self.api.post('task', {'a': 'b', 'c': 'd'}, ['test', 'test2'])
        self.assertCountEqual(res, golden)

        # With fields
        self.api._request = lambda w, x, y, z: {'output_data': [w, x, y, z]}
        golden = {'output_data': ['/task', {'updates': '{"c": "d", "a": "b"}'}, 'POST', None]}
        res = self.api.post('task', {'a': 'b', 'c': 'd'})
        self.assertCountEqual(res, golden)

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
        self.api._request = lambda path, objcode, obj_ids: [self.hash_dict(obj_ids)]
        res = self.api.bulk_delete('task', obj_ids, ['a', 'b'])
        golden = ['3c37ef8e02b141e11835637d278ea545974728b6', '3c37ef8e02b141e11835637d278ea545974728b6',
                  '3c37ef8e02b141e11835637d278ea545974728b6', '3c37ef8e02b141e11835637d278ea545974728b6']
        self.assertEqual(res, golden)

        # Check the path
        obj_ids = [1, 2]
        self.api._request = lambda path, objcode, obj_ids: path
        res = self.api.bulk_delete('task', obj_ids, ['a', 'b'])
        path = "/task"
        self.assertEqual(res, path)

        obj_ids = []
        for x in range(82):
            obj_ids.append({'ID': str(x * 5), 'name': 'blarg'})
        # With fields
        self.api._request = lambda path, objcode, obj_ids: [self.hash_dict(obj_ids)]
        res = self.api.bulk_delete('task', obj_ids, ['a', 'b'])
        golden = ['3c37ef8e02b141e11835637d278ea545974728b6']
        self.assertEqual(res, golden)

    def test_search(self):
        # Test without limit or get_all
        self.api._request = lambda path, params, method, fields: {'path': path,
                                                                  'params': params,
                                                                  'method': method,
                                                                  'fields': fields}
        golden = {'params': {'a': 'x', 'b': 'x'}, 'fields': ['f1', 'f2'], 'method': 'GET', 'path': '/task/search'}
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
        golden = [{'params': {'$$FIRST': 2000, 'b': 'x', '$$LIMIT': 500, 'a': 'x'}, 'method': 'GET', 'path': '/task/search', 'fields': ['f1', 'f2']}, {'params': {'$$FIRST': 2000, 'b': 'x', '$$LIMIT': 500, 'a': 'x'}, 'method': 'GET', 'path': '/task/search', 'fields': ['f1', 'f2']}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], get_all=True)

        self.assertCountEqual(golden, res)

        # Test with get_all - 6120 results
        self.api._count = lambda objcode, params: 6120
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]
        golden = [{'path': '/task/search', 'method': 'GET', 'params': {'b': 'x', 'a': 'x', '$$LIMIT': 120, '$$FIRST': 6000}, 'fields': ['f1', 'f2']}, {'path': '/task/search', 'method': 'GET', 'params': {'b': 'x', 'a': 'x', '$$LIMIT': 120, '$$FIRST': 6000}, 'fields': ['f1', 'f2']}, {'path': '/task/search', 'method': 'GET', 'params': {'b': 'x', 'a': 'x', '$$LIMIT': 120, '$$FIRST': 6000}, 'fields': ['f1', 'f2']}, {'path': '/task/search', 'method': 'GET', 'params': {'b': 'x', 'a': 'x', '$$LIMIT': 120, '$$FIRST': 6000}, 'fields': ['f1', 'f2']}]

        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], get_all=True)

        self.assertCountEqual(golden, res)

        # Test with get_all - 413 results
        self.api._count = lambda objcode, params: 413
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]
        golden = [{'path': '/task/search', 'method': 'GET', 'fields': ['f1', 'f2'],
                   'params': {'$$LIMIT': 413, 'b': 'x', 'a': 'x', '$$FIRST': 0}}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], get_all=True)

        self.assertCountEqual(golden, res)

        # Test with limit count over limit
        self.api._count = lambda objcode, params: 6120
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]

        golden = [{'path': '/task/search', 'method': 'GET', 'params': {'$$FIRST': 4000, 'b': 'x', '$$LIMIT': 10, 'a': 'x'}, 'fields': ['f1', 'f2']}, {'path': '/task/search', 'method': 'GET', 'params': {'$$FIRST': 4000, 'b': 'x', '$$LIMIT': 10, 'a': 'x'}, 'fields': ['f1', 'f2']}, {'path': '/task/search', 'method': 'GET', 'params': {'$$FIRST': 4000, 'b': 'x', '$$LIMIT': 10, 'a': 'x'}, 'fields': ['f1', 'f2']}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], limit=4010)

        self.assertCountEqual(golden, res)

        # Test with limit count over limit
        self.api._count = lambda objcode, params: 2100
        self.api._request = lambda path, params, method, fields: [{'path': path,
                                                                   'params': params,
                                                                   'method': method,
                                                                   'fields': fields}]
        golden = [{'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search', 'params': {'$$LIMIT': 100, 'a': 'x', '$$FIRST': 2000, 'b': 'x'}}, {'method': 'GET', 'fields': ['f1', 'f2'], 'path': '/task/search', 'params': {'$$LIMIT': 100, 'a': 'x', '$$FIRST': 2000, 'b': 'x'}}]
        res = self.api.search('task', {'a': 'x', 'b': 'x'}, ['f1', 'f2'], limit=4000)

        self.assertCountEqual(golden, res)
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
        golden = [{'fields': 'a,b,c'}, {'apiKey': 'fc7t01vo9n6ft3osd528ym7m68dn7wwv'}, {'a': 'b'}, {'method': 'GET'}]
        self.assertCountEqual(res, golden)

    # @todo Make a unit test for count method
    # @todo Make unit test for report
    # @todo Make unit test for upload_document
    # @todo Make unit test for make_document
    # @todo Make unit test for post_document
    # @todo Make unit test for make_update_as_user
    # @todo Make unit test for _parse_post_param_list
    # @todo Make unit test for _p_open_api_connection (maybe)
    # @todo Make unit test for _request_upload_file
    # @todo Make unit test for _p_upload_file
    # @todo Make unit test for _set_authentication
    # @todo Make unit test for _set_authentication
