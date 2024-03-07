############ Conjur Bash API ###################

#!/bin/bash

# CyberArk base URL
BASE_URL="https://cyberark.example.com"

# Authentication
authenticate() {
    local username="$1"
    local password="$2"
    local login_url="${BASE_URL}/api/auth/logon"

    # Perform login and capture token
    token=$(curl -s -X POST -H "Content-Type: application/json" \
        -d "{\"username\": \"${username}\", \"password\": \"${password}\"}" \
        "${login_url}" | jq -r '.token')

    if [[ "${token}" == null || -z "${token}" ]]; then
        echo "Authentication failed"
        exit 1
    else
        echo "Authenticated successfully"
    fi
}

# Function to create a safe
create_safe() {
    local safe_name="$1"
    local url="${BASE_URL}/api/safes"

    curl -s -X POST -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
        -d "{\"name\": \"${safe_name}\"}" \
        "${url}"
}

# Function to add a safe member
add_safe_member() {
    local safe_name="$1"
    local member_name="$2"
    local url="${BASE_URL}/api/safes/${safe_name}/members"

    curl -s -X POST -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
        -d "{\"member\": \"${member_name}\"}" \
        "${url}"
}

# Function to add an account to a safe
add_account() {
    local safe_name="$1"
    local account_details="$2"
    local url="${BASE_URL}/api/safes/${safe_name}/accounts"

    curl -s -X POST -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${token}" \
        -d "${account_details}" \
        "${url}"
}

# Main operation processing loop
process_operations() {
    while IFS=, read -r operation safe_name param; do
        case "${operation}" in
            "create_safe")
                create_safe "${safe_name}"
                ;;
            "add_safe_member")
                add_safe_member "${safe_name}" "${param}"
                ;;
            "add_account")
                # Assuming the account details are passed as a JSON string in $param
                add_account "${safe_name}" "${param}"
                ;;
            *)
                echo "Unknown operation: ${operation}"
                ;;
        esac
    done < "${1}"  # File path is passed as the first script argument
}

# Start script execution

# Ensure username and password are passed as arguments
if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <username> <password> <data_file>"
    exit 1
fi

USERNAME="${1}"
PASSWORD="${2}"
DATA_FILE="${3}"

# Authenticate and proceed if successful
authenticate "${USERNAME}" "${PASSWORD}"
process_operations "${DATA_FILE}"
