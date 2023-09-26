# app/presentation/router.py
import logging
import threading
import uuid
from threading import Thread
import requests
from fastapi import APIRouter, Request, HTTPException, Response
from business_logic.custom_exception import ForwardTaskException
from business_logic.item import ItemLogic
from business_logic.mocking import MockingLogic
from datetime import datetime
import time
from requests_toolbelt import MultipartEncoder

router = APIRouter()
item_logic = ItemLogic()
mocking_logic = MockingLogic()


def wait_async(callback, resul, start_time):  # resul: array with N responses containing "data" and "elapsedtime"
    current_thread = threading.current_thread()
    thread_id = current_thread.ident
    thread_id = str(uuid.uuid4())

    logging.info(f"---------thread LOGS--{time.time()}--{thread_id}----------")

    #logging.info(f"data retrieved: {resul}")

    last_response=len(resul['res']) -1 if len(resul['res'])>0 else 0

    index=0
    #logging.info(f"PUT request to {callback}\n")

    for current_response in resul['res']:
        time_result = calculate_time(current_response['elapsedtime'], start_time)
        if(time_result>0):
            time.sleep(time_result)

        #print(f"\nresponse {index} of {last_response}: {current_response}")

        mimetype=current_response['data'].get('mimetype')

        if mimetype and mimetype=="application/json":
            print("json data")
            del current_response['data']['mimetype']
            dict_=current_response['data']
            key_json=""
            value_json=""
            for key in dict_.keys():
                key_json=key
                value_json=dict_[key]

            multipart_data=MultipartEncoder(fields={key_json:( key_json, value_json, 'application/json')})
            sheaders = {'Content-Type':multipart_data.content_type}
        elif not current_response['data']:
            multipart_data=None
            sheaders = {}
        else:
            multipart_data=MultipartEncoder(fields=current_response['data'])
            sheaders = {'Content-Type': multipart_data.content_type}

        if index != last_response:
            sheaders["CPEE-UPDATE"] = "true"

        response = requests.put(callback, data=multipart_data, headers=sheaders)

        if response.status_code == 200:
            logging.info(f"RETURN ASYNC PUT request to {callback} was successful. {time.time()}")
        else:
            logging.error(f"RETURN ASYNC PUT request to {callback} failed with status code {response.status_code}.")
        index+=1


def calculate_time(stored_elapsedtime, start_time): #calculate precise timeout substracting server's overhead
    dt = datetime.strptime(stored_elapsedtime, "%H:%M:%S.%f")
    total_time = dt.microsecond / 1000000.0 + dt.second + dt.minute * 60 + dt.hour * 3600  # datetime to float(seconds)
    time_elapsed_server = time.time() - start_time
    return total_time - time_elapsed_server


@router.get("/{path:path}")
@router.post("/{path:path}")
@router.put("/{path:path}")
@router.delete("/{path:path}")
@router.patch("/{path:path}")
@router.options("/{path:path}")
@router.head("/{path:path}")
async def mock(path: str, request: Request, response: Response):
    start_time = time.time()
    if request.url.path == "/update":
        return item_logic.handle_request(path)
    else:
        try:
            result = await mocking_logic.handle_request(path, request)
            callback = request.headers['Cpee-Callback']
            logging.info(f"---------server LOGS--------------")

            thread = Thread(target=wait_async, args=[callback, result, start_time])
            thread.start()
            logging.info(f"---------continue--{time.time()}------------")

            return Response(headers={"CPEE-CALLBACK":"true"}, status_code=200)
        except ForwardTaskException as forward_exception:
            raise ForwardTaskException(forward_exception.detail)
        except HTTPException as http_err:
            raise HTTPException(http_err.status_code, http_err.detail)
        except Exception as err:
            print(err)
            raise HTTPException(500, "Internal server error")
