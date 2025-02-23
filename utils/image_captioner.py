import requests

API_URL = "https://router.huggingface.co/hf-inference/v1"
headers = {"Authorization": "Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxx"}

def query(filename):
	with open(filename, "rb") as f:
		data = f.read()
	response = requests.post(API_URL, headers=headers, data=data)
	return response.json()

output = query("cats.jpg")