import requests

def connectThroughProxy(eepsite_url):
    proxies = {'http': 'http://localhost:4444'}
    response = requests.get(eepsite_url, proxies=proxies)
    return response
