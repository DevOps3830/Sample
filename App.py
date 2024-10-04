from flask import Flask, request, render_template, send_file
import subprocess
import os
import pandas as pd
import tempfile

app = Flask(__name__)

# Directory to store kubeconfig uploads
UPLOAD_FOLDER = "/app/kubeconfigs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set the default kubeconfig path
default_kubeconfig = os.path.join(UPLOAD_FOLDER, "config")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle kubeconfig upload
        kubeconfig = request.files["kubeconfig"]
        kubeconfig_path = os.path.join(UPLOAD_FOLDER, kubeconfig.filename)
        kubeconfig.save(kubeconfig_path)
        
        # Set kubeconfig environment variable
        os.environ["KUBECONFIG"] = kubeconfig_path
        
        return render_template("index.html", message="Kubeconfig uploaded successfully")
    
    return render_template("index.html")

@app.route("/table", methods=["GET"])
def generate_table():
    level = request.args.get("level", "namespace")
    workload_type = request.args.get("workload_type", "all")

    # Check if kubeconfig is available
    if not os.getenv("KUBECONFIG"):
        return "Kubeconfig not set! Please upload a kubeconfig file first."

    # Determine the workload selector
    if workload_type == "deployment":
        workload_filter = "app.kubernetes.io/name=deployment"
    elif workload_type == "statefulset":
        workload_filter = "app.kubernetes.io/name=statefulset"
    elif workload_type == "replicaset":
        workload_filter = "app.kubernetes.io/name=replicaset"
    else:  # Default is all
        workload_filter = ""

    # Generate the command based on the selection
    if level == "namespace":
        command = (
            f"kubectl get pods --all-namespaces -l {workload_filter} -o jsonpath='{{range .items[*]}}{{.metadata.namespace}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.cpu}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.memory}}{{\"\\n\"}}{{end}}' | "
            "awk '{cpu[$1]+=$2; mem[$1]+=$3} END {for (ns in cpu) print ns, cpu[ns], mem[ns]}' | "
            "sort -k2 -hr"
        )
    elif level == "pod":
        command = (
            f"kubectl get pods --all-namespaces -l {workload_filter} -o jsonpath='{{range .items[*]}}{{.metadata.namespace}}{{\"\\t\"}}{{.metadata.name}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.cpu}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.memory}}{{\"\\n\"}}{{end}}' | "
            "sort -k3 -hr"
        )
    else:
        return "Invalid level specified!"

    # Execute the command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, executable="/bin/bash")
    output, _ = process.communicate()
    
    data = []
    # Parse the command output
    if level == "namespace":
        for line in output.decode("utf-8").splitlines():
            if line.strip():
                ns, cpu_req, mem_req = line.split()
                data.append({"Namespace": ns, "CPU Request (m)": cpu_req, "Memory Request (Mi)": mem_req})
        df = pd.DataFrame(data)
    elif level == "pod":
        for line in output.decode("utf-8").splitlines():
            if line.strip():
                ns, pod, cpu_req, mem_req = line.split()
                data.append({"Namespace": ns, "Pod": pod, "CPU Request (m)": cpu_req, "Memory Request (Mi)": mem_req})
        df = pd.DataFrame(data)

    # Render the table in HTML
    return render_template("table.html", tables=[df.to_html(classes='data')], titles=df.columns.values, level=level, workload_type=workload_type)

@app.route("/download_pdf", methods=["GET"])
def download_pdf():
    level = request.args.get("level", "namespace")
    workload_type = request.args.get("workload_type", "all")

    # Determine the workload selector
    if workload_type == "deployment":
        workload_filter = "app.kubernetes.io/name=deployment"
    elif workload_type == "statefulset":
        workload_filter = "app.kubernetes.io/name=statefulset"
    elif workload_type == "replicaset":
        workload_filter = "app.kubernetes.io/name=replicaset"
    else:  # Default is all
        workload_filter = ""

    # Generate the command based on the selection
    if level == "namespace":
        command = (
            f"kubectl get pods --all-namespaces -l {workload_filter} -o jsonpath='{{range .items[*]}}{{.metadata.namespace}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.cpu}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.memory}}{{\"\\n\"}}{{end}}' | "
            "awk '{cpu[$1]+=$2; mem[$1]+=$3} END {for (ns in cpu) print ns, cpu[ns], mem[ns]}' | "
            "sort -k2 -hr"
        )
    elif level == "pod":
        command = (
            f"kubectl get pods --all-namespaces -l {workload_filter} -o jsonpath='{{range .items[*]}}{{.metadata.namespace}}{{\"\\t\"}}{{.metadata.name}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.cpu}}{{\"\\t\"}}{{.spec.containers[*].resources.requests.memory}}{{\"\\n\"}}{{end}}' | "
            "sort -k3 -hr"
        )
    else:
        return "Invalid level specified!"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, executable="/bin/bash")
    output, _ = process.communicate()
    
    data = []
    if level == "namespace":
        for line in output.decode("utf-8").splitlines():
            if line.strip():
                ns, cpu_req, mem_req = line.split()
                data.append({"Namespace": ns, "CPU Request (m)": cpu_req, "Memory Request (Mi)": mem_req})
        df = pd.DataFrame(data)
    elif level == "pod":
        for line in output.decode("utf-8").splitlines():
            if line.strip():
                ns, pod, cpu_req, mem_req = line.split()
                data.append({"Namespace": ns, "Pod": pod, "CPU Request (m)": cpu_req, "Memory Request (Mi)": mem_req})
        df = pd.DataFrame(data)

    # Generate temporary PDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        pdf_path = temp_pdf.name
        df.to_html(pdf_path)

    return send_file(pdf_path, as_attachment=True, download_name=f"resource_report_{level}_{workload_type}.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
