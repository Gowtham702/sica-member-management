import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8059'
endpoint = '/api/get_login_otp'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'

# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is GUEST
account_type = 'GUEST'

# if account type is MEMBER
account_type = 'MEMBER'
MEMBERSHIP_ID = '0024'
MOBILE_NUMBER = '9655558329'
guest_name = ""

# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&account_type={account_type}&MEMBERSHIP_ID={MEMBERSHIP_ID}&MOBILE_NUMBER={MOBILE_NUMBER}&guest_name={guest_name}'  # Include the api_key parameter in the query string
print(url)
# Make a GET request to the URL
response = requests.get(url)

# Check the response
if response.status_code == 200:  # Assuming a successful response
    return_response = response.json()
    print(return_response)
else:
    print("Failed to retrieve data. Status code:", response.status_code)



#Testing Website URl : https://www.postman.com/            
#Final OTP GET Request URl : http://68.178.168.28:8069/api/get_login_otp?db={database_name}&api_key={api_key}&account_type={account_type}&MEMBERSHIP_ID={MEMBERSHIP_ID}&MOBILE_NUMBER={MOBILE_NUMBER}        
#Example OTP GET Request URL MEMBER : http://68.178.168.28:8069/api/get_login_otp?db=sicadop_01&api_key=8f4f506e4b4022e154ac3651f9ee006e9b751261&account_type=MEMBER&MEMBERSHIP_ID=2&MOBILE_NUMBER=9384451751
#GUEST OTP REQUEST URL : http://68.178.168.28:8069/api/get_login_otp?db=sicadop_01&api_key=8f4f506e4b4022e154ac3651f9ee006e9b751261&account_type=GUEST&MEMBERSHIP_ID=&MOBILE_NUMBER=7406460855
