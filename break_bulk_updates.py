
from workfrontapi_plus import Api

from wfconfig import WorkfrontConfig

class BreakBulkUpdates(object):

    api = Api(subdomain=WorkfrontConfig.subdomain,
              api_key=WorkfrontConfig.api_key,
              env='sb01',
              api_version='6.0',
              test_mode=True)

    def start(self):
        self.api._request = self.api._make_request
        self.api.debug = True

        # Make a project
        project = self.make_proj()
        print('Created project: ', project['name'])

        # Make 28 tasks - This should work
        tasks = self.make_bulk_tasks(project['ID'], 28)

        # Now make 29 tasks - This should work fine to, but it breaks
        tasks = self.make_bulk_tasks(project['ID'], 29)

    def make_proj(self):
        return self.api.post('proj', {'name': 'Test Project', 'status': 'PLN'})

    def make_bulk_tasks(self, proj_id, max_updates):
        self.api._max_bulk = max_updates
        tasks = []
        for x in range(100):
            tasks.append({'name': 'This is the First Task',
                          'projectID': proj_id,
                          'plannedStartDate': '2017-12-01',
                          'extRefID': 'This is a test',
                          'description': 'This is a longer description test. Test test test.'})
        return self.api.bulk_create('task', tasks)

b = BreakBulkUpdates()

b.start()
