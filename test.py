import requests

for i in range(250):
    r = requests.post('http://192.168.88.191:5000/user/orders')
