import requests
import os
import json

def authenticate_cyberark(username, password, base_url):
    url = f"{base_url}/api/auth/logon"
    payload = {
        "username": username,
        "password": password
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # This will raise an error for HTTP codes 400 or 500
        token = response.json().get('token')
        return token
    except requests.exceptions.HTTPError as e:
        print(f"Error authenticating: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def create_safe(safe_name, token, base_url):
    url = f"{base_url}/api/safes"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"name": safe_name}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Safe '{safe_name}' created successfully.")
    except requests.exceptions.HTTPError as e:
        print(f"Error creating safe '{safe_name}': {e}")

def add_safe_member(safe_name, member_name, token, base_url):
    url = f"{base_url}/api/safes/{safe_name}/members"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {"member": member_name}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Member '{member_name}' added to safe '{safe_name}' successfully.")
    except requests.exceptions.HTTPError as e:
        print(f"Error adding member '{member_name}' to safe '{safe_name}': {e}")

def add_account(safe_name, account_details, token, base_url):
    url = f"{base_url}/api/safes/{safe_name}/accounts"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=account_details, headers=headers)
        response.raise_for_status()
        print(f"Account added to safe '{safe_name}' successfully.")
    except requests.exceptions.HTTPError as e:
        print(f"Error adding account to safe '{safe_name}': {e}")

def process_file(file_path, token, base_url):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    with open(file_path, 'r') as file:
        line_no = 0
        for line in file:
            line_no += 1
            try:
                action, *params = line.strip().split(',')
                if action == "create_safe":
                    create_safe(params[0], token, base_url)
                elif action == "add_safe_member":
                    add_safe_member(params[0], params[1], token, base_url)
                elif action == "add_account":
                    safe_name, account_details_str = params[0], params[1]
                    account_details = json.loads(account_details_str)
                    add_account(safe_name, account_details, token, base_url)
                else:
                    print(f"Unsupported action '{action}' on line {line_no}.")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON data on line {line_no}: {e}")
            except Exception as e:
                print(f"Error processing line {line_no}: {e}")

# Example usage
base_url = "https://cyberark.example.com"
username = "your_username"
password = "your_password"
file_path = "data.txt"

token = authenticate_cyberark(username, password, base_url)
if token:
    process_file(file_path, token, base_url)
else:
    print("Authentication failed. Exiting.")
