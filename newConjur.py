import yaml
from conjur import Client, ClientConfig, ConjurrcData, SslVerificationMode

def create_policy(client, policy_name, policy_data):
    try:
        response = client.create_policy(policy_name, policy_data)
        print(f"Policy {policy_name} created with response: {response}")
    except Exception as e:
        print(f"Error creating policy {policy_name}: {e}")

def update_policy(client, policy_name, policy_data):
    try:
        response = client.update_policy_file(policy_name, policy_data)
        print(f"Policy {policy_name} updated with response: {response}")
    except Exception as e:
        print(f"Error updating policy {policy_name}: {e}")

def delete_policy(client, policy_name):
    try:
        response = client.delete_policy(policy_name)
        print(f"Policy {policy_name} deleted with response: {response}")
    except Exception as e:
        print(f"Error deleting policy {policy_name}: {e}")

def main():
    # Initialize the Conjur Client with the necessary configuration
    client_config = ClientConfig(conjurrc_data=ConjurrcData(
        conjur_url='https://conjur-server',
        account='your-account',
        cert_file='/path/to/conjur-cert.pem'
    ), ssl_verification_mode=SslVerificationMode.TRUST_STORE)

    # Load instructions from YAML file
    with open('/instructions/new.yml', 'r') as file:
        instructions = yaml.safe_load(file)

    for instruction in instructions:
        branch = instruction['branch']
        policy_name = instruction['policy_name']
        policy_data = instruction['policy_data']

        # Dynamically create isolated Conjur accounts for each branch
        client_config.account = f'{client_config.account}-{branch}'
        
        # Initialize Conjur Client with branch-specific account
        client = Client(client_config=client_config)

        if instruction['action'] == 'create':
            create_policy(client, policy_name, policy_data)
        elif instruction['action'] == 'update':
            update_policy(client, policy_name, policy_data)
        elif instruction['action'] == 'delete':
            delete_policy(client, policy_name)

if __name__ == '__main__':
    main()
################################################################################################################################################################################################3
# new.yml
  
# - branch: branch1
#   action: create
#   policy_name: policy1
#   policy_data:
#     key1: value1
#     key2: value2

# - branch: branch1
#   action: update
#   policy_name: policy2
#   policy_data:
#     key3: value3
#     key4: value4

# - branch: branch2
#   action: delete
#   policy_name: policy3
#   policy_data:
#     key5: value5
#     key6: value6
