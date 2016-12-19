import os
import json
from flask import make_response

def root_dir():
    """ Returns root director for this project """
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    print(dir_path)
    return dir_path


def nice_json(arg):
    response = make_response(json.dumps(arg, sort_keys = True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response
