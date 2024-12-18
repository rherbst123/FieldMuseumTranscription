import time

def get_timestamp():
    return time.strftime("%Y-%m-%d-%H%M") 

def get_run_name(modelname):
    return f"{modelname}-{get_timestamp()}"    