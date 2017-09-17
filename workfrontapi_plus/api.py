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

# https://blog.jetbrains.com/pycharm/2017/05/how-to-publish-your-package-on-pypi/

import json
import math

import requests

from workfrontapi_plus.core_wf_object import WorkfrontAPIException


class Api(object):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'

    LOGIN_PATH = "/login"
    LOGOUT_PATH = "/logout"

    # OBJCODES = ObjCode()

    CORE_URL = "https://{subdomain}.{env}.workfront.com/attask/api/v{version}"

    def __init__(self, subdomain, env, api_version='7.0', api_key=None, session_id=None, user_id=None,
                 return_api_errors=False,
                 debug=False,
                 ):
        """Setup class

        :param subdomain: The sub domain for your account
        :param env: {'live', 'sandbox', or 'preview'} default 'sandbox'
        :param api_version: The full version number for the API. Example '7.0'. Default 7.0
        :param api_key: The API key for authentication. Default None.
        :param session_id: An optional session ID for authentication
        :param user_id: The ID of the authenticated user
        :param return_api_errors: In the event that the API generates an error the Workfront API message will be
        returned instead of raising an error
        :param debug: Sets API into debugging mode.
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
        self.return_api_errors = return_api_errors
        self._max_bulk = 99
        self._max_results = 2000

        # These methods are set as class variables to enable easy re-assignment during unit testing.
        # These values are typically overwritten by the unit tests with a lambda function simulating the results
        # of the method.
        self._request = self._make_request
        self._count = self.count
        self._open_api_connection = self._p_open_api_connection
        self._upload_file = self._request_upload_file

    @staticmethod
    def test_mode_make_request(*args):
        return args

    def login(self, username, password=None):
        """Login to Workfront using username and optionally password.
        
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

        # Login method required to use POST
        data = self._request(self.LOGIN_PATH, params, self.POST)

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

        :return: The results of the logout request
        """
        res = self._request(self.LOGOUT_PATH, None, self.GET)
        self.session_id = None
        self.user_id = None
        return res

    def get_list(self, obj_code, ids, fields=None):
        """Returns each object by id, similar to calling get for each id individually

        :param obj_code: object type (i.e. 'PROJECT')
        :param ids: list of ids to lookup
        :param fields: list of field names to return for each object
        :return: Data from Workfront

        """
        path = '/{0}'.format(obj_code)
        return self._request(path, {'id': ','.join(ids)}, self.GET, fields)

    def put(self, obj_code, obj_id, params, fields=None):
        """Updates an existing object, returns the updated object.

        https://developers.workfront.com/api-docs/#PUT

        :param obj_code: object type (i.e. 'PROJECT')
        :param obj_id: The ID of the object to act on
        :param params: A dict of parameters to filter on
        :param fields: List of field names to return for each object
        :return: Data from Workfront

        """
        path = '/{0}/{1}'.format(obj_code, obj_id)
        # The requests package has a problem with nested lists in JSON. We just pre-convert this to
        # JSON to avoid.
        params = {'updates': json.dumps(params)}
        return self._request(path, params, self.PUT, fields)

    def action(self, obj_code, action, params, fields=None, obj_id=None):
        """Updates an existing object, returns the updated object
        :param obj_code: object type (i.e. 'PROJECT')
        :param obj_id: Object ID to operate on
        :param action: action to execute
        :param params: A dict of parameters to filter on
        :param fields: A list of fields to return - Optional

        """
        if obj_id:
            path = '/{obj_code}/{objid}'.format(obj_code=obj_code, objid=obj_id, action=action)
        else:  # for some bulk operations you don't want to pass an obj ID in
            path = '/{obj_code}'.format(obj_code=obj_code, action=action)

        params['action'] = action

        return self._request(path, params, self.PUT, fields)

    def bulk(self, obj_code, updates, fields=None):
        """Makes bulk updates to existing objects

        :param obj_code: object type (i.e. 'PROJECT')
        :param updates: A list of dicts contining the updates
        :param fields: A list of fields to return - Optional
        :return: The results of the _request as a list of updated objects

        """
        if len(updates) > self._max_bulk:
            res = self._bulk_segmenter(self.bulk,
                                       objs_per_loop=self._max_bulk,
                                       obj_code=obj_code,
                                       updates=updates,
                                       fields=fields)
            return res
        path = '/{0}'.format(obj_code)
        params = {'updates': json.dumps(updates)}

        return self._request(path, params, self.PUT, fields)

    def bulk_create(self, obj_code, updates, fields=None):
        """Bulk creation of objects such as tasks, issues, other.

        This method differs from bulk in that it uses the POST operation, not PUT
        :param obj_code: object type (i.e. 'PROJECT')
        :param updates: A list of dicts containing the updates
        :param fields: List of field names to return for each object
        :return: The results of the _request as a list of newly created objects

        """
        # max_objs_per_loop = self._get_max_update_obj_size(updates)

        if len(updates) > self._max_bulk:
            res = self._bulk_segmenter(self.bulk_create,
                                       objs_per_loop=self._max_bulk,
                                       obj_code=obj_code,
                                       updates=updates,
                                       fields=fields)
            return res
        path = '/{0}'.format(obj_code)
        params = {'updates': json.dumps(updates)}
        return self._request(path, params, self.POST, fields)

    def post(self, obj_code, params, fields=None):
        """Creates a new object, returns the new object

        https://developers.workfront.com/api-docs/#POST

        :param obj_code: object type (i.e. 'PROJECT')
        :param params: A dict of parameters to filter on.
        :param fields: List of field names to return for each object.
        :return: The results of the updated object.

        """
        path = '/{0}'.format(obj_code)
        # The requests package has a problem with nested lists in JSON. We just pre-convert this to
        # JSON to avoid. While this is less common in a post operation, it is the only way to tag users in
        # a new note (as example).
        params = {'updates': json.dumps(params)}

        return self._request(path, params, self.POST, fields)

    def get(self, obj_code, obj_id, fields=None):
        """Lookup an single object by id

        :param obj_code: object type (i.e. 'PROJECT')
        :param obj_id: Object ID to operate on
        :param fields:
        :return: The requested object with requested fields

        """
        path = '/{0}/{1}'.format(obj_code, obj_id)
        return self._request(path, None, self.GET, fields)

    def delete(self, obj_code, obj_id, force=True):
        """Delete an object by ID

        :param obj_code: object type (i.e. 'PROJECT')
        :param obj_id: Object ID to operate on
        :param force: Force deletion of the object with relationships. For example
                      if a task is deleted with force "False" associated expenses will
                      not be removed.
        :return: The results of the deletion

        """
        path = '/{0}/{1}'.format(obj_code, obj_id)
        return self._request(path, {'force': force}, self.DELETE)

    def bulk_delete(self, obj_code, obj_ids, force=True, atomic=True):
        """Delete by object ID

        :param obj_code: object type (i.e. 'PROJECT')
        :param obj_ids: A list of object IDs to be deleted
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
        res = []
        if len(obj_ids) > self._max_bulk:
            res = self._bulk_segmenter(self.bulk_delete,
                                       objs_per_loop=self._max_bulk,
                                       obj_code=obj_code,
                                       obj_ids=obj_ids,
                                       force=True,
                                       atomic=True)
            return res
        path = '/{0}'.format(obj_code)

        params = {"ID": obj_ids, "force": force}
        if atomic:
            params['atomic'] = 'true'
        return self._request(path, params, self.DELETE)

    def search(self, obj_code, params, fields=None, get_all=False, limit=None):
        """Search for objects against a given set of filters (params).

        :param obj_code: Object code to search for.
        :param params: Search parameters
        :param fields: List of fields to search for
        :param get_all: The get_all flag will return all search results, looping as many times as
                        necessary to return all results.
        :param limit:
        :return:

        """
        path = '/{0}/search'.format(obj_code)
        if get_all or limit:
            output = []
            first = 0
            count = self._count(obj_code, params)
            if limit:
                count = count if count < limit else limit
                limit = self._max_results if limit > self._max_results else limit
            else:
                limit = self._max_results
            loop_count = int(math.ceil(count / self._max_results))
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

    def count(self, obj_code, params):
        """Count objects for a given set of filters (params).

        :param obj_code: Object code to count.
        :param params:  Dict of criteria to use as filter
                        {'name': 'example task',
                         'name_Mod: 'cicontains'}
        :return:

        """

        path = '/{0}/count'.format(obj_code)
        return self._request(path, params, self.GET)['count']

    def report(self, obj_code, params, agg_field, agg_func, group_by_field=None, rollup=False):
        """Create aggregate reports.

        This method will return an aggregate for the fields specified in an object. For example:

        obj_code = 'TASK', agg_func='duration'
        {
            "data": {
                "durationMinutes": 24468636,
                "dcount_ID": 3062
            }
        }

        :param obj_code: Object type
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

        path = "/{objCode}/report".format(objCode=obj_code)

        if group_by_field:
            gb_key = "{field}_1_GroupBy".format(field=group_by_field)
            params[gb_key] = True

        if rollup:
            params['$$ROLLUP'] = True

        agg_key = '{field}_AggFunc'.format(field=agg_field)
        params[agg_key] = agg_func

        return self._request(path, params, self.GET)

    def upload_document(self, file, name, obj_code, obj_id, version=1):
        handle = self.make_document(file, obj_code, obj_id, version)
        post_doc = self.post_document(name, handle, obj_code, obj_id, version)

    def make_document(self, file, obj_code, obj_id, version=1):
        path = "/upload"
        handle = self._upload_file(file, path)
        return handle

    def post_document(self, name, handle, obj_code, obj_id, version):
        updates = {'name': name,
                   'handle': handle,
                   'docObjCode': obj_code,
                   'objID': obj_id
                   # 'currentVersion': "{'version':'v1.0','fileName':name}"
                   }

        return self.post('docu', updates)

    def make_update_as_user(self, user_email, exec_method, obj_code, params, obj_id=None, action=None, obj_ids=None,
                            fields=None, logout=False):
        """Performs an action on behalf of another user.

        This method will login on behalf of another user by passing in the users ID (email) and the API key to the login
        method. This will set a session ID. While the session ID is set all actions performed or taken will show as if
        done by the users.

        This is useful for script that might need to write updates on behalf of a user, change a commit date, or
        perform other operations that can only be done by a task assignee or owner.
        :param user_email: The email address of the users to act on behalf of
        :param exec_method: Method within Workfront class to execute on behalf of user
                            Options: ('post', 'put', 'action', 'search')
        :param action: Action to take ('post', 'put', 'action', 'search', 'report', 'bulk')
        :param obj_code: The object code to act on
        :param params: A list of parameters
        :param obj_id: Optional. Object ID to act on. This is required for put, and certain action commands.
        :param obj_ids: Optional. Object ID list to act on. This is required for bulk commands.
        :param fields: Optional. List of fields to return
        :return: The results of the query

        """
        login_res = self.login(user_email)

        # commands = {'post': self.post,
        #             'put': self.put,
        #             'action': self.action,
        #             'search': self.search,
        #             'report': self.report,
        #             'bulk': self.bulk}

        if login_res:
            if exec_method == 'post':
                res = self.post(obj_code, params, fields)
                if logout:
                    self.logout()
                return res

            elif exec_method == 'put':
                if obj_id:
                    res = self.put(obj_code, obj_id, params, fields)
                    if logout:
                        self.logout()
                    return res
                else:
                    raise ValueError('Must Pass object id if using put method')

            elif exec_method == 'action':
                if action:
                    res = self.action(obj_code, action, params, fields, obj_id)
                    if logout:
                        self.logout()
                    return res
                else:
                    raise ValueError('Must Pass action parameter if calling action method')

            elif exec_method == 'search':
                res = self.search(obj_code, params, fields)
                if logout:
                    self.logout()
                return res

            else:
                raise ValueError('Login failed. No Session ID')
        else:
            raise ValueError('Login Failed')

    def share_obj(self, obj_code, obj_id, accessor_id, accessor_obj_code, level):
        """Sets sharing levels for an object with one or more ID numbers

        :param obj_code:
        :param obj_id:
        :param ids:
        :param accessor_obj_code:
        :param level:
        :return:
        """
        path = '/{0}/{1}/share'.format(obj_code, obj_id)


        access_levels = {'view': 'VIEW', 'contribute': 'CREATE', 'manage': 'DELETE'}

        params = {'accessorID': accessor_id,
                  'accessorObjCode': accessor_obj_code,
                  'coreAction': access_levels[level]}

        return self._request(path, params, self.PUT)

    def get_obj_share(self, obj_code, obj_id):
        # @todo finish and document this section
        pass

    @staticmethod
    def _parse_parameter_lists(params):
        """Searches params and converts lists to comma sep strings

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
                for list_item in value:
                    output_string = "{output_string}&{key}={value}".format(output_string=output_string,
                                                                           key=key, value=list_item)
            else:
                output_string = "{output_string}&{key}={value}".format(output_string=output_string, key=key,
                                                                       value=value)
        # There will be an & on the far left. Strip that off
        return output_string[1:]

    @staticmethod
    def _parse_post_param_list(params):
        output_string = ""

        if 'apiKey' in params:
            api_string = '&apiKey=' + params['apiKey']
        params.pop('apiKey', None)
        output_string += "updates=" + str(params) + '&method=post' + api_string
        return output_string

    def _make_request(self, path, params, method, fields=None, raw=False):
        """Makes the request to Workfront API

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
        api_param_string = self._prepare_params(method, params, fields, path)

        api_path = self.api_base_url + path
        data = self._open_api_connection(api_param_string, api_path)

        if 'data' in data:
            return data if raw else data['data']
        elif 'error' in data:
            # This condition will occur if there is an error being returned.
            return data['error']['message']
        else:
            raise WorkfrontAPIException(data)

    def _p_open_api_connection(self, data, dest):
        """Makes the request to the Workfront API

        :param data: The URL parameters string
        :param dest: API URL
        :return: json results of query

        """
        try:
            # Request should default ambiguous as WF_API+ should handle methods (GET, POST etc.)

            # FIXME: Breaking changes now require type-check. Type-check should be refactored out
            if isinstance(data, dict) and 'method' in data:
                response = requests.request(data['method'], dest, params=data)
            else:
                # Use requests.get as fallback
                response = requests.get(dest, data)
        except requests.exceptions.HTTPError as e:
            msg = e.response
            raise WorkfrontAPIException(e)

        if response.ok:
            if self.debug: print('Response OK - 200. Len of full URL was ', len(response.url), ' char.')
            return response.json()
        else:
            if self.return_api_errors:
                if self.debug: print('Response OK - 200. Len of full URL was ', len(response.url), ' char.')
                return response.json()
            else:
                raise WorkfrontAPIException(response.text)

    def _request_upload_file(self, file, url):
        api_path = self.api_base_url + "/upload"
        data = self._p_upload_file(file, api_path)
        return data['data']['handle']

    def _p_upload_file(self, file, url):
        file = {'uploadedFile': file}
        params = {}
        params = self._set_authentication(params)
        # r = requests.post(url, files=params, apiKey = '1q2tz2xgsgf2y44mvz78vxn1y0jhqc7h')
        r = requests.request('post', url, files=file, params=params)
        return r.json()

    def _prepare_params(self, method, params, fields, path):

        # If no params passed in set a blank dict.
        params = params if params else {}

        params['method'] = method

        # Check that fields exist before attempting join to avoid error.
        if fields:
            params['fields'] = ','.join(fields)

        # If the request is login must bypass authentication
        if path is not '/login' and 'password' not in params:
            params = self._set_authentication(params)

        # Must come after method/login checks, otherwise: AttributeError: 'str' object has no attribute 'keys'
        if method == self.GET and params:
            params = self._parse_parameter_lists(params)

        # if method == self.PUT and params:
        #     params = self._parse_parameter_lists(params)
        # @todo Check if we need to convert to ascii here. Might be able to just return data.

        # if method == 'POST':
        #     params = self._parse_post_param_list(params)
        return params

    def _set_authentication(self, params):
        """Adds the authentication into params.

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

    @staticmethod
    def _bulk_segmenter(bulk_method, objs_per_loop, **kwargs):
        """Breaks a list of items up into chunks for processing.

        :param bulk_method: An instance of the method (self.bulk, self.bulk_delete, self.bulk_create)
        :param kwargs: The various parameters
        :return: The output of the update from API

        """
        output = []
        if 'updates' in kwargs:
            data = kwargs['updates']
            key = 'updates'
        else:
            data = kwargs['obj_ids']
            key = 'obj_ids'
        for i in range(0, len(data), objs_per_loop):
            sliced_update_list = list(data[i:i + objs_per_loop])
            kwargs[key] = sliced_update_list
            output += bulk_method(**kwargs)

        return output

        # def _get_max_update_obj_size(self, updates):
        #     """Gets the total len of the updates when converted to JSON.
        #
        #     There appears to be a char limit of ~6800 when making a bulk request. This seems related to total
        #     char len only, not number of elements.
        #
        #     This method checks the size of the JSON converted "updates" and calculates a safe self._max_bulk
        #     value.
        #     :param updates: A dict containing updates
        #     :return: A safe value for self._max_bulk
        #
        #     """
        #     # Actual limit seems to be ~6894 but errors are seen sometime at numbers down to 5000. It's possible that
        #     # the problem is not related to overall char size, but is something to do with some other field length or
        #     # attempting to add or modify so many objects at once. This issue isn't well understood at the moment.
        #     api_char_limit = 3000
        #     updates_len = len(updates)
        #     json_len = len(json.dumps(updates))
        #     char_per_update_element = int(math.ceil(json_len / updates_len))
        #     safe_elements_per_loop = int(math.floor(api_char_limit / char_per_update_element))
        #     print('Safe number of update elements per loop is {0}'.format(safe_elements_per_loop))
        #     return safe_elements_per_loop if safe_elements_per_loop < self._max_bulk else self._max_bulk
