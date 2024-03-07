import requests

def authenticate_cyberark(username, password, base_url):
    url = f"{base_url}/api/auth/logon"
    payload = {
        "username": username,
        "password": password
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json().get('token')

def create_safe(safe_name, token, base_url):
    url = f"{base_url}/api/safes"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"name": safe_name}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    print(f"Safe '{safe_name}' created successfully.")
    add_default_members(safe_name, token, base_url)  # Add default members after creating safe

def add_default_members(safe_name, token, base_url):
    default_members = {
        "member1": {"data": "value1"},
        "member2": {"data": "value2"},
        "member3": {"data": "value3"},
        "member4": {"data": "value4"},
        "member5": {"data": "value5"}
    }
    for member_name, member_data in default_members.items():
        add_safe_member(safe_name, member_name, member_data, token, base_url)

def add_safe_member(safe_name, member_name, member_data, token, base_url):
    url = f"{base_url}/api/safes/{safe_name}/members"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "member": member_name,
        "data": member_data
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    print(f"Member '{member_name}' added to safe '{safe_name}' successfully.")

def add_account(safe_name, account_details, token, base_url):
    url = f"{base_url}/api/safes/{safe_name}/accounts"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=account_details, headers=headers)
    response.raise_for_status()
    print(f"Account added to safe '{safe_name}' successfully.")

def process_file(file_path, token, base_url):
    with open(file_path, 'r') as file:
        for line in file:
            action, *params = line.strip().split(',')
            if action == "create_safe":
                create_safe(params[0], token, base_url)
            elif action == "add_safe_member":
                add_safe_member(params[0], params[1], {"data": params[2]}, token, base_url) if len(params) > 2 else print(f"Missing data for {params[1]}")
            elif action == "add_account":
                safe_name, account_details = params[0], eval(params[1])
                add_account(safe_name, account_details, token, base_url)
            else:
                print(f"Error: Unknown action {action}")

# Example usage
if __name__ == "__main__":
    base_url = "https://cyberark.example.com"
    username = "your_username"
    password = "your_password"
    file_path = "data.txt"

    token = authenticate_cyberark(username, password, base_url)
    if token:
        process_file(file_path, token, base_url)
    else:
        print("Authentication failed.")
