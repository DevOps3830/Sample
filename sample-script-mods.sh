#!/bin/bash

# Function to handle colors
function print_color {
    local color=$1
    local message=$2
    case $color in
        "red") echo -e "\033[31m$message\033[0m" ;;
        "green") echo -e "\033[32m$message\033[0m" ;;
        "yellow") echo -e "\033[33m$message\033[0m" ;;
        "blue") echo -e "\033[34m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# Function to display the menu
function display_menu {
    local options=("$@")
    local highlight=0
    local key

    while true; do
        clear
        print_color "yellow" "Select a module using the arrow keys:"
        
        for i in "${!options[@]}"; do
            if [ $i -eq $highlight ]; then
                print_color "green" ">> ${options[$i]}"
            else
                print_color "blue" "   ${options[$i]}"
            fi
        done

        # Get key input
        read -rsn1 key
        case $key in
            $'\x1b') # Handle arrow keys
                read -rsn2 -t 0.1 key
                case $key in
                    '[A') # Up arrow
                        ((highlight--))
                        if [ $highlight -lt 0 ]; then
                            highlight=$((${#options[@]} - 1))
                        fi
                        ;;
                    '[B') # Down arrow
                        ((highlight++))
                        if [ $highlight -ge ${#options[@]}; then
                            highlight=0
                        fi
                        ;;
                esac
                ;;
            '') # Enter key
                return $highlight
                ;;
        esac
    done
}

# Function to input main cluster name
function input_main_cluster {
    read -p "Enter the main cluster name: " main_cluster
    echo "Main Cluster: $main_cluster"
}

# Function to input data clusters
function input_data_clusters {
    local data_clusters=()
    while true; do
        read -p "Enter a data cluster name (or type 'done' to finish): " data_cluster
        if [ "$data_cluster" == "done" ]; then
            break
        fi
        data_clusters+=("$data_cluster")
    done
    echo "Data Clusters:"
    for cluster in "${data_clusters[@]}"; do
        echo "- $cluster"
    done
}

# Main script execution
modules=("Module 1" "Module 2" "Module 3" "Module 4")

# Show the menu and get selection
display_menu "${modules[@]}"
selected_module=$?

clear
echo "You selected: ${modules[$selected_module]}"
case $selected_module in
    0) 
        print_color "red" "Module 1 selected"
        input_main_cluster
        input_data_clusters
        ;;
    1)
        print_color "green" "Module 2 selected"
        input_main_cluster
        input_data_clusters
        ;;
    2)
        print_color "blue" "Module 3 selected"
        input_main_cluster
        input_data_clusters
        ;;
    3)
        print_color "yellow" "Module 4 selected"
        input_main_cluster
        input_data_clusters
        ;;
    *)
        print_color "red" "Invalid selection"
        ;;
esac