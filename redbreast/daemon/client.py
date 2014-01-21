import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 4401))

import time
time.sleep(2)
sock.send('1')
print sock.recv(1024)
sock.close()