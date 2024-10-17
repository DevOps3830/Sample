#!/bin/bash

# --------------------------------------
# Utility Functions
# --------------------------------------

# Prints colored messages to the terminal
print_color() {
    local color=$1
    local message=$2
    case "$color" in
        "red")    echo -e "\033[31m$message\033[0m" ;;
        "green")  echo -e "\033[32m$message\033[0m" ;;
        "yellow") echo -e "\033[33m$message\033[0m" ;;
        "blue")   echo -e "\033[34m$message\033[0m" ;;
        *)        echo "$message" ;;
    esac
}

# Prompts the user for input and returns the value
get_input() {
    local prompt="$1"
    local input
    while true; do
        read -p "$prompt: " input
        if [ -z "$input" ]; then
            print_color "red" "Input cannot be empty. Please try again."
        else
            echo "$input"
            break
        fi
    done
}

# Ensures a directory exists, creating it if necessary
ensure_directory_exists() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        if [ $? -eq 0 ]; then
            print_color "green" "Directory '$dir' created."
        else
            print_color "red" "Failed to create directory '$dir'. Check permissions."
            exit 1
        fi
    else
        print_color "yellow" "Directory '$dir' already exists."
    fi
}

# Check if required command exists on the system
check_command() {
    local cmd="$1"
    if ! command -v "$cmd" &> /dev/null; then
        print_color "red" "Error: Command '$cmd' is not installed or not found in PATH."
        exit 1
    fi
}

# General function to handle failures
handle_error() {
    local exit_code=$1
    local action=$2
    if [ "$exit_code" -ne 0 ]; then
        print_color "red" "Error occurred during $action. Exiting..."
        exit 1
    fi
}

# --------------------------------------
# Kubernetes Functions
# --------------------------------------

# Creates a basic Pod YAML configuration
generate_pod_yaml() {
    local pod_name=$1
    local namespace=$2
    local yaml_file=$3

    cat <<EOF > "$yaml_file"
apiVersion: v1
kind: Pod
metadata:
  name: $pod_name
  namespace: $namespace
spec:
  containers:
  - name: $pod_name-container
    image: nginx
    ports:
    - containerPort: 80
EOF
    handle_error $? "generating Pod YAML"
    print_color "green" "YAML file for Pod '$pod_name' created at $yaml_file."
}

# Previews, edits (if necessary), and applies the Kubernetes YAML configuration
apply_yaml() {
    local yaml_file=$1

    print_color "yellow" "Previewing YAML file: $yaml_file"
    kubectl apply -f "$yaml_file" -o yaml
    handle_error $? "previewing YAML"

    while true; do
        local choice
        read -p "Do you want to apply this configuration? (y/n/edit): " choice
        case "$choice" in
            y|Y)
                kubectl apply -f "$yaml_file"
                handle_error $? "applying configuration"
                print_color "green" "Configuration applied successfully."
                break
                ;;
            n|N)
                print_color "red" "Configuration application canceled."
                break
                ;;
            edit)
                nano "$yaml_file"
                handle_error $? "editing YAML"
                ;;
            *)
                print_color "red" "Invalid option. Please enter y, n, or edit."
                ;;
        esac
    done
}

# Handles the Pod creation process
pod_creation() {
    local yaml_dir="$1"
    local pod_name namespace yaml_file

    pod_name=$(get_input "Enter the Pod name")
    namespace=$(get_input "Enter the namespace")
    yaml_file="$yaml_dir/pod_${pod_name}.yaml"

    generate_pod_yaml "$pod_name" "$namespace" "$yaml_file"
    apply_yaml "$yaml_file"
}

# --------------------------------------
# Helm Functions
# --------------------------------------

# Installs a Helm chart
helm_install() {
    local release_name chart_name namespace

    release_name=$(get_input "Enter the Helm release name")
    chart_name=$(get_input "Enter the Helm chart name (e.g., bitnami/nginx)")
    namespace=$(get_input "Enter the namespace for Helm chart")

    print_color "yellow" "Installing Helm chart '$chart_name' as release '$release_name' in namespace '$namespace'."
    helm install "$release_name" "$chart_name" --namespace "$namespace"
    handle_error $? "installing Helm chart"

    print_color "green" "Helm chart '$chart_name' installed successfully."
}

# --------------------------------------
# Menu Functions
# --------------------------------------

# Displays the main menu and handles user selection
display_menu() {
    local yaml_dir="$1"
    local options=("Pod Creation" "Helm Install" "Exit")
    local choice

    print_color "blue" "Please select an option:"
    select choice in "${options[@]}"; do
        case "$REPLY" in
            1) pod_creation "$yaml_dir" ;;
            2) helm_install ;;
            3) print_color "blue" "Exiting..."; exit 0 ;;
            *) print_color "red" "Invalid selection. Please try again." ;;
        esac
    done
}

# --------------------------------------
# Main Function
# --------------------------------------

main() {
    # Check if required commands exist
    check_command "kubectl"
    check_command "helm"

    print_color "yellow" "Kubernetes & Helm Manager Script"

    # Get and ensure YAML directory exists
    local yaml_dir
    yaml_dir=$(get_input "Enter the directory to store YAML files")
    ensure_directory_exists "$yaml_dir"

    # Display the main menu
    display_menu "$yaml_dir"
}

# Run the main function
main