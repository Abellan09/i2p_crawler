import socket
import time
from database import connection_settings

def connectThroughProxy(darksite_url):
    headers = "GET " + darksite_url + " HTTP/1.1\r\n\r\n"

    if not connection_settings.PROXY:
        host = None
        port = None
    elif ':' in connection_settings.PROXY:
        host = connection_settings.PROXY.split(':')[0]
        port = connection_settings.PROXY.split(':')[1]
    else:
        host = connection_settings.PROXY
        port = None

    try:
        s = socket.socket()
        print(("Connecting to " + darksite_url))
        s.connect((host,port))
        #print(headers)
        s.send(headers.encode('utf-8'))
        #print("Waiting for response from " + darksite_url)

        # Init time
        start_time = time.time()
        #print("Start execution time: " + time.strftime("%H:%M:%S:%", time.localtime(start_time)))
        response = s.recv(10000)
        #print(response)

        # End time
        end_time = time.time()
        elapsed_time = end_time - start_time
        #print("End execution time: " + time.strftime("%H:%M:%S", time.localtime(end_time)))
        #print("Elapsed time: " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

        s.close()
    except socket.error as m:
        print((str(m)))
        s.close()

    return response, start_time, end_time, elapsed_time

