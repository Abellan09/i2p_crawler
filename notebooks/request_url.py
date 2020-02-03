import requests 
import sys

proxies={'http': 'http://localhost:4444',
	'https': 'https://localhost:4444'}
timeout=30

def connectThroughProxy(eepsite_url, proxies, timeout):
    	# headers
    	headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'}
    	response = requests.get(eepsite_url, proxies=proxies, headers=headers, timeout=timeout)
    	return response

def printResponse(response):
	print(response.status_code)
	print(response.elapsed.total_seconds())
	print(response.headers)
	print("[-]")

if len(sys.argv) == 2:

	url=sys.argv[1]

	print("[+] Connecting to " + url)

	response = connectThroughProxy(url, proxies, timeout)
	printResponse(response)
	
else:

	machine=sys.argv[2]

	with open(machine,'r') as f:
		sites = f.readlines()

	for site in sites:

		try:

			site=site.replace(':','').replace('\n','')
			url='http://'+site

			print("[+] Connecting to " + url)

			response = connectThroughProxy(url, proxies, timeout)
			printResponse(response)

		except ConnectionError ce:


		except Exception e:
			exc_type, exc_value, exc_traceback = sys.exc_info()
        		traceback.print_exception(exc_type, exc_value, exc_traceback, limit=5, file=sys.stdout)





