import requests
from requests.auth import HTTPBasicAuth
import traceback
import json

class API:
    def __init__(self, api_host, api_tkn):
        self.api_host = api_host
        self.api_tkn = api_tkn

    def send_ret_json(self, method, route, payload):
        return json.loads(self.send(method, route, payload))

    def send(self, method, route, payload):
        try:
            print("Send API call")
            print([method, route, payload])

            fun = requests.get
            if method == 'POST':
                fun = requests.post
            elif method == 'PUT':
                fun = requests.put
            elif method == 'DELETE':
                fun = requests.delete

            r = fun(self.api_host + '/' + route,
                json=payload,
                auth=HTTPBasicAuth(self.api_tkn, 'not-in-use'),
                verify=False)
            print(f"Status Code: {r.status_code}, Response:")
            print(r.text)

            return r.text
            
        except Exception:
            traceback.print_exc()