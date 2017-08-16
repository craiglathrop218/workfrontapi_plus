import requests
import math
import json

# CRUD wrapper for basic modifications
class WorkfrontObject(object):
    def __init__(self, data, api=None, objCode=None, ID=None):
        self.__dict__['api'] = api
        self.__dict__['_dirty_fields'] = []
        self.__dict__['data'] = data

        if objCode:
            self.__dict__['data']['objCode'] = objCode

        if ID:
            self.__dict__['data']['ID'] = ID



    def __getattr__(self, item):
        return self.__dict__['data'][item]

    def __setattr__(self, key, value):
        self._dirty_fields.append(key)
        self.data[key] = value

    def __str__(self):
        return json.dumps(self.data, indent=4)

    def save(self):
        """
        Persists changes to streamclient instance
        raises -- StreamClientNotSet if stream client was not passed in constructor
               -- StreamNotModifiedException if no fields have changed
               -- StreamAPIException if api call fails
        """
        if not self.api:
            raise StreamClientNotSet()

        '''
        Sets a params dictionary for every time there is a dirty_fields item for that entry,
        meaning there is something to put in params. sets key of this param to be key of the
        dirty_fields dict which is the field that is going to be changed
        '''
        params = {}
        for item in self._dirty_fields:
            params[item] = self.data[item]


        # params = dict([(key, self.data[key])
        #                 for key, val in self._dirty_fields.items() if val])

        #params = dict(self.data)
        if not len(params):
            raise StreamNotModifiedException("No fields were modified.")

        if self.data['ID']:
            res = self.api.put(self.objCode, self.ID, params, list(self.data.keys()))

        else:
            res = self.api.post(self.objCode, params, list(self.data.keys()))

        self.__dict__['data'] = res
        self.__dict__['_dirty_fields'] = []

    def delete(self, streamclient, force=False):
        """
        Deletes the current object by id
        raises -- StreamClientNotSet if stream client was not passed in constructor
        """
        if not self.streamclient:
            raise StreamClientNotSet()
        return self.streamclient.delete(self.objCode, self.ID, force)

    def share(self,user_ids, level='view'):
        return self.api.share_obj(self.objCode, self.ID, user_ids, level)


    def get_share(self):
        return self.api.get_

class WorkfrontAPIException(Exception):
    """Raised when a _request fails"""

    def __init__(self, error_msg):
        super().__init__(error_msg)

class StreamNotModifiedException(Exception):
    "Raised when saving an object that has not been modified"

class StreamClientNotSet(Exception):
    """Raised when calling an api method on an object without an
    attached StreamClient object
    """