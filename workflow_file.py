import json


def import_wkfw_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def save_wkfw_file(filepath, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)


BASE_TEMPLATE = """
{
    "cells":[
        {
            "type": "markdown",
            "content": "This is a markdown cell and below will be a task cell."
        },
        {
            "type": "task",
            "task_type": "write",
            "task_data":{
                "interval": 0.2,
                "text": "Hello World!"
            }
        }
    ]
}
"""

def create_wkfw_file(filepath):
    save_wkfw_file(filepath, json.loads(BASE_TEMPLATE))

def process_data(data):
    print("Processing Done!")