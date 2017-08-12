# workfrontapi_plus
A workfront API with extended features written for python 3.x. This package contains several notable features and improvements from the Workfront provided "example" Python api.

##### Ability to handle lists as parameters
The workfront API will reject the ['something','somethingelse'] format if sent as a parameter value. This
method looks through the params for lists and converts them to simple comma separated values in a string. For
example.

```json
{'status': ['CUR', 'PLN', 'APP'],
 'status_Mod': 'in'}
```

 will be converted to

```json
{'status': 'CUR',
 'status': 'PLN',
 'status': 'APP',
 'status_Mod': 'in'}
```

##### Automatic handling of bulk updates greater than 100 items
The Workfront API limits updates to 100 objects at a time. The bulk, bulk_create, and bulk_delete functions can all automatically handle update lists of any size.

##### Automatic handling of results greater than 2000 items
The Workfront API will only provide 2000 objects as the result of a search. Workfrontapi_plus allows you to set a `get_all` flag or specify a limit when calling the search function. The results will be compiled into a single list and returned. Note that large responses may take some time as multiple API calls are needed.

##### Support for API Key Authentication
Allows for both login with username / pass or setting of an API key.

##### Make updates or create on behalf of another user
This method will login on behalf of another user by passing in the users ID (email) and the API key to the login
method. This will set a session ID. While the session ID is set all actions performed or taken will show as if
done by the users.

This is useful for script that might need to write updates on behalf of a user, change a commit date, or
perform other operations that can only be done by a task assignee or owner. This method will allow for post, put, search, or action.

##### General enhancements to the `report` function
The report function has been updated to allow for better control over aggregation, grouping and summation. 

##### A simple count function
Pass in some filter parameters and an object. This method will return a simple count of matching objects.

##### parse_workfront_date
In `workfrontapo_plus.Tools` `parse_workfront_date(date)` converts from the Workfront datetime format into a Python datetime object.

## Getting Started

### Authentication 
If using the API key, it is highly recommended that you store the key in a separate class or config file that 
is not part of your repository. Here is an example configuration file:

```python
class WorkfrontConfig(object):
    """
    This file holds path and credential information for the workfront API

    Replace the xxxxx below with your API key.
    """
    api_key = 'abcd21vo9n6ft3osd5548ym7m23dn7wwv'
    subdomain = 'xyz'
```

When instantiating the Workfront API class:

```python
from workfrontapi_plus import Workfront, Tools
from wfconfig import WorkfrontConfig

api = Workfront(WorkfrontConfig.subdomain, 'preview', api_key=WorkfrontConfig.api_key)
```

A user_id and session_id can be used in place of an API key, or, after instantiation a login can be executed.

### Basic Usage

Most functions require an object type, search parameters, and optional list of fields to return. Here is an example of a simple search call:

```python
params = {'name':'Roshan',
          'name_Mod':'cicontains'}

fields = ['name','entryDate']
api.search('USER', params, fields)
```
