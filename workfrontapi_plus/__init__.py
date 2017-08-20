"""
Copyright 2017, Integrated Device Technologies, Inc.

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

__doc__ = """
workfrontapi_plus is an upgraded version of the Python API distributed by Workfront.

This package adds some key features to the standard Workfront API package. Important features:

* Upgraded for Python 3.x (Does not support 2.x) *
This pacakge will only work with Python 3.x.

* Make updates as or on behalf of a user *
This allows a user with an API key to "login" as another user and make updates. For example a note update could be
left on behalf of another user.

* Bulk Update, Bulk Delete and Bulk Create with automatic handling of over 100 items*
Bulk update will automatically handle lists greater than 100 elements (the Workfront API limit). In addition to the 
standard "bulk" update support has been added for creation and deletion in bulk.

* Support for lists as parameter items * 
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
 



Authors: Roshan Bal, Craig Lathrop
"""

from workfrontapi_plus.api import Api
from workfrontapi_plus.objects import *
from workfrontapi_plus.core_wf_object import *
from workfrontapi_plus.tools import *
