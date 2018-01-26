import requests
import json

CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_OCTET_STREAM = "application/octet-stream"

def http_get(uri):
    pass


def http_post(uri, headers = None, params = None, body = None, log = False):
    if (log): print("\n→→→→→→→→→→→→ start http connection →→→→→→→→→→→→")
    response = requests.post(uri, headers=headers, params=params, data=json.dumps(body))
    if (log): print(response.text)
    if (log): print("←←←←←←←←←←←← end   http connection  ←←←←←←←←←←←←\n")
    return response


def http_post_image(uri, image,  headers= None, params = None, log = False):
    if (log): print("\n→→→→→→→→→→→→ start http connection →→→→→→→→→→→→")
    response = requests.post(uri, headers=headers, params=params, data=image)
    if (log): print(response.text)
    if (log): print("←←←←←←←←←←←← end   http connection  ←←←←←←←←←←←←\n")
    return response

def create_headers(content_type = None, ocp_apim_subscriotion_key = None, authorization = None):
    dic = {}
    if not content_type is None: dic['Content-Type'] = content_type
    if not ocp_apim_subscriotion_key is None: dic['Ocp-Apim-Subscription-Key'] = ocp_apim_subscriotion_key
    if not authorization is None:dic['Authorization'] = "key=" + authorization
    return dic