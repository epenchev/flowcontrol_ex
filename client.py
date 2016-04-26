# sample client program
import socket
import os
import time
import sys

HOST = 'localhost'    # remote server host
PORT = 7777           # Server remote port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcpwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    
    print '[before connect] win', tcpwin, 'rcv buffer', bufsize
    
    #print 'set buffer size to 16000 bytes'
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16000)
    print 'connect'
    s.connect((HOST, PORT))
    
    tcpwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    
    print '[after connect] win', tcpwin, 'rcv buffer', bufsize
    time.sleep(30)
    print 'data in buffer', len(s.recv(1024000, socket.MSG_PEEK))
    
    '''
    tcpwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print '[after connect]  win', tcpwin, 'rcv buffer', bufsize

    time.sleep(10)
    print 'data in buffer', len(s.recv(1024000, socket.MSG_PEEK))
    
    print 'set buffer size to 16000 bytes'
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16000)
    tcpwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print 'win', tcpwin, 'rcv buffer', bufsize
    time.sleep(30)
    print 'data in buffer', len(s.recv(1024000, socket.MSG_PEEK))
    
    print 'set buffer size to 1024000 bytes'
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024000)
    tcpwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print 'win', tcpwin, 'rcv buffer', bufsize
    time.sleep(30)
    print 'data in buffer', len(s.recv(1024000, socket.MSG_PEEK))
    
    print 'set buffer size to 16000 bytes'
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 16000)
    tcpwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    bufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print 'win', tcpwin, 'rcv buffer', bufsize
    time.sleep(30)
    print 'data in buffer', len(s.recv(1024000, socket.MSG_PEEK))
    '''

except socket.error as msg:
    s = None
    print msg
    sys.exit(1)

s.close()


