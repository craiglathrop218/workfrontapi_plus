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

from datetime import datetime
import collections
import re
import hashlib
import hmac

class Tools(object):
    @staticmethod
    def parse_workfront_date(date_string):
        """
        Converts from the Workfront datetime format into a Python datetime object

        :param date_string: The workfront date string. Example "2017-01-01T01:01:00.000-0800"
        :return: A datetime object
        """
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S:%f%z")

    def flatten_response(self, data, sep=":", pretty=False):
        """
        Flattens out nested dict

        This method will take a Workfront API response and "flatten out" certain nested dicts.
        For example, here is a response for a task
        [{'ID': 'abc123...',
          'name': 'test task',
          'project': {'ID': 'cde456',
                      'name': 'My Proj'}
          }]

        would be converted to
        [{'ID': 'abc123...',
          'name': 'test task',
          'project:ID': 'cde456',
          'project:name': 'My Proj'
          }]

        :param data:
        :param skip_keys:
        :param use_keys:
        :param pretty: Removes the project:name style notation. Example:
                with pretty set to true
                [{'ID': 'abc123...',
                  'Name': 'test task',
                  'Project ID': 'cde456',
                  'Project Name': 'My Proj'
                  }]
        :return: A processed list or dict
        """
        output = []
        for item in data:
            output.append(self.flatten_dict(item, sep=sep, pretty=pretty))
        return output

    def flatten_dict(self, data, parent_key='', sep=":", pretty=False):
        items = []
        for key, value in data.items():
            new_key = parent_key + sep + key if parent_key else key
            if pretty:
                new_key = self.pretty_keys(new_key)
            if isinstance(value, collections.MutableMapping):
                items.extend(self.flatten_dict(data=value, parent_key=new_key, sep=sep, pretty=pretty).items())
            else:
                items.append((new_key, value))

        return dict(items)

    def pretty_keys(self, key):
        # todo Finish this, still a bit buggy.
        key = key[:1].title()+key[1:]
        res = re.findall('[A-Z][^A-Z]*', key)
        output = ''
        for item in res:
            output = '{0} {1}'.format(output, item)

        return output.strip()

    @staticmethod
    def text_mode(text):
        """
        Converts Workfront "Text Mode" into a parameter string.

        :param text: A string containing Workfront text mode parameters
        :return: A dict version of the passed in parameters
        """
        output = {}

        for line in text.splitlines():

            key, value = line.split("=")

            # key = key_pair[0].strip()
            # value = key_pair[1].strip()

            if "\t" in value:
                # It's a list
                value_list = value.split("\t")
                output[key] = value_list
            else:
                output[key] = value
        return output

    @staticmethod
    def make_config_file():
        """
        Makes a config file to hold sub domain and API Key
        """
        code = '''
class WorkfrontConfig(object):
    """
    This file holds path and credential information for the workfront API

    This file is designed to help keep your authentication data safe and out of your 
    repository. To use this file when instantiating the Workfront Api:
    
    
    1 from wfconfig import WorkfrontConfig
    2
    3 api = Api(subdomain=WorkfrontConfig.subdomain,
    4           api_key=WorkfrontConfig.api_key,
    5           env='preview',
    6           api_version='6.0')
    
    """
    # Enter your API key here. This can be found in the Workfront interface under 
    # setup->Customer Info.
    api_key = '{api_key}'
    
    # The sub domain is the prefix to the URL you use to access Workfront. For example
    # https://xxx.my.workfront.com, xxx would be the sub domain.
    subdomain = '{sub_domain}'
'''
        api_key = input("Enter your API key: ")
        sub_domain = input("Enter your subdomain: ")
        output = code.format(api_key=api_key, sub_domain=sub_domain)
        config_file = open("wfconfig.py", "w")
        config_file.write(output)
        config_file.close()


    @staticmethod
    def make_signature(message, key):

        key = bytes(key, 'UTF-8')
        message = bytes(message, 'UTF-8')

        digester = hmac.new(key, message, hashlib.sha1)
        signature1 = digester.hexdigest()

        return signature1