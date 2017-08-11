from datetime import datetime

class Tools(object):

    @staticmethod
    def parse_workfront_date(date_string):
        """
        Converts from the Workfront datetime format into a Python datetime object

        :param date_string: The workfront date string. Example "2017-01-01T01:01:00.000-0800"
        :return: A datetime object
        """
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S:%f%z")
