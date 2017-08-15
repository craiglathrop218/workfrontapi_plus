import requests
import math
import json

# CRUD wrapper for basic modifications
class WorkfrontObject(object):
    def __init__(self, data, api=None):
        self.__dict__['api'] = api
        self.__dict__['data'] = data
        self.__dict__['_dirty_fields'] = {}

    def __getattr__(self, item):
        return self.__dict__['data'][item]

    def __setattr__(self, key, value):
        self._dirty_fields[key] = True
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
        if not self.streamclient:
            raise StreamClientNotSet()

        '''
        Sets a params dictionary for every time there is a dirty_fields item for that entry,
        meaning there is something to put in params. sets key of this param to be key of the
        dirty_fields dict which is the field that is going to be changed
        '''
        params = dict([(key, self.data[key])
                       for key, val in self._dirty_fields.items() if val])
        if not len(params):
            raise StreamNotModifiedException("No fields were modified.")

        if 'ID' in self.data:
            self.__dict__['data'] = self.streamclient.put(self.objCode, self.ID, params, list(self.data.keys()))
        else:
            self.__dict__['data'] = self.streamclient.post(self.objCode, params, list(self.data.keys()))

        self.__dict__['_dirty_fields'] = {}

    def delete(self, streamclient, force=False):
        """
        Deletes the current object by id
        raises -- StreamClientNotSet if stream client was not passed in constructor
        """
        if not self.streamclient:
            raise StreamClientNotSet()
        return self.streamclient.delete(self.objCode, self.ID, force)



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