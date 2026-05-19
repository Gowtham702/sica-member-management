import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8059'
endpoint = '/get/app/maintenance'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'
MEMBERSHIP_ID = '0024'

# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'
# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}'
print(url)

# Make a GET request to the URL
response = requests.get(url)

# Check the response
if response.status_code == 200:  # Assuming a successful response
    return_response = response.json()
    print(return_response)
else:
    print("Failed to retrieve data. Status code:", response.status_code)






