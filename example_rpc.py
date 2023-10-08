# Example to show how to use classes from source/rpc/rpc_client.py
# begin import  XmlRpcCameraProxy

import os
import snap7
import socket
from collections import namedtuple
from source.rpc.rpc_client import XmlRpcProxyManager


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
IP_LIST = [
    # "192.168.0.47",
    # "192.168.0.48",
    "192.168.0.49",
    "192.168.0.50",
]
PLATFORM = "3.5.0061"
Point = namedtuple("Point", ["x", "y"])

camera_manager = XmlRpcProxyManager(IP_LIST, 8080)
reference = Point(320, 240) # control to know error
run = True

def init_camera_manager():
    camera_manager.connect()
    camera_manager.init_config()

def print_detection_result(result):
    for i, cam in enumerate(camera_manager):
        print(f"\t-> Camera {cam.ip}: {cam.url}")
        res = result[i]
        for key, value in res.items():
            print(f"\t{key}: {value}")

def execute_detection(verbose=False):
    result = camera_manager.execute_detection(tries=2)
    if verbose:
        print_detection_result(result)
    return result
        


def main(run = True):
    init_camera_manager()
    # Aditional init actions
    # ....
    # main loop
    while run:
        results = execute_detection(verbose=True)
        # Aditional actions
        diferences = []
        for res in results:
            if res['error'] == 0:
                point_detected = Point(res["x"], res["y"])
                diferences.append((point_detected.x - reference.x, point_detected.y - reference.y))
            else:
                diferences.append((0,0))

        print(f"Diferences: {diferences}")
        run = False

        

if __name__ == "__main__":
    try:
        main(run)
    except KeyboardInterrupt:
        run = False
        print("END")
    finally:
        run = False
# sys.exit(0)
