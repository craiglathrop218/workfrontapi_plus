from workfrontapi_plus.api import Api
from wfconfig import WorkfrontConfig


api = Api(WorkfrontConfig.subdomain,
                    'my',
          api_version='7.0',
          api_key=WorkfrontConfig.api_key,
          test_mode=True)



class Controller(object):
    def __init__(self):
        self.s_updates = StatusUpdates()

    def main(self):
        task_results = self.s_updates.search_for_task_items()
        issue_results = self.s_updates.search_for_issue_items()

        self.s_updates.deal_with_results('TASK', task_results)
        self.s_updates.deal_with_results('OPTASK', issue_results)


class StatusUpdates(object):
    def search_for_task_items(self):
        params = {'objectCategoriesMM:ID': '59938d71004361ba93ea1c9104898d2b',
                  'objectCategoriesMM:ID_Mod': 'in',
                  'DE:Status Update_Mod': 'notblank'}
        fields = ['DE:Status Update']
        res = api.search('TASK', params, fields)
        return res

    def search_for_issue_items(self):
        params = {'objectCategoriesMM:ID': '59938d41004356ca81bb12a678230b6d',
                  'objectCategoriesMM:ID_Mod': 'in',
                  'DE:Status Update_Mod': 'notblank'}
        fields = ['DE:Status Update']
        res = api.search('OPTASK', params, fields)
        return res

    def write_update(self, objcode, objid, comment_text):
        comment_dict = {'objID': objid,
                        'noteText': comment_text,
                        'noteObjCode': objcode}
        res = api.post('NOTE', comment_dict)

        return res

    def clear_status_update(self, obj_code, obj_id):
        updates = {'DE:Status Update': ''}

        res = api.put(obj_code, obj_id, updates)
        return res

    def deal_with_results(self, objcode, results):
        for item in results:
            self.write_update(objcode, item['ID'], item['DE:Status Update'])
            self.clear_status_update(objcode, item['ID'])
# params = {'objectCategoriesMM:ID': '59938d71004361ba93ea1c9104898d2b',
#           'objectCategoriesMM:ID_Mod':'in'}




#a = search_for_task_items()
#write_update('TASK', '598b7754018ab55188def1b15b2f98eb', 'comment jtwwktjghkj')


C = Controller()
#
C.main()