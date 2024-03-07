#!/bin/bash

# Base URL for the CyberArk API
BASE_URL="https://cyberark.example.com"

# Declare an associative array for default members and their specific data
declare -A MEMBER_DATA=(
    [member1]='{"data": "value1"}'
    [member2]='{"data": "value2"}'
    [member3]='{"data": "value3"}'
    [member4]='{"data": "value4"}'
    [member5]='{"data": "value5"}'
)

# Authenticate to CyberArk and retrieve a session token
authenticate() {
    local username="$1"
    local password="$2"
    local login_url="${BASE_URL}/api/auth/logon"

    # Make API call to authenticate
    response=$(curl -s -w "%{http_code}" -o response.tmp -X POST -H "Content-Type: application/json" \
        -d "{\"username\": \"${username}\", \"password\": \"${password}\"}" \
        "${login_url}")
    http_code=$(tail -n1 response.tmp)
    content=$(head -n -1 response.tmp)

    if [ "$http_code" != "200" ]; then
        echo "Authentication failed with status $http_code"
        echo "$content"
        exit 1
    fi

    # Extract token from response
    token=$(jq -r '.token' <<< "$content")
    echo "Authenticated successfully. Token: $token"
    rm response.tmp
}

# Function to create a safe
create_safe() {
    local safe_name="$1"
    local url="${BASE_URL}/api/safes"

    response=$(curl -s -w "%{http_code}" -o response.tmp -X POST -H "Authorization: Bearer ${token}" \
        -H "Content-Type: application/json" -d "{\"name\": \"${safe_name}\"}" "${url}")
    http_code=$(tail -n1 response.tmp)
    content=$(head -n -1 response.tmp)

    if [ "$http_code" != "201" ]; then
        echo "Failed to create safe $safe_name with status $http_code"
        echo "$content"
    else
        echo "Safe $safe_name created successfully."
        add_default_members "$safe_name"
    fi
    rm response.tmp
}

# Function to add default members to a safe
add_default_members() {
    local safe_name="$1"
    for member_name in "${!MEMBER_DATA[@]}"; do
        add_safe_member "$safe_name" "$member_name" "${MEMBER_DATA[$member_name]}"
    done
}

# Function to add a member to a safe
add_safe_member() {
    local safe_name="$1"
    local member_name="$2"
    local member_data="$3"
    local url="${BASE_URL}/api/safes/${safe_name}/members"

    response=$(curl -s -w "%{http_code}" -o response.tmp -X POST -H "Authorization: Bearer ${token}" \
        -H "Content-Type: application/json" -d "$member_data" "${url}")
    http_code=$(tail -n1 response.tmp)
    content=$(head -n -1 response.tmp)

    if [ "$http_code" != "201" ]; then
        echo "Failed to add member $member_name to safe $safe_name with status $http_code"
        echo "$content"
    else
        echo "Member $member_name added to safe $safe_name successfully."
    fi
    rm response.tmp
}

# Function to add an account to a safe (implementation example)
add_account() {
    local safe_name="$1"
    local account_details="$2"
    local url="${BASE_URL}/api/safes/${safe_name}/accounts"

    response=$(curl -s -w "%{http_code}" -o response.tmp -X POST -H "Authorization: Bearer ${token}" \
        -H "Content-Type: application/json" -d "$account_details" "${url}")
    http_code=$(tail -n1 response.tmp)
    content=$(head -n -1 response.tmp)

    if [ "$http_code" != "201" ]; then
        echo "Failed to add account to safe $safe_name with status $http_code"
        echo "$content"
    else
        echo "Account added to safe $safe_name successfully."
    fi
    rm response.tmp
}

# Main operation processing function
process_operations() {
    while IFS=, read -r operation safe_name param; do
        case "$operation" in
            "create_safe")
                create_safe "$safe_name"
                ;;
            "add_safe_member")
                # Example: add_safe_member "safeName" "memberName" '{"data": "memberData"}'
                # Using MEMBER_DATA for default data in this example; adjust as needed.
                add_safe_member "$safe_name" "$param" "${MEMBER_DATA[$param]}"
                ;;
            "add_account")
                # Example usage: add_account "safeName" '{"username": "accountUser", "platform": "Linux", "address": "192.168.1.10"}'
                add_account "$safe_name" "$param"
                ;;
            *)
                echo "Unknown operation: $operation"
                ;;
        esac
    done < "$1"
}

# Script execution
if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <username> <password> <data_file.csv>"
    exit 1
fi

USERNAME="$1"
PASSWORD="$2"
DATA_FILE="$3"

authenticate "$USERNAME" "$PASSWORD"
process_operations "$DATA_FILE"
