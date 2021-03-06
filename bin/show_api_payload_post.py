#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Provide high level document structure of the Sumo Logic sumologic-api.yaml
"""

import os
import pprint
import time
import requests
from benedict import benedict

__version__ = 1.00
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

API_URL = 'https://api.sumologic.com/docs/sumologic-api.yaml'
API_FILE = '/var/tmp/sumologic-api.yaml'
PP = pprint.PrettyPrinter(indent=2, width=40, depth=4)

SEC2MIN = 60
MIN2HOURS = 60
NUM_HOURS = 4

TIME_LIMIT = SEC2MIN * MIN2HOURS * NUM_HOURS

if os.path.exists(API_FILE):
    stat_time = os.path.getctime(API_FILE)
    time_now = time.time()
    time_delta = (time_now - stat_time)
    if int(time_delta) > TIME_LIMIT:
        yaml_stream = requests.get(API_URL).text
        with open(API_FILE, 'w') as file_object:
            file_object.write(yaml_stream)
else:
    yaml_stream = requests.get(API_URL).text
    with open(API_FILE, 'w') as file_object:
        file_object.write(yaml_stream)

yaml_dict = benedict.from_yaml(API_FILE)

for keypath in benedict.keypaths(yaml_dict):
    if 'post.requestBody.content.application/json.schema.$ref' in keypath:
        if '{' not in keypath:
            (_paths, endpoint, apimethod) = keypath.split('.')[:3]
            (_first, apiversion, objectname) = endpoint.split('/')[:3]
            print('API_ENDPOINT: {}'.format(endpoint))
            print('API_DETAILS: {} {} {}'.format(objectname, apimethod, apiversion))
            keypayload = yaml_dict[keypath]
            keypayload = keypayload.replace('#/', '')
            keypayload = keypayload.replace('/', '.')
            my_payload = dict()
            my_payload['api.version'] = apiversion
            my_payload[objectname] = dict()
            if 'properties' in yaml_dict[keypayload]:
                for ATTRIBUTE in yaml_dict[keypayload]['properties']:
                    my_payload[objectname][ATTRIBUTE] = 'example_field'
                    for item in yaml_dict[keypayload]['properties'].items():
                        ATTRIBUTE = str(item[0])
                        if 'example' in item[1].keys():
                            my_value = item[1]['example']
                            my_payload[objectname][ATTRIBUTE] = my_value
                PP.pprint(my_payload)
            elif 'allOf' in yaml_dict[keypayload]:
                for my_item in yaml_dict[keypayload]['allOf']:
                    if '$ref' in my_item:
                        refpath = my_item['$ref']
                        refpath = refpath.replace('#/', '')
                        refpath = refpath.replace('/', '.')
                        if 'properties' in yaml_dict[refpath]:
                            for ATTRIBUTE in yaml_dict[refpath]['properties']:
                                my_payload[objectname][ATTRIBUTE] = 'example_field'
                                for item in yaml_dict[refpath]['properties'].items():
                                    ATTRIBUTE = str(item[0])
                                    if 'example' in item[1].keys():
                                        my_value = item[1]['example']
                                        my_payload[objectname][ATTRIBUTE] = my_value
                    if 'properties' in my_item:
                        for ATTRIBUTE in my_item['properties']:
                            print(ATTRIBUTE)
                            my_payload[objectname][ATTRIBUTE] = 'example_field'
                            for item in my_item['properties'].items():
                                ATTRIBUTE = str(item[0])
                                if 'example' in item[1].keys():
                                    my_value = item[1]['example']
                                    my_payload[objectname][ATTRIBUTE] = my_value
                PP.pprint(my_payload)
