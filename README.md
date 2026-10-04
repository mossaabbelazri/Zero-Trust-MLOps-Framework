# 🛡️ Zero-Trust MLOps Framework for Kubernetes

> An enterprise-grade, generic DevSecOps architecture for securely deploying any Machine Learning model on Google Kubernetes Engine (GKE) with SOAR (Security Orchestration, Automation, and Response) auto-remediation.

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-Jenkins-D24939?logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![IaC](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Cloud](https://img.shields.io/badge/Cloud-Google%20Cloud-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/)
[![Service Mesh](https://img.shields.io/badge/Service%20Mesh-Istio-466BB0?logo=istio&logoColor=white)](https://istio.io/)
[![Secrets](https://img.shields.io/badge/Secrets-HashiCorp%20Vault-FFEC6E?logo=vault&logoColor=black)](https://www.vaultproject.io/)
[![Monitoring](https://img.shields.io/badge/Monitoring-Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![ML](https://img.shields.io/badge/ML-MLflow%20%2B%20FastAPI-0194E2?logo=mlflow&logoColor=white)](https://mlflow.org/)

---

## 🌟 Overview

Deploying Machine Learning models to production is challenging. Securing them against lateral movement, supply chain attacks, and data exfiltration is even harder. 

This repository provides a **fully automated, Secure-by-Design MLOps framework**. It allows AI Engineers and Data Scientists to deploy *any* ML model (NLP, Computer Vision, Fraud Detection, or NIDS) behind a military-grade security perimeter without worrying about the underlying infrastructure.

### 🔥 Key Features

1. **Universal ML Serving:** Built with `FastAPI` and `mlflow.pyfunc`, the serving API automatically adapts to any ML framework (Scikit-Learn, XGBoost, PyTorch, TensorFlow).
2. **Shift-Left Security:** Automated CI/CD pipeline featuring SAST (SonarQube), Container Vulnerability Scanning (Trivy), and IaC Scanning (tfsec).
3. **Zero-Trust Networking:**
   - **Layer 7:** Strict mTLS enforced by **Istio Service Mesh**.
   - **Layer 4:** Physical network isolation via **Calico Network Policies**.
4. **Dynamic Secrets (Just-in-Time):** Credentials injected directly into memory by **HashiCorp Vault**. No secrets in code or environment variables.
5. **SOAR Auto-Remediation:** Prometheus continuously monitors the mesh for Layer 7 attacks. If an anomaly is detected (e.g., massive 403/503 Istio rejections), a Jenkins Webhook triggers a Calico network quarantine policy, isolating the attacker into a forensic observation cage instantly.

---

## 🏗️ Architecture

![Architecture](architecture détaillé.png)

---

## 🚀 Quickstart

### 1. Register your Model in MLflow
Train your model (any framework) and register it in your MLflow tracking server:
```python
import mlflow

# Train your model...
# Log it to MLflow
mlflow.sklearn.log_model(sk_model, "model", registered_model_name="MyGenericModel")
```

### 2. Configure the Deployment
Edit the `k8s/ml-deployment.yaml` file to point to your MLflow model:
```yaml
env:
  - name: MODEL_NAME
    value: "MyGenericModel"
  - name: MODEL_STAGE
    value: "Production"
  - name: ANOMALY_THRESHOLD
    value: "0.5" # Optional: for generic anomaly monitoring
```

### 3. Production Deployment (GKE)
For a full enterprise deployment, ensure you have Google Cloud SDK installed and authenticated. 

1. **Initialize Terraform**:
   ```bash
   cd terraform
   terraform init
   terraform apply -auto-approve
   ```
2. **Trigger CI/CD Pipeline**:
   Push your code to the `main` branch. The Jenkins pipeline (`Jenkinsfile`) will automatically:
   - Scan the Python code (SonarQube).
   - Build and scan the generic Docker image (Trivy).
   - Inject HashiCorp Vault sidecars.
   - Deploy Istio in `STRICT` mTLS mode and serve your model securely!

---

## 💻 Local Testing (For Researchers & Evaluators)

If you want to evaluate the generalized API locally without provisioning a Kubernetes cluster, you can run the FastAPI application directly:

1. **Navigate to the application folder:**
   ```bash
   cd ml-app
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the local server (Mocking MLflow):**
   ```bash
   # Linux/macOS
   MLFLOW_TRACKING_URI="file:///tmp/mock" uvicorn main:app --reload

   # Windows (PowerShell)
   $env:MLFLOW_TRACKING_URI="file:///C:/mock"; uvicorn main:app --reload
   ```
4. **View the Swagger UI:**
   Open `http://127.0.0.1:8000/docs` in your browser. The API will gracefully enter *Degraded Mode* (since the mock MLflow URI is empty) while keeping all inference routes accessible for testing.

---

## 📂 Repository Structure

```text
.
├── Jenkinsfile                 # DevSecOps Pipeline
├── Jenkinsfile.remediation     # SOAR Auto-remediation Pipeline
├── ml-app/                     # Generic FastAPI ML Serving Application
│   ├── main.py                 # Dynamic MLflow PyFunc loading
│   └── Dockerfile              # Non-root secure container
├── k8s/                        # Kubernetes Manifests
│   ├── ml-deployment.yaml      # Model Deployment & Istio config
│   ├── ml-backendconfig.yaml   # Google Cloud Armor WAF integration
│   └── quarantine-networkpolicy.yaml # SOAR Forensic Cage
├── terraform/                  # GKE Cluster Provisioning
└── prometheus-rules.yml        # Zero-Trust Anomaly Detection Rules
```

---

## 🛡️ The SOAR Loop (Self-Healing)
If an attacker manages to bypass the WAF and attempts a lateral movement or DoS attack, Istio blocks the unauthenticated requests. 
**Prometheus** detects the spike in 403/503 errors and fires an alert. **Alertmanager** calls the `Jenkinsfile.remediation` webhook, which applies `quarantine-networkpolicy.yaml`, physically cutting the attacker's pod Egress traffic via Calico. The threat is neutralized automatically in seconds.

---
*Created as part of an advanced AI Security & Cloud Engineering research project.*
