import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8055'
endpoint = '/create/grievance_report'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'
# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is MEMBER
MEMBERSHIP_ID = '0024'
REASON_ID = '1'

data = {"member_name_no": "0024", "name": "6558989", "project_name": "cook", "projection_house_name": "Muthu",
        "outdoor_unit_name": "fesj", "location": "dfgr", "contact_outdoor_unit_manager": "20/12/2023", "approximate_time_lost": "fgxvfezgve",
        "has_outdoor_unit_manager_helpful_to_the_solve_issue": "Yes", "name_contact_no_of_production_manager_executive_producer": "gdxgdg", "brief_issue_faced_with_service_of_outdoor_unit_equipment": "dfgh", "issue_has_been_reported": "20/10/2023",
        "issue_type": "djgibjikf fg h"}

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
    
    
