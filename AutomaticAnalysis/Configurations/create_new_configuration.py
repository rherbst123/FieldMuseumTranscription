import json
import sys

CONFIG_FOLDER = "AccuracyTesting/Configurations/"

def get_json(filename):
    with open(CONFIG_FOLDER+filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def does_file_already_exist(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except FileNotFoundError:
        return False

def confirm(configuration_filename, config_name):
    while True:
        pass

def get_names():
    fname = input("Enter the filename you want to save to: ")
    config_name = input("Enter the name for your configuration")
    if not does_file_already_exist(fname):
            

def main(config_name, configuration_filename):
    pass


if __name__ == "__main__":
    config_name = ""
    configuration_filename = ""
    main(config_name, configuration_filename)