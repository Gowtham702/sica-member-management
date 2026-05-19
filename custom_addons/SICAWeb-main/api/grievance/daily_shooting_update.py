import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8055'
endpoint = '/create/daily_shooting_update'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'
# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is MEMBER
MEMBERSHIP_ID = '0024'
REASON_ID = '3'

data = { 'date': '26/01/2023',
            'member_contact_no': 'member_contact_no',
            'member_name': 'member_name',
            'email': 'email',
            'membership_no': 'membership_no',
            'category': 'category',
            'project_title': 'project_title',
            'format': 'format',
            'designation': 'designation',
            'producer': 'producer',
            'project_house': 'project_house',
            'production_executive': 'production_executive',
            'production_executive_contact_no': 'production_executive_contact_no',
            'outdoor_unit_name':'outdoor_unit_name',
            'location': 'location',
            'reason_id': 'location',}

# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&MEMBERSHIP_ID={MEMBERSHIP_ID}&Reason_id={REASON_ID}&data={data}' # Include the api_key parameter in the query string
print(url)

# url : http://localhost:8055/create/work_details?db=odoo_si&api_key=8f4f506e4b4022e154ac3651f9ee006e9b751261&MEMBERSHIP_ID=121&data={'project_name': 'Animal Photo', 'year': '2023', 'designation': ''}

# Make a GET request to the URL
response = requests.post(url)

# Check the response
if response.status_code == 200:  # Assuming a successful response
    return_response = response.json()
    print(return_response)
else:
    print("Failed to retrieve data. Status code:", response.status_code)
    
    
