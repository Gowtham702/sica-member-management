import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8059'
endpoint = '/member/session/close'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'

# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

access_token = 'd5e6f2a3-2220-4e14-aa93-dd8fb13d1ab2'
membership_number = '0024'

# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&membership_number={membership_number}&access_token={access_token}'  # Include the api_key parameter in the query string
print(url)

#URl: http://68.178.168.28:8069/otp/verify?db=odoo_si&api_key=8f4f506e4b4022e154ac3651f9ee006e9b751261&OTP=3240&access_token=58f99119-5ecb-42b1-8bbd-e3c337731c2

# Make a GET request to the URL
response = requests.post(url)

# Check the response
if response.status_code == 200:  # Assuming a successful response
    return_response = response.json()
    print(return_response)
else:
    print("Failed to retrieve data. Status code:", response.status_code)

