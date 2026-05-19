import requests

# Define the URL of your Odoo instance
base_url = 'http://localhost:8059'
endpoint = '/post/job_seeker'  # Endpoint defined in your Odoo controller

# Assuming you have multiple databases and need to specify the database name
database_name = 'odoo_si'
# Your API key
api_key = '8f4f506e4b4022e154ac3651f9ee006e9b751261'

# if account type is MEMBER
MEMBERSHIP_ID = '0024'

data = {"membership_no": "0024", "mobile_number": "6558989", "member_name": "Muthu",
        "skills": "1, dferferf", "post_apply": "1", "grade": "fedf",
        "portifolio_link": "gdrgdr", "portifolio_link_2": "gdrgdr", "note": "gdxgdg", "document_binary": "", "availability_from": "20/10/2023", "availability_till": "10/10/2024", "format_id": "2", "job_seeker_id": "38"}

# Prepare the full URL
url = f'{base_url}{endpoint}?db={database_name}&api_key={api_key}&MEMBERSHIP_ID={MEMBERSHIP_ID}&data={data}' # Include the api_key parameter in the query stringx
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
    
    
