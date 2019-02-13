import requests

def connectThroughProxy(eepsite_url):
    proxies = {'http': 'http://localhost:4444'}
    # headers as recommned
    #headers = {'User-Agent': 'MYOB/6.66 (AN/ON)'}
    headers = {}
    response = requests.get(eepsite_url, proxies=proxies, headers={})
    return response
