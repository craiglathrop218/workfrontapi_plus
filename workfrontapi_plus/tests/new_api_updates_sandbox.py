from workfrontapi_plus import Api, Project, Task, Issue
from wfconfig import WorkfrontConfig
import requests
from workfrontapi_plus.objects.core_wf_object import WorkfrontObject

api = Api(WorkfrontConfig.subdomain,
          'preview',
          api_version='6.0',
          api_key=WorkfrontConfig.api_key,
          test_mode=True)


f = open('C:/Users/robal/Documents/testdocumentPDF.pdf', 'rb')
url = 'https://idt.preview.workfront.com/attask/api/v7.0/upload?apiKey=1q2tz2xgsgf2y44mvz78vxn1y0jhqc7h'
file = open('C:/Users/robal/Documents/testdocumentPDF.pdf', 'rb')
# files = {'uploadedFile': file}
# values = {'author': 'John Smith'}
# r = requests.post(url, files=files)
# r = requests.post(url, files=files)
# val = r.json()
api.make_document(file, 'PROJ', '58a250c5000227f75154615d375388ba', 1)
a = 0
# res = api.upload_file(f)
# print(res)
# issu = Issue(api, issue_id='59936d1800295eacc7f69885696ebcdd')
# issu.name = 'NEW ISSUE NAME!'
# issu.status = 'CLS'
# issu.save()
# issu.add_comment('new issue comment.....')
# issu.share(['54107a1a001b8dd814f4d035f586991c'], 'view')
# tsk = Task(api, task_id='598b7754018ab3670280d87b2071896b')
# tsk.name = 'NEW ISSUE NAME!'
# tsk.save()
# tsk.add_comment('new issue comment')
# test = WorkfrontObject('data', api)
# proj = Project(api, project_id='58a250c5000227f75154615d375388ba')
#
# res = proj.status = 'PLN'
# proj.description = 'New Description for test project from python api'
# proj.add_comment('comment -------')
# proj.save()

# proj = Project(api, name='New Test Project')
# proj.status = 'PLN'
# proj.description = 'New Description for test project from python api'
# proj.save()
# print(proj.ID)
# task = Task(api, '598b7754018ab55188def1b15b2f98eb')
# task.add_comment('working for a task')
#
# issue = Issue(api, '5992463e0008657d1ccdfaf7ea1e6a5e')
# issue.add_comment('working for an issue')
