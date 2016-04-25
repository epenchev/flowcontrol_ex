# sample client program
import socket
import os
import time
import sys

HOST = 'localhost'    # remote server host
PORT = 7777           # Server remote port
 
def get_socket_options(s, optlist):
    try:
        optlist["tcp_win"] = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
        optlist["sock_buf"] = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    except socket.error as msg:
        print 'Error geting socket options', msg

def set_tcp_window_size(s, tcpwin):
    try:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, tcpwin)
        return s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    except socket.error as msg:
        print 'Error setting TCP window size', msg

def set_socket_recv_bufsize(s, bufsize):
    try:
        # kernel doubles the size of the value
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufsize)
        return s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    except socket.error as msg:
        print 'Error setting TCP window size', msg


optlist = {}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    get_socket_options(s, optlist)
    print 'before connect TCP win', optlist["tcp_win"], 'socket receive buffer', optlist["sock_buf"] 
    
    s.connect((HOST, PORT))
    get_socket_options(s, optlist)
    print 'After connect TCP win', optlist["tcp_win"], 'socket receive buffer', optlist["sock_buf"]
    set_socket_recv_bufsize(s, 4096)

    for count in range(0, 20):
        get_socket_options(s, optlist)
        bufsize = optlist["sock_buf"];
        print 'TCP win', optlist["tcp_win"] , 'socket receive buffer', optlist["sock_buf"]
        #print 'data received', len(s.recv(1024000))
        #print 'data in buffer', len(s.recv(1024000, socket.MSG_PEEK))
        time.sleep(5)
  
except socket.error as msg:
    s = None
    print msg
    print 'could not connect to target', HOST
    sys.exit(1)

s.close()


