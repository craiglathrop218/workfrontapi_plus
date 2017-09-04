from unittest import TestCase
from workfrontapi_plus.core_wf_object import WorkfrontObject
from tests.wf_project_data_mock import project_data

class TestWorkfrontObject(TestCase):

    core_obj = WorkfrontObject(project_data)

    def test__convert_dates(self):
        pass

    def test_save(self):
        pass

    def test_delete(self):
        pass

    def test_share(self):
        pass

    def test_get_share(self):
        pass
