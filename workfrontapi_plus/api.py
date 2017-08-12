"""
Copyright (c) 2017 Craig Lathrop & Roshan Bal

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
"""

#  Original copyright notice from Workfront Version of this API
#
#  Copyright (c) 2010 AtTask, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
#  documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import codecs, requests, json, math

import urllib.error
import urllib.parse
import urllib.request



class Workfront(object):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

    LOGIN_PATH = "/login"
    LOGOUT_PATH = "/logout"

    CORE_URL = "https://{subdomain}.{env}.workfront.com/attask/api/v{version}"

    def __init__(self, subdomain, env, api_version='7.0', api_key=None, session_id=None, user_id=None, debug=False,
                 test_mode=False):
        """
        Setup class
        
        :param subdomain: The sub domain for your account
        :param env: {'live', 'sandbox', or 'preview'} default 'sandbox'
        :param api_version: The full version number for the API. Example '7.0'. Default 7.0
        :param api_key: The API key for authentication. Default None.
        :param session_id: An optional session ID for authentication
        :param user_id: The ID of the authenticated user
        """
        self.subdomain = subdomain
        api_base_url = self.CORE_URL.format(subdomain=subdomain,
                                            env=env,
                                            version=api_version)

        self.api_base_url = api_base_url
        self.session_id = session_id
        self.user_id = user_id
        self.api_key = api_key
        self.debug = debug
        self.test_mode = test_mode

        # These methods are set as class variables to enable easy re-assignment during unit testing.
        # These values are typically overwritten by the unit tests with a lambda function simulating the results
        # of the method.
        self._request = self._make_request
        self._count = self.count
        self._open_api_connection = self._p_open_api_connection

    @staticmethod
    def test_mode_make_request(*args):
        return args

    def login(self, username, password=None):
        """
        Login to Workfront using username and optionally password.
        
        This method will make a login _request and set the lession ID.
        
        If an API key is set the password is not needed. The resulting sessionID
        will allow you to act on behalf of a user.

        https://developers.workfront.com/api-docs/#Login

        :param username: The Workfront username, typically an email address
        :param password: The Workfront password
        :return: The results of the login.
        """
        params = {'username': username}
        if password:
            params['password'] = password

        data = self._request(self.LOGIN_PATH, params, self.GET)

        if 'sessionID' in data:
            self.session_id = data['sessionID']
            self.user_id = data['userID']
            # Just a short cut here. Return script looks for 2.
            return data
        else:
            return data

    def logout(self):
        """
        Logout method.

        Clears the class session_id and user_id fields.
        """
        self._request(self.LOGOUT_PATH, None, self.GET)
        self.session_id = None
        self.user_id = None

    def get_list(self, objcode, ids, fields=None):
        """
        Returns each object by id, similar to calling get for each id individually

        :param objcode: object type (i.e. 'PROJECT')
        :param ids: list of ids to lookup
        :param fields: list of field names to return for each object
        :return: Data from Workfront
        """
        path = '/{0}'.format(objcode)
        return self._request(path, {'ids': ','.join(ids)}, fields)

    def put(self, objcode, objid, params, fields=None):
        """
        Updates an existing object, returns the updated object.

        https://developers.workfront.com/api-docs/#PUT

        :param objcode: object type (i.e. 'PROJECT')
        :param objid: The ID of the object to act on
        :param params: A dict of parameters to filter on
        :param fields: List of field names to return for each object
        :return: Data from Workfront
        """
        path = '/{0}/{1}'.format(objcode, objid)
        return self._request(path, params, self.PUT, fields)

    def action(self, objcode, action, params, fields=None, objid=None):
        """
        Updates an existing object, returns the updated object
        :param objcode: object type (i.e. 'PROJECT')
        :param objid: Object ID to operate on
        :param action: action to execute
        :param params: A dict of parameters to filter on
        :param fields: A list of fields to return - Optional
        """
        if objid:
            path = '/{objcode}/{objid}'.format(objcode=objcode, objid=objid, action=action)
        else:  # for some bulk operations you don't want to pass an obj ID in
            path = '/{objcode}'.format(objcode=objcode, action=action)

        params['action'] = action

        return self._request(path, params, self.PUT, fields)

    def _bulk_segmenter(self, bulk_method, **kwargs):
        """
        Breaks a list of items up into chunks of 100 for processing.

        :param bulk_method: An instance of the method (self.bulk, self.bulk_delete, self.bulk_create)
        :param kwargs: The various parameters
        :return: The output of the update from API
        """
        output = []
        if 'updates' in kwargs:
            data = kwargs['updates']
            key = 'updates'

        else:
            data = kwargs['objids']
            key = 'objids'
        for i in range(0, len(data), 100):
            sliced_update_list = list(data[i:i + 100])
            kwargs[key] = sliced_update_list
            output += bulk_method(**kwargs)

        return output

    def bulk(self, objcode, updates, fields=None):
        """
        Makes bulk updates to existing objects
        :param objcode: object type (i.e. 'PROJECT')
        :param updates: A list of dicts contining the updates
        :param fields: A list of fields to return - Optional
        :return: The results of the _request as a list of updated objects
        """

        if len(updates) > 100:
            res = self._bulk_segmenter(self.bulk, objcode=objcode, updates=updates, fields=fields)
            return res
        path = '/{0}'.format(objcode)
        params = {'updates': updates}
        return self._request(path, params, self.PUT, fields)

    def bulk_create(self, objcode, updates, fields=None):
        """
        Bulk creation of objects such as tasks, issues, other.

        This method differs from bulk in that it uses the POST operation, not PUT
        :param objcode: object type (i.e. 'PROJECT')
        :param updates: A list of dicts containing the updates
        :param fields: List of field names to return for each object
        :return: The results of the _request as a list of newly created objects
        """
        if len(updates) > 100:
            res = self._bulk_segmenter(self.bulk_create, objcode=objcode, updates=updates, fields=fields)
            return res
        path = '/{0}'.format(objcode)
        params = {'updates': updates}
        return self._request(path, params, self.POST, fields)

    def post(self, objcode, params, fields=None):
        """
        Creates a new object, returns the new object

        https://developers.workfront.com/api-docs/#POST

        :param objcode: object type (i.e. 'PROJECT')
        :param params: A dict of parameters to filter on.
        :param fields: List of field names to return for each object.
        :return: The results of the updated object.
        """
        path = '/{0}'.format(objcode)
        return self._request(path, params, self.POST, fields)

    def get(self, objcode, objid, fields=None):
        """
        Lookup an object by id

        :param objcode: object type (i.e. 'PROJECT')
        :param objid: Object ID to operate on
        :param fields:
        :return: The requested object with requested fields
        """
        path = '/{0}/{1}'.format(objcode, objid)
        return self._request(path, None, self.GET, fields)

    def delete(self, objcode, objid, force=True):
        """
        Delete by object ID

        :param objcode: object type (i.e. 'PROJECT')
        :param objid: Object ID to operate on
        :param force: Force deletion of the object with relationships. For example
                      if a task is deleted with force "False" associated expenses will
                      not be removed.
        :return: The results of the deletion
        """
        path = '/{0}/{1}'.format(objcode, objid)
        return self._request(path, {'force': force}, self.DELETE)

    def bulk_delete(self, objcode, objids, force=True, atomic=True):
        """
        Delete by object ID

        :param objcode: object type (i.e. 'PROJECT')
        :param objids: A list of object IDs to be deleted
        :param force: True by default. Force deletion of the object with relationships. For example
                      if a task is deleted with force "False" associated expenses will
                      not be removed.
        :param atomic: True by default. Removes all objects at the same time. This is useful is situations where you might be deleting
                       a parent object with children in the same set of "ids". For example:

                       Task A
                            Task B
                            Task C

                       If in the above example you delete Task A, Task B and C will be deleted automatically. If you do
                       not specify atomic=True and the ID's for Task B and C are in the list of ID's to be deleted it
                       will throw an error as it will not be able to find those ID's.
        :return: The results of the deletion
        """
        if len(objids) > 100:
            res = self._bulk_segmenter(self.bulk_delete, objcode=objcode, objids=objids, force=True, atomic=True)
            return res
        path = '/{0}'.format(objcode)

        params = {"ID": objids, "force": force}
        if atomic:
            params['atomic'] = 'true'
        return self._request(path, params, self.DELETE)

    def search(self, objcode, params, fields=None, get_all=False, limit=None):
        """
        Search for objects against a given set of filters (params).

        :param objcode: Object code to search for.
        :param params:
        :param fields:
        :return:
        """
        path = '/{0}/search'.format(objcode)
        if get_all or limit:
            max_limit = 500
            output = []
            first = 0
            count = self._count(objcode, params)
            if limit:
                count = count if count < limit else limit
                limit = max_limit if limit > max_limit else limit
            else:
                limit = max_limit
            loop_count = int(math.ceil(count / max_limit))
            params['$$LIMIT'] = limit
            for i in range(0, loop_count):
                if i == (loop_count - 1):
                    params['$$LIMIT'] = count - ((loop_count - 1) * limit)
                params['$$FIRST'] = first
                res = self._request(path, params, self.GET, fields)
                output += res
                first += limit
            return output

        return self._request(path, params, self.GET, fields)

    def count(self, objcode, params):
        """
        Count objects for a given set of filters (params).

        :param objcode: Object code to count.
        :param params:  Dict of criteria to use as filter
                        {'name': 'example task',
                         'name_Mod: 'cicontains'}
        :return:
        """

        path = '/{0}/count'.format(objcode)
        return self._request(path, params, self.GET)['count']

    def report(self, objcode, params, agg_field, agg_func, group_by_field=None, rollup=False):
        """
        Create aggregate reports.

        This method will return an aggregate for the fields specified in an object. For example:

        objcode = 'TASK', agg_func='duration'
        {
            "data": {
                "durationMinutes": 24468636,
                "dcount_ID": 3062
            }
        }

        :param objcode: Object type
        :param params:  Dict of criteria to use as filter
                        {'name': 'example task',
                         'name_Mod: 'cicontains'}

        :param agg_field: The field to aggregate on.
        :param agg_func: Type of function (sum, avg, etc)
        :param group_by_field: Group results by this field

                        "data": {
                            "Project 1": {
                                "durationMinutes": 24000,
                                "dcount_ID": 4,
                                "project_name": "Project 1"
                            },
                            "Project 2": {
                                "durationMinutes": 3360,
                                "dcount_ID": 1,
                                "project_name": "Project 1"
                            }
                        }

        :param rollup: Flag to indicate a roll-up of all groupings.

                        "data": {
                            "Project 1": {
                                "durationMinutes": 24000,
                                "dcount_ID": 4,
                                "project_name": "Project 1"
                            },
                            "Project 2": {
                                "durationMinutes": 3360,
                                "dcount_ID": 1,
                                "project_name": "Project 1"
                            },
                            "$$ROLLUP": {
                                "durationMinutes": 27600,
                                "dcount_ID": 5
                            }

        :return: dict with the results
        """

        path = "/{objCode}/report".format(objCode=objcode)

        if group_by_field:
            gb_key = "{field}_1_GroupBy".format(field=group_by_field)
            params[gb_key] = True

        if rollup:
            params['$$ROLLUP'] = True

        agg_key = '{field}_AggFunc'.format(field=agg_field)
        params[agg_key] = agg_func

        return self._request(path, params, self.GET)

    def make_update_as_user(self, user_email, exec_method, objcode, params, objid=None, action=None, objids=None,
                            fields=None, logout=False):
        """
        Performs an action on behalf of another user.

        This method will login on behalf of another user by passing in the users ID (email) and the API key to the login
        method. This will set a session ID. While the session ID is set all actions performed or taken will show as if
        done by the users.

        This is useful for script that might need to write updates on behalf of a user, change a commit date, or
        perform other operations that can only be done by a task assignee or owner.
        :param user_email: The email address of the users to act on behalf of
        :param exec_method: Method within Workfront class to execute on behalf of user
                            Options: ('post', 'put', 'action', 'search')
        :param action: Action to take ('post', 'put', 'action', 'search', 'report', 'bulk')
        :param objcode: The object code to act on
        :param params: A list of parameters
        :param objid: Optional. Object ID to act on. This is required for put, and certain action commands.
        :param objids: Optional. Object ID list to act on. This is required for bulk commands.
        :param fields: Optional. List of fields to return
        :return: The results of the query
        """
        res = self.login(user_email)

        commands = {'post': self.post,
                    'put': self.put,
                    'action': self.action,
                    'search': self.search,
                    'report': self.report,
                    'bulk': self.bulk}

        if res:
            if exec_method == 'post':
                return self.post(objcode, params, fields)

            elif exec_method == 'put':
                if objid:
                    return self.put(objcode, objid, params, fields)
                else:
                    raise ValueError('Must Pass object id if using put method')

            elif exec_method == 'action':
                if action:
                    return self.action(objcode, action, params, fields, objid)
                else:
                    raise ValueError('Must Pass action parameter if calling action method')

            elif exec_method == 'search':
                return self.search(objcode, params, fields)

            else:
                raise ValueError('Login failed. No Session ID')
        else:
            raise ValueError('Login Failed')

    @staticmethod
    def _parse_parameter_lists(params):
        """
        Searches params and converts lists to comma sep strings

        The workfront API will reject the ['something','somethingelse'] format if sent as a parameter value. This
        method looks through the params for lists and converts them to simple comma separated values in a string. For
        example.

        {'status': ['CUR', 'PLN', 'APP'],
         'status_Mod': 'in'}

         will be converted to

        {'status': 'CUR',
         'status': 'PLN',
         'status': 'APP',
         'status_Mod': 'in'}

        :param params: A dict of the filter parameters
        :return: The filters params converted to a string
        """
        output_string = ""

        for key, value in params.items():
            if isinstance(value, list):
                # Convert list to multiple instances of same key.
                # Sort to make unit testing easier
                value = sorted(value)
                for list_item in value:
                    output_string = "{output_string}&{key}={value}".format(output_string=output_string,
                                                                           key=key, value=list_item)
            else:
                output_string = "{output_string}&{key}={value}".format(output_string=output_string, key=key,
                                                                       value=value)
        # There will be an & on the far left. Strip that off
        return output_string[1:]

    def _make_request(self, path, params, method, fields=None, raw=False):
        """
        Makes the request to Workfront API

        :param path: The API Path (i.e. http://domain.my.workfront.com/attask/api/v7.0/{action}/{obj})
        :param params: A dict of filter parameters
        :param method: The method (GET, POST, DELETE, PUT)
        :param fields: A list of fields to return
        :param raw: Flag to return data exactly as provided by API. The practical effect of this flag is to return
                    the value of the "data" key when set to False and the whole object when set to true. Example:

                    raw = True:
                    {'data': [{'ID':'ACB123...',
                               'name': 'proj 1'},
                               {'ID':'ACB156...',
                               'name': 'proj 2'}]
                    }

                    raw = False:
                    [{'ID':'ACB123...',
                     'name': 'proj 1'},
                     {'ID':'ACB156...',
                     'name': 'proj 2'}]

        :return: The query results
        """
        api_param_string = self._prepare_params(method, params, fields)

        api_path = self.api_base_url + path
        data = self._open_api_connection(api_param_string, api_path)

        return data if raw else data['data']

    def _p_open_api_connection(self, data, dest):
        """
        Makes the request to the Workfront API

        :param data: The URL parameters string
        :param dest: API URL
        :return: json results of query
        """
        try:
            response = requests.get(dest, data)
        except requests.exceptions.RequestException as e:
            raise WorkfrontAPIException(e)
        return response.json()

    def _prepare_params(self, method, params, fields):

        # If no params passed in set a blank dict.
        params = params if params else {}
        params['method'] = method
        params = self._set_authentication(params)

        if fields:
            params['fields'] = ','.join(fields)

        if method == self.GET and params:
            params = self._parse_parameter_lists(params)
            data = urllib.parse.quote(params, '&=')
        else:
            data = urllib.parse.urlencode(params)
        # @todo Check if we need to convert to ascii here. Might be able to just return data.
        #return data.encode('ascii')
        return data

    def _set_authentication(self, params):
        """
        Adds the authentication into params.

        :param params:
        :return:
        """
        # Added a check to see if a session ID is being used instead of API Key - CL 8/4
        if self.session_id:
            params['sessionID'] = self.session_id
        elif self.api_key:
            params['apiKey'] = self.api_key
        else:
            raise ValueError("No valid authentication method provided. You must set either a sessionID or API Key.")

        return params


class WorkfrontAPIException(Exception):
    """Raised when a _request fails"""

    def __init__(self, errors):
        error_msg = errors.read().decode("utf8", 'ignore')
        error_msg_decode = json.loads(error_msg)
        message = error_msg_decode['error']['message']
        super().__init__(message)


class ObjCode:
    """
    Constants for Workfront objCode's
    """
    PROJECT = 'proj'
    TASK = 'task'
    ISSUE = 'optask'
    TEAM = 'team'
    HOUR = 'hour'
    TIMESHEET = 'tshet'
    USER = 'user'
    ASSIGNMENT = 'assgn'
    USER_PREF = 'userpf'
    CATEGORY = 'ctgy'
    CATEGORY_PARAMETER = 'ctgypa'
    PARAMETER = 'param'
    PARAMETER_GROUP = 'pgrp'
    PARAMETER_OPTION = 'popt'
    PARAMETER_VALUE = 'pval'
    ROLE = 'role'
    GROUP = 'group'
    NOTE = 'note'
    DOCUMENT = 'docu'
    DOCUMENT_VERSION = 'docv'
    EXPENSE = 'expns'
    CUSTOM_ENUM = 'custem'
    PROGRAM = 'prgm'
