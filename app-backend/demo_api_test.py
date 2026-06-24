import csv
import json
import urllib.request
from urllib.error import HTTPError, URLError

with open('demo_sample.csv', 'r', encoding='utf-8') as f:
    data = list(csv.DictReader(f))

req = urllib.request.Request(
    'http://127.0.0.1:8000/analyze',
    data=json.dumps({'data': data}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print('status', resp.status)
        body = resp.read().decode('utf-8')
        print(body[:2000])
except HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode('utf-8'))
except URLError as e:
    print('URL Error', e)
