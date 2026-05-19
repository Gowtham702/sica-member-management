import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8059'
endpoint = '/create/shooting_dop'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'
# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is MEMBER
MEMBERSHIP_ID = '0024'

data = {"date": "21/01/2023", "member_name": "6558989", "member_number": "0024", "mobile_number": "0024",
        "grade": "grade",
        "project_title": "fesj", "format_id": "11", "schedule_start": "10/12/2023", "schedule_end": "05/05/2024",
        "producer": "Producer", "production_house": "Production House", "production_executive": "production_executive",
        "production_executive_contact_no": "production_executive_contact_no",
        "location": "location", "outdoor_link_details": "Yes",
        'associate': [{"name": "Animal Photo", "mobile_number": "2023", "member_number": "0024", "role_type": "Assistent"},{"name": "Animal Photo", "mobile_number": "2023", "member_number": "0024", "role_type": "Assistent"}]
         }
# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&MEMBERSHIP_ID={MEMBERSHIP_ID}&data={data}' # Include the api_key parameter in the query string
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
    
    
