import os
import pathlib


ABS_PATH = pathlib.Path(__file__).parent.absolute()

def setup_mitmdump_server():
    path = os.path.join(ABS_PATH, "inject.py")
    os.system(f"nohup mitmdump -p 8080 -s {path}&")

def close_mitmdump_server():
    path = os.path.join(ABS_PATH, "close_mitmdump_server")
    os.system(f"sh {path}")
