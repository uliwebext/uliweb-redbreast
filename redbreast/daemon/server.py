import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 4401))
sock.listen(5)
while True:
    conn, address = sock.accept()
    try:
        conn.settimeout(5)
        buf = conn.recv(1024)
        print buf
        if buf == '1':
            conn.send('welcome to server!')
        else:
            conn.send('please go out!')
    except socket.timeout:
        print 'timeout'
    conn.close()
    time.sleep(0)
    if buf == 'exit':
        exit()
