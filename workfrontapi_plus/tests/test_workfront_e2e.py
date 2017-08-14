from unittest import TestCase
from workfrontapi_plus import Workfront

from wfconfig import WorkfrontConfig

import hashlib, json, requests
from nose.tools import assert_true
import random


'''https://realpython.com/blog/python/testing-third-party-apis-with-mocks/'''

class TestWorkfrontE2E(TestCase):

    api = Workfront(WorkfrontConfig.subdomain,
                    'preview',
                    api_version='6.0',
                    api_key=WorkfrontConfig.api_key,
                    test_mode=True)

########  LIVE E2E TESTS #############

    def test_e2e_controller(self):
        self.api._request = self.api._make_request
        self.api.debug = True
        random.seed(4)
        rnd = str(random.randint(2, 90) * 54)
        rnd = rnd.encode('ascii')
        hash_str = hashlib.sha224(rnd).hexdigest()
        # Make a project
        project = self.make_proj()
        print('Created project: ', project['name'])

        # Make a task
        # task = self.make_a_task(project['ID'])
        # print('Created task: ', task['name'])
        #
        # # Delete a task
        # del_res = self.delete_a_task(task['ID'])
        # print('Deleted task: ', del_res['success'])

        # Make a lot of tasks
        tasks = self.make_bulk_tasks(project['ID'])
        print('Created {0} tasks'.format(len(tasks)))
        task_ids = [x['ID'] for x in tasks]
        # Update a lot of tasks
        t_updates = self.bulk_update_tasks(task_ids, hash_str)
        print('Updated task name to {0}.'.format(t_updates[0]['name']))

        # Test search
        self.assertEqual(len(self.live_search(hash_str)), len(task_ids))

        del_res = self.bulk_delete_tasks(task_ids)
        print('Deleted task: ', del_res['success'])



        self.delete_a_proj(project['id'])



    def make_proj(self):
        return self.api.post('proj', {'name': 'Test Project', 'status': 'PLN'})

    def make_a_task(self, proj_id):
        return self.api.post('task', {'name': 'First Task', 'projectID': proj_id})

    def delete_a_task(self, task_id):
        return self.api.delete('task', task_id)

    def make_bulk_tasks(self, proj_id):
        tasks = []
        for x in range(150):
            tasks.append({'name': 'This is the First Task',
                          'projectID': proj_id,
                          'plannedStartDate': '2017-12-01',
                          'extRefID': 'This is a test',
                          'description': 'This is a '
                          })
        return self.api.bulk_create('task', tasks)

    def bulk_update_tasks(self, task_ids, hash):
        updates = []
        for t_id in task_ids:
            updates.append({'name': 'update aaaaaaaaa the First Task',
                            'ID': t_id,
                            'plannedStartDate': '2017-12-01',
                            'extRefID': 'This is a test',
                            'description': 'This is a '})

        return self.api.bulk('task', updates)

    def bulk_delete_tasks(self, task_ids):
        return self.api.bulk_delete('task', task_ids)

    def live_search(self, hash):
        return self.api.search('task', {'name': 'Updated name {0}'.format(hash), 'name_Mod': 'cicontains'}, ['name'])


    def make_error(self):

        with self.assertRaises(Exception) as context:
            res = self.api.search('task', {'namea': 'cra', 'name_Mod': 'cicontains'}, ['name'])

    def delete_a_proj(self, proj_id):
        return self.api.delete('proj', proj_id)