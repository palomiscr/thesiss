# app/business_logic/item.py
import logging
import sys

import yaml
from yaml import SafeLoader
import json
from datetime import datetime
import os


class ItemLogic:
    def handle_request(self, path: str):
        endpoints = {}
        exceptions = []
        directory_path = "./logs/test_set"
        file_count = len([f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))])
        print(f"Number of files in the directory: {file_count}")
        for i in range(1, file_count+1):
            print(f"Reading file {i}...")
            with open(f"{directory_path}/log ({i}).yaml", "r") as stream:
                try:
                    data = list(yaml.load_all(stream, Loader=SafeLoader))
                except yaml.YAMLError as exc:
                    print(exc)

            for entry in data:  # skip logs only containing descriptions
                if 'event' in entry.keys():
                    transition = entry['event']['cpee:lifecycle:transition']
                    if transition == 'activity/calling':
                        self.fetch_data(entry, endpoints, 'req')
                    elif transition == 'activity/receiving':
                        self.fetch_data(entry, endpoints, 'res')
                    elif transition == 'task/instantiation':
                        exception_endpoint = entry['event']['concept:endpoint']
                        if exception_endpoint not in exceptions:
                            exceptions.append(exception_endpoint)
        # Serializing json
        endpoints_json = json.dumps(endpoints, indent=4)
        with open("result.json", "w") as outfile:
            outfile.write(endpoints_json)
        with open("exceptions.txt", "w") as outfile:
            outfile.write(str(exceptions))

        return {"message": f"Update Received request for path: {path}"}

    def get_request_parameters(self, entry):
        reqdict = {}
        if entry['event']['data']:  # empty set of parameters
            for par in entry['event']['data']:  # fetch request parameters
                reqdict[par['name']] = str(par['value'])  # {name: costs, value: 738.0} -> {costs:738}
        return reqdict

    def get_response_body(self, entry):
        resdict = {}
        if 'raw' in entry['event'].keys():  # empty response
            for par in entry['event']['raw']:  # fetch request parameters
                resdict[par['name']] = par['data']  # {name: id, data: FlyNiki} -> {id:FlyNiki}
                if par.get('mimetype'):
                    resdict['mimetype']=par['mimetype']
        return resdict


    def fetch_data(self, entry, endpoints, petition_type):

        dict_ = {}
        endpoint_name = entry['event']['concept:endpoint']
        if petition_type == 'req':
            dict_ = self.get_request_parameters(entry)
        else:
            dict_ = self.get_response_body(entry)

        uuid = entry['event']['cpee:activity_uuid']
        current_timestamp_str = entry['event']['time:timestamp']
        current_timestamp = datetime.fromisoformat(current_timestamp_str)
        if endpoint_name not in endpoints:
            endpoints[endpoint_name] = []
            if petition_type == 'req':  # req:dictionary
                endpoints[endpoint_name].append({'req': dict_, 'timestamp': current_timestamp_str, 'uuid': uuid, 'res': []})
            elif petition_type == 'res':  # res: list of dictionaries
                res_output = {'data': dict_,'elapsedtime': current_timestamp_str}
                endpoints[endpoint_name].append({'req': {}, 'res': [res_output], 'uuid': uuid})
        else:
            current_uuid = entry['event']['cpee:activity_uuid']
            found=False
            for stored_entry in endpoints[endpoint_name]:  # req?, res?, timestamp?, uuid
                if stored_entry['uuid'] == current_uuid:
                    found=True
                    if petition_type == 'req' and not stored_entry['req']:
                        stored_entry['req'] = dict_
                        stored_entry['timestamp'] = str(current_timestamp)
                        for response in stored_entry['res']:
                                response['elapsedtime'] = str(datetime.fromisoformat(response['elapsedtime']) - current_timestamp)  # res - req time
                    elif petition_type == 'res':
                        if stored_entry.get('timestamp'):  # there is already a req timestamp
                            recorded_timestamp = datetime.fromisoformat(stored_entry['timestamp'])
                            elapsedtime = str(current_timestamp - recorded_timestamp)  # res timestamp-req timestamp
                        else:  # at this point, we have several responses without req yet
                            elapsedtime = str(current_timestamp)

                        res_output = {'data': dict_,'elapsedtime': elapsedtime}
                        stored_entry['res'].append(res_output)
                        # if len(stored_entry['res'])>1:
                        #     print("multiresponse", endpoint_name)
                        #     print("uuid", uuid)
            if not found:#new req/res entry is added to that endpoint list
                if petition_type == 'req':  # req:dictionary
                    endpoints[endpoint_name].append({'req': dict_, 'timestamp': current_timestamp_str, 'uuid': uuid, 'res': []})
                elif petition_type == 'res':  # res: list of dictionaries
                    res_output = {'data': dict_, 'elapsedtime': current_timestamp_str}
                    endpoints[endpoint_name].append({'req': {}, 'res': [res_output], 'uuid': uuid})
