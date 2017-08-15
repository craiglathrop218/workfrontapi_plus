from workfrontapi_plus.api import Api, Project, Task, Issue
from wfconfig import WorkfrontConfig
from workfrontapi_plus.objects.core_wf_object import WorkfrontObject

api = Api(WorkfrontConfig.subdomain,
                    'preview',
          api_version='6.0',
          api_key=WorkfrontConfig.api_key,
          test_mode=True)


#test = WorkfrontObject('data', api)
proj = Project(api, '58a250c5000227f75154615d375388ba')
#proj.add_comment('blah blah blah')

task = Task(api, '598b7754018ab55188def1b15b2f98eb')
task.add_comment('working for a task')

issue = Issue(api, '5992463e0008657d1ccdfaf7ea1e6a5e')
issue.add_comment('working for an issue')
