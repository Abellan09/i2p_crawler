import socket
import time

def connectThroughProxy(eepsite_url):
    headers = "GET " + eepsite_url + " HTTP/1.1\r\n"

    host = "localhost" #proxy server IP
    port = 4444        #proxy server port

    try:
        s = socket.socket()
        #print("Connecting to " + eepsite_url)
        s.connect((host,port))
        s.send(headers.encode('utf-8'))
        #print("Waiting for response from " + eepsite_url)

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
        print (str(m))
        s.close()

    return response, start_time, end_time, elapsed_time

