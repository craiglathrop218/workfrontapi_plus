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

import json
from workfrontapi_plus.tools import Tools


class WorkfrontObject(object):
    def __init__(self, data, api=None, obj_code=None, obj_id=None, convert_dates=False, fields=None):
        self.__dict__['api'] = api
        self.__dict__['convert_dates'] = convert_dates

        if convert_dates:
            self._convert_dates(data)

        # Set a blank list to record field changes
        self.__dict__['_dirty_fields'] = []
        self.__dict__['data'] = data

        if obj_code:
            self.__dict__['data']['objCode'] = obj_code

        if obj_id:
            self.__dict__['data']['ID'] = obj_id

        self.__dict__['fields'] = fields

    def __getattr__(self, item):
        return self.__dict__['data'][item]

    def __setattr__(self, key, value):
        if key == 'api':
            self.__dict__['api'] = value
        else:
            self._dirty_fields.append(key)
            self.data[key] = value

    def __str__(self):
        return json.dumps(self.data, indent=4)

    def _convert_dates(self, data):
        t = Tools()
        for key, item in data.items():
            if 'date' in key.lower():  # A full date will be 28 char. Avoids dates w/o time.
                try:
                    data[key] = t.parse_workfront_date(item)
                except:
                    #print('{0} could not be converted'.format(data[key]))
                    # There was a key with Date but didn't contain a Workfront formatted date.
                    pass

            if isinstance(item, dict):
                data[key] = self._convert_dates(data[key])

            if isinstance(item, list):
                for i in range(len(item)):
                    if isinstance(data[key][i], dict):
                        # Check to see if the list is a dict. Not all lists contain dicts, some are simple lists that
                        # should be skipped.
                        data[key][i] = self._convert_dates(data[key][i])
        return data

    def save(self):
        """Save updated fields

        """
        if not self.__dict__['api']:
            raise ValueError('API must be set to save.')

        '''
        Sets a params dictionary for every time there is a dirty_fields item for that entry,
        meaning there is something to put in params. sets key of this param to be key of the
        dirty_fields dict which is the field that is going to be changed.
        '''
        params = {}
        for item in self._dirty_fields:
            params[item] = self.data[item]

        # params = dict([(key, self.data[key])
        #                 for key, val in self._dirty_fields.items() if val])

        # params = dict(self.data)
        if not len(params):
            raise ValueError("No parameters were modified.")

        # Get the fields if not set during import
        local_fields = list(self.data.keys()) if not self.fields else self.fields

        if self.data['ID']:
            res = self.__dict__['api'].put(self.objCode, self.data['ID'], params, local_fields)

        else:
            res = self.__dict__['api'].post(self.objCode, params, list(self.data.keys()))

        if self.__dict__['convert_dates']:
            self._convert_dates(res)

        self.__dict__['data'] = res
        self.__dict__['_dirty_fields'] = []

        return res

    def delete(self, force=False):
        """ Deletes the current object by id

        """
        if not self.__dict__['api']:
            raise ValueError('API must be set to save.')
        return self.__dict__['api'].delete(self.objCode, self.ID, force)

    def share(self, user_ids, level='view'):
        return self.__dict__['api'].share_obj(self.objCode, self.ID, user_ids, level)

    def get_share(self):
        return self.__dict__['api'].get_


class WorkfrontAPIException(Exception):
    """Raised when a _request fails with error

    """

    def __init__(self, error_msg):
        super().__init__(error_msg)
