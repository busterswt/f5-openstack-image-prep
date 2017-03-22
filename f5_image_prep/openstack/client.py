# Copyright 2015-2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
import json
import glanceclient as gclient
from keystoneclient.v3 import client
from keystoneclient.auth.identity import v3
from keystoneclient import session as session

class AuthURLNotSet(KeyError):
    pass


def get_keystone_client(creds):
    """Create keystone client."""
    auth = v3.Password(username=creds.username,
                       password=creds.password,
                       project_name=creds.tenant_name,
                       project_id=creds.project_id,
                       auth_url=creds.auth_url,
                       project_domain_name=creds.project_domain_name,
                       user_domain_name=creds.user_domain_name)
    sess = session.Session(auth=auth,verify=False)

    return creds.auth_url,sess

def get_glance_client(creds):
    """Create glance client"""
    auth_url,sess = get_keystone_client(creds)

    path = '%s/auth/catalog' % auth_url
    resp = sess.get(path,
                    authenticated=True,
                    endpoint_filter={'service_type': 'identity',
                                     'interface': 'public',
                                     'region_name': 'RegionOne'})

    catalog = json.loads(resp.text)
    glance_endpoint = get_endpoint_url('image',catalog)

    authDict = sess.auth.__dict__
    myToken = authDict["auth_ref"]["auth_token"]

    return gclient.Client('1', endpoint=glance_endpoint, token=myToken, insecure=True)

def get_endpoint_url(type,catalog):
    try:
        for service in catalog["catalog"]:
	    # Find the matching service in catalog
            if service['type'] == type:
                for endpoint in service["endpoints"]:
                    if endpoint['interface'] == 'public':
                        return endpoint['url']
    except:
        raise Exception("Unable to determine endpoint URL!")
