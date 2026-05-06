import requests
import re

url = "https://onlinesim.com.br/copacabana/assets/indexv2_7_0.js"
try:
    response = requests.get(url)
    js_content = response.text
    # Procurar strings que comecem com /api/ ou api/ ou que tenham 'produtos'
    endpoints = re.findall(r'["\'](/api/[^\'"]+)["\']', js_content)
    print("Endpoints encontrados:", list(set(endpoints))[:20])
except Exception as e:
    print(e)
