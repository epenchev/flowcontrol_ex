import socket
import time
import sys
from collections import OrderedDict
from optparse import OptionParser

targets = OrderedDict()
#targets['download.microsoft.com'] = 'GET /download/2/9/4/29413F94-2ACF-496A-AD9C-8F43598510B7/EIE11_EN-US_MCM_WIN764.EXE HTTP/1.1\r\nHost: download.microsoft.com\r\nConnection: close\r\n\r\n' 
#targets['ubuntu.ipacct.com'] = 'GET /releases/trusty/ubuntu-14.04.4-server-amd64.iso HTTP/1.1\r\nHost: ubuntu.ipacct.com\r\nConnection: close\r\n\r\n' 
#targets['apache.cbox.biz'] = 'GET /httpd/httpd-2.4.20.tar.gz HTTP/1.1\r\nHost: apache.cbox.biz\r\nConnection: close\r\n\r\n'
#targets['appldnld.apple.com'] = 'GET /itunes12/031-51748-20160321-D6635716-EDF6-11E5-A6FC-DF14BE379832/iTunes12.3.3.dmg HTTP/1.1\r\nHost: appldnld.apple.com\r\nConnection: close\r\n\r\n'
# skip this one is to slow
targets['ftp.freebsd.org'] = 'GET /pub/FreeBSD/releases/amd64/amd64/ISO-IMAGES/10.3/FreeBSD-10.3-RELEASE-amd64-dvd1.iso HTTP/1.1\r\nHost: ftp.freebsd.org\r\nConnection: close\r\n\r\n'

parser = OptionParser()
parser.add_option("--wait_timeout", help="sleep time seconds/milliseconds", type="float", dest="wait_time", metavar="seconds", default=0.2)
parser.add_option("--buffer_size", help="receive socket buffer size in KBytes", type="int", dest="buf_size", metavar="KBytes", default=16)
parser.add_option("--count_size", help="resize socket buffer on every count MBytes", type="int", dest="byte_count", metavar="MBytes", default=10)
#parser.add_option("--twin", help="change TCP win field on every count MBytes", dest="twin", metavar="Bytes", default=0)

(options, args) = parser.parse_args()

def download(host, request):
    print 'Connecting to', host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        total = 0
        s.connect((host, 80))
        # just for the stats
        startbufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        startwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
        print 'Initial buf size=', startbufsize, 'Initial TCP win=', startwin
        #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, startwin * 2)
        #print 'TCP win set to ', s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
        request = targets.get(host)

        if request is not None:
            print 'Sending request'
            s.sendall(request)
            print 'Start download()'
            start = time.time()
            while 1:
                data = s.recv(10000)
                total += len(data)
                if not data:
                    print 'Received total', total ,'bytes from', host
                    print 'Download completed in', time.time() - start, 'seconds'
                    break
            
    except socket.error as msg:
        s = None
        print msg
        sys.exit(1)


def download_ex_flowcontrol(host, request):
    print 'Connecting to', host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        total = 0
        s.connect((host, 80))
        startbufsize = s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        startwin = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
        print 'Initial buf size=', startbufsize, 'Initial TCP win=', startwin
        request = targets.get(host)
        if request is not None:
            print 'Sending request'
            s.sendall(request)
            print 'Start download_ex_flowcontrol()'
            start = time.time()
            size = 0
            while 1:
                data = s.recv(10000)
                total += len(data)
                size += len(data)
                # on every M size do buffer resize
                if size / (options.byte_count * 1000000) > 0:
                    size = 0
                    # monitor TCP window on every resize
                    print 'TCP Win=', s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
                    #s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, options.buf_size * 1000)
                    
                    # some experiments with the TCP window
                    #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, 1152)
                    
                    print 'buffer size set to', s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF), 'TCP win is', s.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
                    time.sleep(options.wait_time)
                    # restore the original buffer size
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, startbufsize)
                    
                    #s.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, twin)
                if not data:
                    print 'Received total', total ,'bytes from', host
                    print 'Download completed in', time.time() - start, 'seconds'
                    break
            s.close()
    except socket.error as msg:
        s = None
        print msg
        sys.exit(1)


for host in targets.keys():
    request = targets.get(host)
    download(host, request)
    #download_ex_flowcontrol(host, request)
