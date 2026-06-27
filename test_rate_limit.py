import requests

url = "http://127.0.0.1:8000/query"
headers = {"Authorization": "Bearer hello123"}
body = {"question": "What is AI safety?"}

for i in range(12):
    response = requests.post(url, json=body, headers=headers)
    print(f"Request {i+1}: {response.status_code}")
    if response.status_code == 429:
        print("Rate limit hit!")
        print("Headers:", dict(response.headers))
        break