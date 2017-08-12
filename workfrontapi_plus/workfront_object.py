


class WorkfrontObject(object):

    def __init__(self, wfid=None, obj_code=None, *args, **kwargs):
        self._id = None
        self._obj_code = None
        self.id = wfid
        self.obj_code = obj_code
        self.params = {}

    def save(self):
        pass

    def set_update_params(self, execute=False, **kwargs):
        for item in kwargs:
            pass

    def write_update(self):
        pass

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if len(value) == 32:
            self._id = value
        else:
            raise ValueError("The ID string must be exactly 32 characters")

    @property
    def obj_code(self):
        return self._id

    @obj_code.setter
    def obj_code(self, value):
        if len(value) == 32:
            self._id = value
        else:
            raise ValueError("The ID string must be exactly 32 characters")