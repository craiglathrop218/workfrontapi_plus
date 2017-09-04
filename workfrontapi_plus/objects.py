"""Copyright 2017, Integrated Device Technologies, Inc.

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

from workfrontapi_plus.core_wf_object import WorkfrontObject


# class Note(object):
#     def __init__(self, objcode, objid):
#         self.objcode = objcode
#         self.objid = objid
#
#     def create_note_dictionary(self, comment_text):
#         comment_dict = {}
#         comment_dict['noteObjID'] = self.objid
#         comment_dict['noteText'] = comment_text
#         comment_dict['noteObjCode'] = self.objcode
#
#         return comment_dict


class _WorkTypeObject(WorkfrontObject):
    """
    A class that shares common traits with issues, tasks, and projects
    """

    def __init__(self, data=None, api=None, obj_code=None, obj_id=None, name=None, convert_dates=False, fields=None):

        super().__init__(data, api, obj_code=obj_code, obj_id=obj_id, convert_dates=convert_dates, fields=fields)
        if name:
            self.name = name

    def change_status(self, new_status):
        self.params['status'] = new_status
        return self.params

    def add_comment(self, comment_text, author_email=None):
        if author_email:
            if not self.api.api_key:
                raise ValueError(
                        'To post comment on behalf of a user, an admin API key must be used for authentication.')
            else:
                self.api.login(author_email)

        comment = self._create_note_dictionary(comment_text)
        res = self.api.post('NOTE', comment)
        # Clear the login session if the update was made on behalf of the user
        self.api.logout()
        return res

    def _create_note_dictionary(self, comment_text):
        comment_dict = {'objID': self.ID,
                        'noteText': comment_text,
                        'noteObjCode': self.objCode}

        return comment_dict


class Task(_WorkTypeObject):
    # TODO: edit available people, name, description, status, etc... possibly change the way we do comments?

    def __init__(self, data=None, api=None, name=None, task_id=None, convert_dates=False, fields=None):
        if not data:
            data = {}
        # params = params

        super().__init__(api=api, obj_code='TASK', obj_id=task_id, name=name, data=data, convert_dates=convert_dates,
                         fields=fields)
        if name:
            self.name = name

    def accept_work(self):
        # acceptWork
        pass

    def approve_approval(self):
        # approveApproval
        pass

    def assign(self):
        # assign
        pass

    def bulk_copy(self):
        # bulkCopy
        pass

    def bulk_move(self):
        # bulkMove
        pass

    def calculate_data_extension(self):
        # calculateDataExtension
        pass

    def calculate_data_extensions(self):
        # calculateDataExtensions
        pass

    def mark_done(self):
        # markDone
        pass

    def mark_not_done(self):
        # markNotDone
        pass

    def move(self):
        # move
        pass

    def recall_approval(self):
        # recallApproval
        pass

    def reject_approval(self):
        # rejectApproval
        pass

    def reply_to_assignment(self):
        # replyToAssignment
        pass

    def unaccept_work(self):
        # unacceptWork
        pass

    def unassign(self):
        # unassign
        pass

    def unassign_occurrences(self):
        # unassignOccurrences
        pass


class Issue(_WorkTypeObject):
    # TODO: edit available people, name, description, status, etc... possibly change the way we do comments?

    def __init__(self, data=None, api=None, name=None, issue_id=None, convert_dates=False, fields=None):
        if not data:
            data = {}
        # params = params

        super().__init__(api=api, obj_code='OPTASK', obj_id=issue_id, name=name, data=data, convert_dates=convert_dates,
                         fields=fields)
        if name:
            self.name = name

    def accept_work(self):
        # acceptWork
        pass

    def approve_approval(self):
        # approveApproval
        pass

    def assign(self):
        # assign
        pass

    def calculate_data_extension(self):
        # calculateDataExtension
        pass

    def mark_done(self):
        # markDone
        pass

    def mark_not_done(self):
        # markNotDone
        pass

    def move(self):
        # move
        pass

    def move_to_task(self):
        # moveToTask
        pass


class Project(_WorkTypeObject):
    """
    Class for the project object type.
    """

    # TODO: edit available people, name, description, status, etc... possibly change the way we do comments?

    def __init__(self, data=None, api=None, name=None, proj_id=None, convert_dates=False, fields=None):
        if not data:
            data = {}
        # params = params

        super().__init__(api=api, obj_code='PROJ', obj_id=proj_id, name=name, data=data, convert_dates=convert_dates,
                         fields=fields)

        if name:
            self.name = name

    def attach_template(self, template_id,
                        fields=None,
                        predecessor_task_id=None,
                        parent_task_id=None,
                        exclude_template_task_ids=None,
                        options=None):
        """
        Attaches a template to a project with options.

        :param template_id:
        :param fields:
        :param predecessor_task_id:
        :param parent_task_id:
        :param exclude_template_task_ids:
        :param options:
        :return:
        """
        params = {'templateID': template_id,
                  'predecessorTaskID': predecessor_task_id,
                  'parentTaskID': parent_task_id,
                  'excludeTemplateTask_IDs': exclude_template_task_ids,
                  'options': options}
        return self.api.action('PROJ', 'attachTemplate', params, fields, self.ID)

    def approve_approval(self):
        # approveApproval
        pass

    # def attach_template(self):
    #     # attachTemplate
    #     pass

    def calculate_data_extension(self):
        # calculateDataExtension
        pass

    def calculate_finance(self):
        # calculateFinance
        pass

    def calculate_timeline(self):
        # calculateTimeline
        pass

    def recall_approval(self):
        # recallApproval
        pass

    def reject_approval(self):
        # rejectApproval
        pass

    def set_budget_to_schedule(self):
        # setBudgetToSchedule
        pass
