import threading
import matplotlib.pyplot as plt
from line_analizer import LineAnalyser



IP_LIST = [
    # "192.168.1.110",
    # "10.5.0.55",
    "192.168.0.50",
    # "192.168.0.49",
    # "192.168.0.50",
]

analisis = LineAnalyser(IP_LIST)

def main():
    info = analisis.run_analizer()
    for i in info:
        img = i[1]
        for key, value in i[0].items():
            print(f'{key}: \t{value}')
        plt.imshow(img)
        plt.show()    
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
    
