import requests
from urllib.parse import quote

# Define the URL of your Odoo instance
base_url = 'http://localhost:8059'
endpoint = '/create/update_shooting'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'
# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is MEMBER
MEMBERSHIP_ID = '0024'

data = {"date": "20/12/2023", "member_name": "6558989", "member_number": "cook", "mobile_number": "0024",
        "grade": "Grade",
        "dop_name": "Murugan", "dop_member_number": "0024", "project_title": "fesj", "format_id": "3",
        "designation": "Designation",
        "producer": "Producer", "production_house": "Production House", "production_executive": "production_executive",
        "production_executive_contact_no": "production_executive_contact_no",
        "location": "location",
        "outdoor_unit_name": "outdoor_unit_name",
        "notes": "Yes", }

# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&MEMBERSHIP_ID={MEMBERSHIP_ID}&data={data}'  # Include the api_key parameter in the query string
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
