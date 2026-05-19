import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8059'
endpoint = '/get/all/member_details/discussion'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'

# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is MEMBER
account_type = 'MEMBER'
user_member_no = '0024'
member_no = '0024'
limit = ''

# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&user_member_no={user_member_no}&member_no={member_no}' # Include the api_key parameter in the query string
print(url)
#http://localhost:8055/get/all/member_details/discussion?db=odoo_si&api_key=8f4f506e4b4022e154ac3651f9ee006e9b751261&user_member_no=0024&member_no=3020

# http://68.178.168.28:8069/get/member_details?db=odoo_si&api_key=8f4f506e4b4022e154ac3651f9ee006e9b751261&MEMBERSHIP_ID=0024
# Make a GET request to the URL
response = requests.get(url)

# Check the response
if response.status_code == 200:  # Assuming a successful response
    return_response = response.json()
    print(return_response)
else:
    print("Failed to retrieve data. Status code:", response.status_code)
    
    




