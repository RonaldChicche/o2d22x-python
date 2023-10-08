import socket

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(("192.168.0.50", 50010))
    soc.sendall(b'1000v03\r\n')
    msg = soc.recv(1024)
    print(msg)

try:
    main()
except KeyboardInterrupt:
    print("END")
