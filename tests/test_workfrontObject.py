from unittest import TestCase
from workfrontapi_plus.core_wf_object import WorkfrontObject
from tests.wf_project_data_mock import project_data
from datetime import datetime


class TestWorkfrontObject(TestCase):

    core_obj = WorkfrontObject(project_data)

    def test__convert_dates(self):

        res = self.core_obj._convert_dates(project_data)
        golden = '2015-09-18'
        test = res['entryDate'].strftime('%Y-%m-%d')
        self.assertEqual(test, golden)

        golden = 'Test 2'
        test = res['name']
        self.assertEqual(test, golden)

        test = res['projectUsers'][0]['user']['reservedTimes'][0]['endDate']
        self.assertTrue(isinstance(test, datetime))


    def test_save(self):
        pass

    def test_delete(self):
        pass

    def test_share(self):
        pass

    def test_get_share(self):
        pass
