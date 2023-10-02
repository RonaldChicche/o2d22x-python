import cv2
import numpy as np
from io import BytesIO
from source.o2d22x import O2D22xPCICDevice
import matplotlib.pyplot as plt
from collections import namedtuple



'''
3 pixel por mmm
word:
- busy
- ready
- falla (fail/pass(3times) - errors)
- desfase de linea 
- fuera de area

precision 
posX - mm
posY - mm
orientacion
desX - mm
desY - mm


4 camaras
'''
Objeto = namedtuple('Objeto', ['x', 'y', 'ori'])


class LineAnalyser():

    data_struct = {
        "SYSTEM":{
            "BUSY": 0,
            "READY": 0,
            "FAIL": 0,
            "GAP": 0,
            "OUTSIDE": 0,
        },
        "CAM1":{
            "POSX": 0,
            "POSY": 0,
            "ORIE": 0,
            "DESX": 0,
            "DESY": 0,
            "FAIL": 0,
        },
        "CAM2":{
            "POSX": 0,
            "POSY": 0,
            "ORIE": 0,
            "DESX": 0,
            "DESY": 0,
            "FAIL": 0,
        },
        "CAM3":{
            "POSX": 0,
            "POSY": 0,
            "ORIE": 0,
            "DESX": 0,
            "DESY": 0,
            "FAIL": 0,
        },
        "CAM4":{
            "POSX": 0,
            "POSY": 0,
            "ORIE": 0,
            "DESX": 0,
            "DESY": 0,
            "FAIL": 0,
        }
    }

    def __init__(self, ip_list) -> None:
        self.cameras = [O2D22xPCICDevice(ip, 50010) for ip in ip_list]
        # Area definition
        self.mx = 200
        self.my = 200
        self.or_err = 20
        self.img_w = 640
        self.img_h = 480

    def getAllInfo(self):
        all_info = []
        for cam in self.cameras:
            all_info.append(cam.request_device_info_decoded())
        
        return all_info
    
    def analize_cam(self, id_cam, app):
        tries = 3
        responses = {}
        cam = self.cameras[id_cam]
        while tries:
            responses['SET_APP'] = cam.select_application(app)      # * !
            responses['SET_OT1'] = cam.activate_result_output(1)    # * !
            responses['RES_EVA'] = cam.evaluate_image_decoded()     # data !
    
            if responses['RES_EVA']['result'] == "FAIL":
                print(f'<CAM{id_cam}> Evaluation fail - T{3-tries} retring')
                tries -= 1
                continue
            responses['SET_OT2'] = cam.activate_result_output(0)    # * !    
            responses['RES_IMG'] = cam.request_image_decoded(responses['RES_EVA']['result'])     # data !

            for key, value in responses.items():
                if str(value) == '!':
                    print(f'<CAM{id_cam}> Fail {key} - T{3-tries}')                    
                    tries -= 1
                    continue
                
            return (responses['RES_EVA'], responses['RES_IMG'])
        
        responses['RES_EVA'] = {'result': 'FAIL'}
        responses['RES_IMG'] = cam.request_image_decoded(responses['RES_EVA']['result'])     # data !
        return (responses['RES_EVA'], responses['RES_IMG'])


    def run_analizer(self):
        results = []
        for i in range(len(self.cameras)):
            result = self.analize_cam(i, 4)
            # print(result[0])
            results.append(result)

        for cam_response in results:
            if cam_response[0]['result'] == 'FAIL':
                continue
            obj = Objeto(cam_response[0]['x'], cam_response[0]['y'], cam_response[0]['rot'])
            img = cam_response[1]
            # Print analysis on image
            dx = self.img_w/2 - obj.x
            dy = self.img_h/2 - obj.y
            cam_response[0]['dx'] = dx
            cam_response[0]['dy'] = dy
            
            # Draw margin lines
            lx_1s = (int(self.img_w/2 - self.mx), self.img_h)
            lx_1e = (int(self.img_w/2 - self.mx), 0)
            lx_2s = (int(self.img_w/2 + self.mx), self.img_h)
            lx_2e = (int(self.img_w/2 + self.mx), 0)

            ly_1s = (self.img_w, int(self.img_h/2 - self.my))
            ly_1e = (0, int(self.img_h/2 - self.my))
            ly_2s = (self.img_w, int(self.img_h/2 + self.my))
            ly_2e = (0, int(self.img_h/2 + self.my))

            ch_s = (0, int(self.img_h/2))
            ch_e = (self.img_w, int(self.img_h/2))
            cv_s = (int(self.img_w/2), 0)
            cv_e = (int(self.img_w/2), self.img_h)

            cv2.line(img, lx_1s, lx_1e, (0, 255, 0), 1)
            cv2.line(img, lx_2s, lx_2e, (0, 255, 0), 1)
            cv2.line(img, ly_1s, ly_1e, (0, 255, 0), 1)
            cv2.line(img, ly_2s, ly_2e, (0, 255, 0), 1)
            cv2.circle(img, (obj.x, obj.y), 0, (255, 0, 0), 5)
            
            cv2.line(img, ch_s, ch_e, (150, 0, 150), 1)
            cv2.line(img, cv_s, cv_e, (150, 0, 150), 1)

            # Draw difference
            ldx_s = (obj.x, obj.y)
            ldx_e = (int(self.img_w/2), obj.y)
            ldy_s = (obj.x, obj.y)
            ldy_e = (obj.x, int(self.img_h/2))
            cv2.line(img, ldx_s, ldx_e, (150, 0, 150), 1)
            cv2.line(img, ldy_s, ldy_e, (150, 0, 150), 1)
            txt_dx = (int((obj.x + self.img_w/2)/2), obj.y + 10)
            txt_dy = (obj.x+10, int((obj.y + self.img_h/2)/2))
            cv2.putText(img, f"x_diff: {dx}", (txt_dx), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 0, 150), 1)
            cv2.putText(img, f"y_diff: {dy}", (txt_dy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 0, 150), 1)

            cam_response = (cam_response[0], img)

        return results

            

        

            






        



