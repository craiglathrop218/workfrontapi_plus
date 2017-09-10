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
from workfrontapi_plus import Api, Tools

from wfconfig import WorkfrontConfig

import hashlib, json, requests
from nose.tools import assert_true
import random

'''https://realpython.com/blog/python/testing-third-party-apis-with-mocks/'''


class TestWorkfrontE2E(TestCase):
    api = Api(WorkfrontConfig.subdomain,
              'preview',
              api_version='6.0',
              api_key=WorkfrontConfig.api_key,
              )

    ########  LIVE E2E TESTS #############

    def test_e2e_controller(self):
        self.api._request = self.api._make_request
        self.api.debug = True
        rnd = str(random.randint(2, 900) * 54)
        rnd = rnd.encode('ascii')
        hash_str = hashlib.sha224(rnd).hexdigest()
        # Make some projects
        project_list = []
        test_proj_num = 3

        # Make the API return an error
        self.api.return_api_errors = True
        error_res = self.api.search('task', {}, fields=['booobooobooooboooboo'])
        self.assertEqual('APIModel V6_0 does not support field booobooobooooboooboo (Task)', error_res)
        print('Proper Error '+error_res)

        # Make three projects
        for x in range(test_proj_num):
            project_list.append(self.make_proj(hash_str))

        proj_id_list = [d['ID'] for d in project_list]

        print('Created project: ', project_list[0]['name'], ' with ID: ', project_list[0]['ID'])

        # Make a task
        task = self.make_a_task(project_list[0]['ID'])
        print('Created task: ', task['name'])

        # Share the task out
        res = self.share(task['ID'])
        print('Shared task with: ', task['name'])


        # Test get_list
        res = self.api.get_list('proj', proj_id_list)
        print('Returned a list of {0} projects'.format(len(res)))

        # Test Action by Assigning User
        params = {'objID': WorkfrontConfig.test_user_id,
                  'objCode': 'USER'}
        assign_action = self.do_action('TASK', 'assign', params, objid=task['ID'])
        print('Assigned task to ', WorkfrontConfig.test_user_id)

        # Test Put

        params = {'status': 'INP'}

        res = self.tst_put('TASK', task['ID'], params)

        print('Updated task ', task['ID'], ' to have a status of in progress')

        # Delete a task
        del_res = self.delete_a_task(task['ID'])
        print('Deleted task: ', del_res['success'])

        # Make a lot of tasks
        tasks = self.make_bulk_tasks(project_list[0]['ID'])
        print('Created {0} tasks'.format(len(tasks)))
        task_ids = [x['ID'] for x in tasks]
        # # Update a lot of tasks
        t_updates = self.bulk_update_tasks(task_ids, hash_str)
        print('Updated task name to {0}.'.format(t_updates[0]['name']))

        # Test search
        params = {'name': hash_str, 'name_Mod': 'cicontains'}
        search_res = self.search('PROJ', params)

        search_res_id_list = [d['ID'] for d in search_res]

        self.assertCountEqual(search_res_id_list, proj_id_list)
        print('Successfully searched for and found project: ', search_res[0]['ID'])
        a = 0
        # self.assertEqual(len(search_res), len(task_ids))
        #
        del_res = self.bulk_delete_tasks(task_ids)
        print('Deleted task: ', del_res['success'])

        # self.delete_a_proj(project['id'])

        # Test Document Uploading
        file = open('../test_doc.pdf', 'rb')
        made_doc = self.make_doc(file, 'PROJ', project_list[0]['ID'], 1)
        print('Got handle ', made_doc)

        posted_doc = self.post_doc('document.pdf', made_doc, 'PROJ', project_list[0]['ID'], 1)

        print('Posted document named, ', '"document.pdf"')

        # Test Report
        # params = {'DE:JIRA Project ID=CTP',
        #          'DE:JIRA Project ID_Mod=cieq'}
        #
        # report = self.report_tst('PROJ', params)


        # Test Count

        params = {'status': 'CUR'}

        count_res = self.get_count('TASK', params)
        print('Got count of ', count_res)

        # Test Get List
        # ids = ['599636f70000b26a0d9032d3f3dc7eb6', '59934a0e00068fc9ab14ef083d54962f',
        #        '56d8b69f0077e4db6bdb89c9288ec11c']
        # fields = ['name', 'status']
        # list = self.get_the_list('PROJ', ids, fields)
        #
        # print('Got the list ', list)



        # Test Login
        res = self.login_tst(WorkfrontConfig.test_login_email, WorkfrontConfig.test_pass)
        self.assertEqual(res['userID'], WorkfrontConfig.test_user_id, WorkfrontConfig.test_pass)
        print('Logged into user ', res['userID'])
        a = 0

        # Test Make Update as User
        params = {'objID': project_list[0]['ID'],
                  'noteText': 'Comment coming from workfront',
                  'noteObjCode': 'PROJ'}
        made_comment = self.make_update_by_user(WorkfrontConfig.test_make_update_email, 'post', 'NOTE', params)
        print('Created comment: ', made_comment['noteText'], ' on behalf of ', WorkfrontConfig.test_login_email)

        # Test Logout
        logout_res = self.logout_tst()
        self.assertEqual(logout_res['success'], True)
        # self.assertEqual(logout_res['session_id'], None)
        # self.assertEqual(logout_res['user_id'], None)

        # Delete the test projects
        for x in range(test_proj_num):
            p_id = project_list[x]['ID']
            self.delete_a_proj(p_id)

            print('Deleted the project ', p_id)

    def login_tst(self, username, password=None):
        return self.api.login(username, password)

    def logout_tst(self):
        res = self.api.logout()
        return res

    def get_count(self, objcode, params):
        return self.api.count(objcode, params)

    def make_doc(self, file, obj_code, obj_id, version=1):
        return self.api.make_document(file, obj_code, obj_id, version)

    def post_doc(self, name, handle, obj_code, obj_id, version):
        self.api.post_document(name, handle, obj_code, obj_id, version)

    def get_the_list(self, objcode, ids, fields=None):
        return self.api.get_list(objcode, ids, fields)

    def do_action(self, objcode, action, params, fields=None, objid=None):
        return self.api.action(objcode, action, params, fields, objid)

    def report_tst(self, objcode, params, agg_field=None, agg_func=None, group_by_field=None, rollup=False):
        return self.api.report(objcode, params, agg_field, agg_func, group_by_field, rollup)

    def tst_put(self, objcode, objid, params, fields=None):
        return self.api.put(objcode, objid, params, fields)

    def make_update_by_user(self, user_email, exec_method, objcode, params, objid=None, action=None, objids=None,
                            fields=None, logout=False):
        res = self.api.make_update_as_user(user_email, exec_method, objcode, params, objid, fields, logout)
        return res

    def make_proj(self, hash_str):
        return self.api.post('proj', {'name': 'e2e Test Project {0}'.format(hash_str), 'status': 'PLN'})

    def make_a_task(self, proj_id):
        return self.api.post('task', {'name': 'First Task', 'projectID': proj_id})

    def share(self, task_id):
        share_user = WorkfrontConfig.clover_user_id
        return self.api.share_obj('task', task_id, share_user, 'USER', 'manage')

    def delete_a_task(self, task_id):
        return self.api.delete('task', task_id)

    def make_bulk_tasks(self, proj_id):
        tasks = []
        for x in range(30):
            tasks.append({'name': 'This is task number {0}'.format(x),
                          'projectID': proj_id,
                          'plannedStartDate': '2017-12-01'
                          })
        return self.api.bulk_create('task', tasks)

    def bulk_update_tasks(self, task_ids, hash_str):
        updates = []
        for t_id in task_ids:
            updates.append({'name': 'Hash: {0} - {1}'.format(hash_str, t_id[4:]),
                            'ID': t_id,
                            'description': '''Description here'''})

        return self.api.bulk('task', updates)

    def bulk_delete_tasks(self, task_ids):
        return self.api.bulk_delete('task', task_ids)

    def live_search(self, hash_str):
        return self.api.search('task', {'name': 'Updated name {0}'.format(hash_str), 'name_Mod': 'cicontains'},
                               ['name'])

    def search(self, objcode, params, fields=None, get_all=False, limit=None):
        return self.api.search(objcode, params, fields, get_all, limit)

    def make_error(self):

        with self.assertRaises(Exception) as context:
            res = self.api.search('task', {'namea': 'cra', 'name_Mod': 'cicontains'}, ['name'])

    def delete_a_proj(self, proj_id):
        return self.api.delete('proj', proj_id)
