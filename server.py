# sample server program
import socket
import sys
import time
import os
import random, string

def gen_random_data(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def send_msg(sock, msg):
    totalsent = 0
    msglen = len(msg)
    while totalsent < msglen:
        sent = sock.send(msg[totalsent:])
        #print 'sent', sent, ' bytes'
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent
    return totalsent

HOST = 'localhost'
PORT = 7777        # non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
except socket.error as msg:
    print 'Error starting server', msg
    sys.exit(1)

# generate 20M of data
data = gen_random_data(1024000 * 20)
print 'Server init done !'

while 1:
    conn, addr = s.accept()
    print 'Connected by', addr
    print 'sent buffer is', conn.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    sent = 0
    chunkSize = len(data)
    while (sent < len(data)):
        try:
            sent += send_msg(conn, data[sent:sent + chunkSize])
            print 'Total send', sent
        except socket.error as msg:
            print 'error sending data', msg
            break
        except RuntimeError as msg:
            print msg
            break
    conn.close()

