import requests
import yaml

def load_operations(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def get_auth_token(base_url, username, password):
    url = f"{base_url}/passwordvault/api/auth/CyberArk/Logon"
    response = requests.post(url, data=json.dumps({"username": username, "password": password}), headers={'Content-Type': 'application/json'}, verify=True)
    if response.status_code == 200:
        return response.text.strip('"')
    else:
        raise Exception("Failed to authenticate.")

def add_safe(base_url, token, details, default_members):
    url = f"{base_url}/passwordvault/api/safes"
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    response = requests.post(url, headers=headers, json=details, verify=True)
    
    if response.status_code == 201:
        print(f"Safe '{details.get('SafeName')}' added successfully.")
        safe_name = details.get('SafeName')
        
        for member in default_members:
            try:
                add_safe_member(base_url, token, safe_name, member)
            except Exception as e:
                print(f"Failed to add default member to safe '{safe_name}': {e}")
    else:
        raise Exception("Failed to add safe.")

def add_safe_member(base_url, token, safe, details):
    url = f"{base_url}/passwordvault/api/safes/{safe}/members"
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    response = requests.post(url, headers=headers, json=details, verify=True)
    
    if response.status_code == 201:
        print(f"Member '{details.get('memberName')}' added to safe '{safe}' successfully.")
    else:
        raise Exception("Failed to add safe member.")

def add_account(base_url, token, safe, details):
    url = f"{base_url}/passwordvault/api/accounts"
    details['safeName'] = safe
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    response = requests.post(url, headers=headers, json=details, verify=True)
    
    if response.status_code == 201:
        print(f"Account '{details.get('userName')}' added successfully.")
    else:
        raise Exception("Failed to add account.")

def delete_safe(base_url, token, safe):
    url = f"{base_url}/passwordvault/api/safes/{safe}"
    headers = {'Authorization': token}
    response = requests.delete(url, headers=headers, verify=True)
    
    if response.status_code == 204:
        print(f"Safe '{safe}' deleted successfully.")
    else:
        raise Exception("Failed to delete safe.")

def delete_account(base_url, token, accountID):
    url = f"{base_url}/passwordvault/api/accounts/{accountID}"
    headers = {'Authorization': token}
    response = requests.delete(url, headers=headers, verify=True)
    
    if response.status_code == 204:
        print(f"Account '{accountID}' deleted successfully.")
    else:
        raise Exception("Failed to delete account.")

def process_operations(operations, base_url, token, default_members):
    for op in operations:
        if op['action'] == "add_safe":
            add_safe(base_url, token, op['details'], default_members)
        elif op['action'] == "add_safe_member":
            add_safe_member(base_url, token, op['safe'], op['details'])
        elif op['action'] == "add_account":
            add_account(base_url, token, op['safe'], op['details'])
        elif op['action'] == "delete_safe":
            delete_safe(base_url, token, op['safe'])
        elif op['action'] == "delete_account":
            delete_account(base_url, token, op['accountID'])
        else:
            print(f"Unknown action: {op['action']}")

if __name__ == "__main__":
    operations_file = "operations.yaml"
    base_url = "https://cyberark.example.com"
    username = "admin"
    password = "password"
    
    operations = load_operations(operations_file)
    token = get_auth_token(base_url, username, password)
    
    # Define default members for new safes
    default_members = [
        {
            "memberName": "DefaultMember1",
            "searchIn": "Vault",
            "permissions": {
                "useAccounts": True,
                "retrieveAccounts": True,
                # Define other permissions as needed
            }
        },
        # Add other default members as needed
    ]

    if token:
        process_operations(operations.get('operations', []), base_url, token, default_members)
    else:
        print("Authentication or script setup failed.")
