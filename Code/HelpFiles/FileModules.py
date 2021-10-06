import yaml
import json



def load_config(file_addr):
    return load_yalm(file_addr)

def load_yalm(file_addr):
    with open(file_addr) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def load_json(file_addr):
    with open(file_addr) as file:
        return json.load(file)