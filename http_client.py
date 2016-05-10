import socket
import time
import sys
from collections import OrderedDict
import StringIO

targets = OrderedDict()
#targets['download.microsoft.com'] = '/download/2/9/4/29413F94-2ACF-496A-AD9C-8F43598510B7/EIE11_EN-US_MCM_WIN764.EXE' 
#targets['ubuntu.ipacct.com'] = '/releases/trusty/ubuntu-14.04.4-server-amd64.iso' 
#targets['apache.cbox.biz'] = '/httpd/httpd-2.4.20.tar.gz'
targets['appldnld.apple.com'] = '/itunes12/031-51748-20160321-D6635716-EDF6-11E5-A6FC-DF14BE379832/iTunes12.3.3.dmg'
#targets['ftp.freebsd.org'] = '/pub/FreeBSD/releases/amd64/amd64/ISO-IMAGES/10.3/FreeBSD-10.3-RELEASE-amd64-dvd1.iso'


# A minimal implementation of httlib2 to be used for the test cases
class HTTPConnection:
    _http_vsn_str = 'HTTP/1.1'
    default_port = 80
    
    def __init__(self, host, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.host = host
        self.sock = None
        self.fp = None
        self._buffer = []
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            self.sock = None
            print msg
            sys.exit(1)

    def connect(self):
        try:
            self.sock.connect((self.host, self.default_port))
            self.fp = self.sock.makefile('rb', 0)
        except socket.error as msg:
            self.sock = None
            print msg
            sys.exit(1)
    
    def close(self):
        sock = self.sock
        fp = self.fp
        if sock:
            self.sock = None
            self.fp = None
            sock.close()
            fp.close()

    def request(self, method, url, headers={}):
        header_names = dict.fromkeys([k.lower() for k in headers])
        hdr = '%s %s %s' % (method, url, self._http_vsn_str)
        self._buffer.append(hdr)
        self._putheader('Host', self.host.encode("ascii"))

        for hdr, value in headers.iteritems():
            self._putheader(hdr, value)

        self._buffer.extend(("", ""))
        msg = "\r\n".join(self._buffer)
        del self._buffer[:]
        try:
            self.sock.sendall(msg)
        except socket.error as errmsg:
            self.sock = None
            print errmsg
            sys.exit(1)

    def get_response(self):
        maxline = 65536
        response = ''
        if self.fp == None:
            return HTTPResponse(response) # not connected
        while True:
            line = self.fp.readline(maxline + 1)
            if len(line) > maxline:
                print 'Warning line to long'
                return HTTPResponse(response)
            if not line:
                print 'Empty line, connection dropped'
                return HTTPResponse(response)
            if line == '\r\n':
                return HTTPResponse(response)
            response += line
                
    def _putheader(self, header, *values):
        header = '%s' % header
        values = [str(v) for v in values]
        hdr = '%s: %s' % (header, '\r\n\t'.join(values))
        self._buffer.append(hdr)

class HTTPResponse:
    def __init__(self, msg):
        # from the Status-Line of the response
        self.version = '' # HTTP-Version
        self.status = ''  # Status-Code
        self.reason = ''  # Reason-Phrase
        self.headers = OrderedDict()
        # Raw headers
        self.msg = msg
        self._read_msg()

    def _read_msg(self):
        maxline = 65536
        if self.msg:
            buf = StringIO.StringIO(self.msg)
            line = buf.readline(maxline + 1)
            if line:
                try:
                    [self.version, self.status, self.reason] = line.split(None, 2)
                except ValueError:
                    try:
                        [self.version, self.status] = line.split(None, 1)
                        self.reason = ''
                    except ValueError:
                        self.version = ''
                        self.status = ''
            line = buf.readline(maxline + 1)
            while line:
                [header, value] = line.split(': ', 1)
                line = buf.readline(maxline + 1)
                self.headers[header] = value.rstrip()
            
                

# Test functions
def download(host, resource):
    print 'Start download()'
    socket_timeout = 5.0
    max_read = 10240
    conn = HTTPConnection(host)
    conn.connect()
    print 'Receive buffer size=',conn.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print 'TCP Win size=', conn.sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    # lazy ranges
    header_value_ranges = ('bytes=0-5000000', 'bytes=0-10000000', 'bytes=0-30000000', 'bytes=0-50000000', 'bytes=0-100000000')
    for range in header_value_ranges:
        headers = {'Connection': 'keep-alive',
                   'Range': range,
                   'Accept': '*/*'}
        conn.request("GET", resource, headers)
        response = conn.get_response()
        if int(response.status) != 206:
            print 'Error not 206 HTTP status code !!!', response.status
            break
        content_len = int(response.headers['Content-Length'])
        print 'Downloading', content_len / 1000000, 'MBytes'
        if not content_len:
            print 'Error unable to get max Content-Length !!!'
            break
        total = 0
        start = time.time()
        #conn.sock.settimeout(socket_timeout)
        while 1:
            data = conn.sock.recv(max_read)
            total += len(data)
            if not data:
                print 'break data'
                break
            if total >= content_len:
                print 'break len'
                break

        print 'Received ', total / 1000000 ,'MBytes from', host, ' completed in ', time.time() - start, ' seconds'
        print 'Calculated speed', (total / 1000000 * 8) / (time.time() - start), 'Mbps'


def download_ex_flowcontrol_new(host, resource):
    print 'Start download_ex_flowcontrol()'
    socket_timeout = 5.0
    max_read = 10240
    max_msg_peek = max_read * 1000
    large_bufsize = 512000
    bufsize = 16000
    tcpwin = bufsize + 256
    verbose = 0
    # time to sleep/simulate some work with the buffer
    work_time = 0.1
    conn = HTTPConnection(host)

    # set receive buffer before connect for some test
    # conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufsize)
    # no need to set TCP_WINDOW_CLAMP it's adjusted to the receive buffer
    #conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, 1024)
    conn.connect()
    
    init_win = conn.sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
    init_buf = conn.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    
    if verbose:
        print 'Initial receive buffer set to', init_buf
        print 'Initial TCP Win set to', init_win

    # lazy ranges
    #header_value_ranges = ('bytes=0-5000000', 'bytes=0-10000000', 'bytes=0-30000000', 'bytes=0-50000000', 'bytes=0-100000000')
    header_value_ranges = ('bytes=0-50000', 'bytes=0-100000', 'bytes=0-300000', 'bytes=0-500000', 'bytes=0-1000000')
    for range in header_value_ranges:
        conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufsize)
        conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, tcpwin)
        if verbose:
            print 'Receive buffer size set to', conn.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            print 'TCP Win set to', conn.sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)

        headers = {'Connection': 'keep-alive',
                   'Range': range,
                   'Accept': '*/*'}
        conn.request("GET", resource, headers)
        response = conn.get_response()
        if int(response.status) != 206:
            print 'Error not 206 HTTP status code !!!', response.status
            break
        content_len = int(response.headers['Content-Length'])
        print 'Downloading', content_len / 1000000, 'MBytes'
        if not content_len:
            print 'Error unable to get max Content-Length !!!'
            break
        total = 0
        start = time.time()
        # conn.sock.settimeout(socket_timeout)
        while 1:
            if len(conn.sock.recv(max_msg_peek, socket.MSG_PEEK)) >= bufsize:
                # we've got data do some work here
                time.sleep(work_time)
                break
        
        # set a larger buffer to resume a normal download 
        conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, init_buf)
        conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP, init_win)

        if verbose:
            print 'Resume download with Receive buffer set to', conn.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            print 'Resume download with TCP Win', conn.sock.getsockopt(socket.IPPROTO_TCP, socket.TCP_WINDOW_CLAMP)
        
        while 1:
            data = conn.sock.recv(max_read)
            total += len(data)
            if not data:
                break
            if total >= content_len:
                break

        print 'Received ', total / 1000000 ,'MBytes from', host, ' completed in ', time.time() - start, ' seconds'
        print 'Calculated speed', (total / 1000000 * 8) / (time.time() - start), 'Mbps'
    

# Start tests
for host in targets.keys():
    resource = targets.get(host)
    #download(host, resource)
    download_ex_flowcontrol_new(host, resource)

