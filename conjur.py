
import requests
import os
import base64

# Function to authenticate with Conjur and retrieve an access token
def conjur_authenticate():
    conjur_authn_url = "http://localhost:8080/authn/myConjurAccount/frank@db/authenticate"
    api_key = "<FRANK API TOKEN>"  # Host's API Key

    response = requests.post(conjur_authn_url, data=api_key, verify=False)
    if response.status_code != 200:
        raise Exception("Authentication failed")

    encoded_token = base64.b64encode(response.content).decode('utf-8')
    return encoded_token

# Function to retrieve a secret from Conjur
def retrieve_secret(variable_id, access_token):
    conjur_variable_url = f"http://localhost:8080/secrets/myConjurAccount/variable/{variable_id}"
    headers = {"Authorization": f"Token token=\"{access_token}\""}

    response = requests.get(conjur_variable_url, headers=headers, verify=False)
    if response.status_code != 200:
        raise Exception("Failed to retrieve secret")

    return response.text

# Main function to connect to PostgreSQL and execute a query
def main():
    access_token = conjur_authenticate()
    
    db_username = retrieve_secret("db/POSTGRES_HOST_AUTH_METHOD", access_token)
    db_password = retrieve_secret("db/POSTGRES_HOST_AUTH_METHOD", access_token)
    db_name = retrieve_secret("db/POSTGRES_PASSWORD", access_token)

    print(db_username, db_password,db_name)

    # conn_string = f"host='localhost' dbname='{db_name}' user='{db_username}' password='{db_password}'"
    
    # # Connect to your postgres DB
    # conn = psycopg2.connect(conn_string)
    
    # # Execute a query
    # cursor = conn.cursor()
    # cursor.execute("SELECT * FROM example_table")

    # # Fetch and print the result
    # for row in cursor.fetchall():
    #     print(row)  # Assuming 'row' is a tuple of column values

    # # Close the cursor and connection
    # cursor.close()
    # conn.close()

if __name__ == "__main__":
    main()









Setting up Conjur OSS (Open Source Software) on Kubernetes using Helm involves several steps. Helm simplifies the deployment of applications on Kubernetes clusters by managing packages called charts. Conjur OSS is a powerful secret management tool that helps you manage and secure access to secrets (such as keys, tokens, and other sensitive data) in applications, systems, and infrastructure.

Below is a high-level guide on how to set up Conjur OSS in Kubernetes using Helm. This guide assumes you have a Kubernetes cluster running and Helm installed on your local machine.

### Step 1: Add CyberArk Helm Repository

Before you can install Conjur OSS using Helm, you need to add the CyberArk Helm repository to your Helm client. This repository contains the charts for deploying Conjur OSS.

```shell
helm repo add cyberark https://cyberark.github.io/helm-charts
helm repo update
```

### Step 2: Create a Namespace for Conjur OSS

It's a good practice to deploy applications within their own Kubernetes namespaces to isolate resources and manage access more securely.

```shell
kubectl create namespace conjur-oss
```

### Step 3: Install Conjur OSS using Helm

Now, you can install Conjur OSS using Helm. You'll specify the namespace you created in the previous step. You may also need to customize the installation by creating a `values.yaml` file if you need to override default configuration values.

```shell
helm install conjur-oss cyberark/conjur-oss --namespace conjur-oss --set dataKey="$(docker run --rm cyberark/conjur data-key generate)"
```

The `dataKey` is a required setting for the Helm chart, used to secure the data stored by Conjur. This command uses Docker to run a Conjur container just to generate a new data key. If you're not using Docker, you'll need to find another way to generate this key.

### Step 4: Configure Access to Conjur OSS

After installation, you'll need to set up access to Conjur OSS for your applications. This typically involves configuring Kubernetes authentication with Conjur and managing policies for secrets access.

1. **Configure Kubernetes Authenticator**: You'll need to enable and configure the Kubernetes authenticator in Conjur. This involves setting up a Conjur policy that defines the Kubernetes authenticator and its permitted hosts.

2. **Create Conjur Policies**: Define Conjur policies to manage access to secrets. Policies define roles (such as users or applications) and permissions on secrets.

3. **Inject Secrets into Applications**: Use Conjur's Kubernetes authenticator and secrets provider to securely inject secrets into your applications running in Kubernetes.

### Step 5: Verify the Installation

Verify that Conjur OSS is running and accessible by listing the pods in the `conjur-oss` namespace and checking the logs of the Conjur OSS pod.

```shell
kubectl get pods -n conjur-oss
kubectl logs <conjur-oss-pod-name> -n conjur-oss
```

### Additional Configuration and Usage


