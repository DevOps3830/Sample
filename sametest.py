import os
import yaml
import subprocess

def print_color(color, message):
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{message}{colors['reset']}")

def get_user_input(prompt):
    return input(f"{prompt}: ")

def input_params(param_name, is_list=False):
    if is_list:
        values = []
        while True:
            value = get_user_input(f"Enter a value for {param_name} (or type 'done' to finish)")
            if value == "done":
                break
            values.append(value)
        return values
    else:
        return get_user_input(f"Enter a value for {param_name}")

def apply_k8s_config(config_file):
    # Preview YAML
    print_color("yellow", f"Previewing YAML for {config_file}:")
    subprocess.run(["kubectl", "apply", "-f", config_file, "-o", "yaml"], check=False)

    while True:
        user_input = input("Do you want to apply this configuration? (y/n/edit): ").lower()
        if user_input == 'y':
            subprocess.run(["kubectl", "apply", "-f", config_file], check=False)
            print_color("green", "Applied configuration.")
            break
        elif user_input == 'n':
            print_color("red", "Cancelled applying configuration.")
            break
        elif user_input == "edit":
            subprocess.run(["nano", config_file], check=False)
        else:
            print_color("red", "Invalid option. Please type y, n, or edit.")

def create_pod_yaml(pod_name, pod_namespace, pod_yaml_path):
    pod_yaml = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "namespace": pod_namespace
        },
        "spec": {
            "containers": [{
                "name": f"{pod_name}-container",
                "image": "nginx",
                "ports": [{
                    "containerPort": 80
                }]
            }]
        }
    }
    
    with open(pod_yaml_path, 'w') as f:
        yaml.dump(pod_yaml, f)
    
    print_color("green", f"YAML configuration created for Pod: {pod_name} in namespace: {pod_namespace}")

def helm_install_chart(release_name, chart_name, namespace):
    # Run Helm install command
    helm_command = ["helm", "install", release_name, chart_name, "--namespace", namespace]
    
    try:
        print_color("yellow", f"Installing Helm chart: {chart_name} with release name: {release_name} in namespace: {namespace}")
        subprocess.run(helm_command, check=True)
        print_color("green", f"Helm chart {chart_name} installed successfully.")
    except subprocess.CalledProcessError as e:
        print_color("red", f"Error installing Helm chart: {e}")

def main():
    # Ask for directory name to store YAML files
    yaml_dir = get_user_input("Enter the directory name to store all YAML files")
    
    # Create the directory if it doesn't exist
    os.makedirs(yaml_dir, exist_ok=True)

    # Modules list
    modules = [
        "Cluster Management",
        "Data Processing",
        "Backup & Restore",
        "Monitoring",
        "Pod Creation",
        "Helm Install"  # New module for Helm installation
    ]
    
    # Display module selection menu
    print_color("yellow", "Select a module:")
    for i, module in enumerate(modules):
        print(f"{i + 1}. {module}")
    
    selected_module = int(input("Enter the module number: ")) - 1
    if selected_module not in range(len(modules)):
        print_color("red", "Invalid selection")
        return

    print_color("green", f"You selected: {modules[selected_module]}")
    
    # Handle selected module
    if selected_module == 0:
        # Cluster Management
        main_cluster = input_params("Main Cluster")
        data_clusters = input_params("Data Clusters", is_list=True)
        config_file = os.path.join(yaml_dir, "cluster_management.yaml")
        # Simulate a YAML file (This would be more dynamic based on real requirements)
        with open(config_file, 'w') as f:
            f.write(f"main_cluster: {main_cluster}\ndata_clusters:\n")
            for cluster in data_clusters:
                f.write(f"  - {cluster}\n")
        apply_k8s_config(config_file)
        
    elif selected_module == 1:
        # Data Processing
        process_name = input_params("Process Name")
        data_sources = input_params("Data Sources", is_list=True)
        config_file = os.path.join(yaml_dir, "data_processing.yaml")
        # Simulate a YAML file
        with open(config_file, 'w') as f:
            f.write(f"process_name: {process_name}\ndata_sources:\n")
            for source in data_sources:
                f.write(f"  - {source}\n")
        apply_k8s_config(config_file)
    
    elif selected_module == 2:
        # Backup & Restore
        backup_name = input_params("Backup Name")
        volumes = input_params("Volumes", is_list=True)
        config_file = os.path.join(yaml_dir, "backup_restore.yaml")
        # Simulate a YAML file
        with open(config_file, 'w') as f:
            f.write(f"backup_name: {backup_name}\nvolumes:\n")
            for volume in volumes:
                f.write(f"  - {volume}\n")
        apply_k8s_config(config_file)
    
    elif selected_module == 3:
        # Monitoring
        monitor_name = input_params("Monitor Name")
        services = input_params("Services", is_list=True)
        config_file = os.path.join(yaml_dir, "monitoring.yaml")
        # Simulate a YAML file
        with open(config_file, 'w') as f:
            f.write(f"monitor_name: {monitor_name}\nservices:\n")
            for service in services:
                f.write(f"  - {service}\n")
        apply_k8s_config(config_file)
    
    elif selected_module == 4:
        # Pod Creation
        pod_name = input_params("Pod Name")
        pod_namespace = input_params("Pod Namespace")
        config_file = os.path.join(yaml_dir, f"pod_{pod_name}.yaml")
        create_pod_yaml(pod_name, pod_namespace, config_file)
        apply_k8s_config(config_file)

    elif selected_module == 5:
        # Helm Install
        release_name = input_params("Helm Release Name")
        chart_name = input_params("Helm Chart Name")
        namespace = input_params("Namespace")
        helm_install_chart(release_name, chart_name, namespace)

if __name__ == "__main__":
    main()