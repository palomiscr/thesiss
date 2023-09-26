import logging

import jellyfish
from fastapi import Request, HTTPException
import json, random
from business_logic.custom_exception import ForwardTaskException
from urllib.parse import unquote
from business_logic.similarity import Similarity

similarity=Similarity()

class MockingLogic:
    async def handle_request(self, path: str,  request: Request):
        # we assume we receive an extra parameter called mock with the endpoint
        with open("./result.json", 'r') as file:
            data_json = json.load(file)
        logs_data=data_json
        with open('./exceptions.txt', 'r') as file:
            list_as_str = file.read()

        exception_list = eval(list_as_str)
        emulate_endpoint='original_endpoint' #return 512 if endpoint not found
        endpoint=request.query_params[emulate_endpoint] #endpoint to emulate
        req_params={}
        logging.info(f"---------MOCKING LOGS--------------")

        try:
            request_body=await request.body()
            request_body_str = request_body.decode("utf-8")
            # print("query params", request.query_params)
            # print("path params", request.path_params)
            parsed_data = {}
            # print("body params non parsed ", request_body_str)
            data_pairs = request_body_str.split("&")
            for pair in data_pairs:
                key, value = pair.split("=")
                key = unquote(key)  # Decode URL-encoded key
                value = unquote(value)  # Decode URL-encoded value
                if value=='':
                    value='None'
                parsed_data[key] = value
            req_params=parsed_data
        except Exception as e:
            print("error", e)
        if endpoint in exception_list:
            raise ForwardTaskException(detail="forwarded task")
        else:
            resul=self.match_found(logs_data,endpoint, req_params)
            return resul

    def exact_match(self, stored_req, incoming_req):
        return stored_req==incoming_req

    def match_found(self, logs_data, endpoint, req_params):
        exact_matches = []
        closest_match={}
        max_score=0
        if logs_data is not None and endpoint in logs_data.keys():
            endpoint_entries=logs_data[endpoint]
            for entry in endpoint_entries:
                stored_req=entry.get('req')
                # print(f"\nstored_req: {stored_req}")
                # print(f"incoming request: {req_params}")
                if self.exact_match(stored_req, req_params):
                    exact_matches.append(entry) #in case of several exact matches, randomize
                elif not exact_matches: #in case of NO exact matches search for approximate matching
                    current_score = similarity.get_similarity(stored_req, req_params)
                    if current_score>max_score :
                        closest_match=entry
                        max_score=current_score
            # print("exact matches", exact_matches)
            # print("closest match", closest_match)
            if exact_matches:
                return random.choice(exact_matches)
            elif closest_match:
                return closest_match
            else:
                raise HTTPException(status_code=404,
                                    detail="no close match found")
        else:
            print(f"endpoint not found: {endpoint}")
            raise HTTPException(status_code=512,
                            detail="Endpoint not found. Please update the server with the corresponding template log.")


    def get_dict_params(self, request, emulate_endpoint):#create req dictionary for query parameters
        req_params={}
        for param in request.query_params:
            if param!=emulate_endpoint:
                req_params[param]= request.query_params[param]#create new entry in dictionary
        return req_params