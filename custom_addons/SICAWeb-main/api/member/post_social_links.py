import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8055'
endpoint = '/post/member_social_links'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'
# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is MEMBER
MEMBERSHIP_ID = '0024'

data = {"facebook_link" : "Muthaiyan", "youtube_link": "Muthaiyan", "linkedin_link": 'Muthaiyan',  "twitter_link": 'l', "instagram_link" : 'Muthaiyan'}

# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&MEMBERSHIP_ID={MEMBERSHIP_ID}&data={data}' # Include the api_key parameter in the query string
print(url)

# url : http://68.178.168.28:8069/post/member_social_links?db=odoo_si&api_key=8f4f506e4b4022e154ac3651f9ee006e9b751261&MEMBERSHIP_ID=0024&data={'facebook_link': 'Muthaiyan', 'youtube_link': 'Muthaiyan', 'linkedin_link': 'Muthaiyan', 'twitter_link': 'Muthaiyan', 'instagram_link': 'Muthaiyan'}

# Make a GET request to the URL
response = requests.post(url)

# Check the response
if response.status_code == 200:  # Assuming a successful response
    return_response = response.json()
    print(return_response)
else:
    print("Failed to retrieve data. Status code:", response.status_code)
    
    
