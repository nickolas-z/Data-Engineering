# Spark on Kubernetes - Linode Deployment Guide

## 🚀 Prerequisites

### 1. Linode Account Setup
- Account with billing enabled
- API token for automation (optional)
- SSH key pair for node access

### 2. Local Tools
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Linode CLI (optional)
pip install linode-cli
linode-cli configure
```

---

## 🏗️ Step 1: Create Kubernetes Cluster on Linode

### Option A: Through Linode Cloud Manager (Web UI)
1. **Login to Linode Cloud Manager**
2. **Create Kubernetes Cluster:**
   - Go to "Kubernetes" section
   - Click "Create Cluster"
   - **Region**: Choose closest to you (e.g., Newark, Frankfurt)
   - **Kubernetes Version**: Latest stable (1.28+)
   - **Node Pools:**
     - **Master-compatible nodes**: 2x Linode 4GB (g6-standard-2)
     - **Worker nodes**: 3x Linode 8GB (g6-standard-4) 
   - **Cluster Label**: spark-cluster

### Option B: Through Linode CLI
```bash
# Create cluster
linode-cli lke cluster-create \
  --label SimpleSpark \
  --region nl-ams \
  --k8s_version 1.33 \
  --node_pools.type g6-standard-2 --node_pools.count 3 \
  --node_pools.type g6-standard-4 --node_pools.count 1
```

### Step 2: Download Kubeconfig
```bash
# Download kubeconfig file
# From Linode UI: Cluster -> Download kubeconfig
# Save as ~/.kube/config

# Or via CLI
linode-cli lke kubeconfig-view [CLUSTER_ID] --text --no-headers | base64 -d > ~/.kube/config

```


```shell
#!/usr/bin/bash

# Отримуємо ID створеного кластера
CLUSTER_ID=$(linode-cli lke clusters-list --text --no-headers | grep SimpleSpark | awk '{print $1}')

echo "Кластер створено успішно. ID: $CLUSTER_ID"

# Отримуємо закодований kubeconfig для кластера
ENCODED_KUBECONFIG=$(linode-cli lke kubeconfig-view "$CLUSTER_ID" --json | jq -r '.[0].kubeconfig')

# Декодуємо kubeconfig з Base64 та зберігаємо в файл
echo "$ENCODED_KUBECONFIG" | base64 -d > ~/.kube/config/kubeconfig.yaml

# Налаштування змінної оточення для використання нового kubeconfig
export KUBECONFIG=~/.kube/config/kubeconfig.yaml
```

```
# Test connection
kubectl get nodes
```

Expected output:
```
NAME                         STATUS   ROLES    AGE   VERSION
lke123-456-pool-789-abc      Ready    <none>   5m    v1.33.x
lke123-456-pool-789-def      Ready    <none>   5m    v1.33.x
lke123-456-pool-789-ghi      Ready    <none>   5m    v1.33.x
```

---

## ⚙️ Step 2: Install Spark on Kubernetes

### Method 1: Using Bitnami Helm Chart (Recommended)

```bash
# Add Bitnami repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create namespace
kubectl create namespace spark

# Install Spark cluster
helm install spark bitnami/spark \
  --namespace spark \
  --set master.replicaCount=1 \
  --set worker.replicaCount=3 \
  --set worker.resources.requests.memory="2Gi" \
  --set worker.resources.requests.cpu="1000m" \
  --set worker.resources.limits.memory="4Gi" \
  --set worker.resources.limits.cpu="2000m" \
  --set master.service.type=LoadBalancer \
  --set master.service.ports.http=80

# Check installation
kubectl get pods -n spark
kubectl get services -n spark
```

### Method 2: Custom YAML Deployment

Create `spark-k8s-manifest.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: spark
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-master
  namespace: spark
spec:
  replicas: 1
  selector:
    matchLabels:
      app: spark-master
  template:
    metadata:
      labels:
        app: spark-master
    spec:
      containers:
      - name: spark-master
        image: bitnami/spark:3.5
        ports:
        - containerPort: 7077
        - containerPort: 8080
        env:
        - name: SPARK_MODE
          value: "master"
        - name: SPARK_RPC_AUTHENTICATION_ENABLED
          value: "no"
        - name: SPARK_RPC_ENCRYPTION_ENABLED
          value: "no"
        - name: SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED
          value: "no"
        - name: SPARK_SSL_ENABLED
          value: "no"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: spark-master-service
  namespace: spark
spec:
  type: LoadBalancer
  selector:
    app: spark-master
  ports:
  - name: spark
    port: 7077
    targetPort: 7077
  - name: web
    port: 8080
    targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-worker
  namespace: spark
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spark-worker
  template:
    metadata:
      labels:
        app: spark-worker
    spec:
      containers:
      - name: spark-worker
        image: bitnami/spark:3.5
        env:
        - name: SPARK_MODE
          value: "worker"
        - name: SPARK_MASTER_URL
          value: "spark://spark-master-service:7077"
        - name: SPARK_WORKER_MEMORY
          value: "2g"
        - name: SPARK_WORKER_CORES
          value: "2"
        - name: SPARK_RPC_AUTHENTICATION_ENABLED
          value: "no"
        - name: SPARK_RPC_ENCRYPTION_ENABLED
          value: "no"
        - name: SPARK_LOCAL_STORAGE_ENCRYPTION_ENABLED
          value: "no"
        - name: SPARK_SSL_ENABLED
          value: "no"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

Deploy:
```bash
kubectl apply -f spark-k8s-manifest.yaml
```

---

## 🌐 Step 3: Expose Spark UI

### Get LoadBalancer IP
```bash
# Check service status
kubectl get services -n spark

# Wait for EXTERNAL-IP
kubectl get service spark-master-service -n spark -w
```

### Access Spark Master UI
```bash
# Get external IP
EXTERNAL_IP=$(kubectl get service spark-master-service -n spark -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Spark Master UI: http://$EXTERNAL_IP:8080"
```

### Optional: Setup Ingress with Domain
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: spark-ingress
  namespace: spark
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - spark.yourdomain.com
    secretName: spark-tls
  rules:
  - host: spark.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: spark-master-service
            port:
              number: 8080
```

---

## 🔧 Step 4: Deploy and Run Spark Applications

### Create Spark Job ConfigMap
```bash
# Create sample Python job
cat << 'EOF' > spark-pi.py
from pyspark.sql import SparkSession
import sys

def calculate_pi(partitions):
    spark = SparkSession.builder.appName("PiCalculation").getOrCreate()
    
    def f(_):
        from random import random
        x = random() * 2 - 1
        y = random() * 2 - 1
        return 1 if x ** 2 + y ** 2 <= 1 else 0
    
    n = 100000 * partitions
    count = spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(lambda a, b: a + b)
    pi = 4.0 * count / n
    
    print(f"Pi is roughly {pi}")
    spark.stop()
    return pi

if __name__ == "__main__":
    partitions = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    calculate_pi(partitions)
EOF

# Create ConfigMap
kubectl create configmap spark-jobs -n spark --from-file=spark-pi.py
```

### Deploy Spark Job as Kubernetes Job
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: spark-pi-job
  namespace: spark
spec:
  template:
    spec:
      containers:
      - name: spark-submit
        image: bitnami/spark:3.5
        command: ["/opt/bitnami/spark/bin/spark-submit"]
        args:
        - "--master"
        - "spark://spark-master-service:7077"
        - "--deploy-mode"
        - "client"
        - "--executor-memory"
        - "1g"
        - "--total-executor-cores"
        - "4"
        - "/app/spark-pi.py"
        - "10"
        volumeMounts:
        - name: spark-jobs
          mountPath: /app
      volumes:
      - name: spark-jobs
        configMap:
          name: spark-jobs
      restartPolicy: Never
  backoffLimit: 4
```

Deploy and monitor:
```bash
# Deploy job
kubectl apply -f spark-job.yaml

# Monitor job
kubectl get jobs -n spark
kubectl logs -n spark job/spark-pi-job

# Clean up job
kubectl delete job spark-pi-job -n spark
```

---

## 📊 Step 5: Monitoring and Scaling

### Install Prometheus + Grafana
```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.service.type=LoadBalancer
```

### Auto-scaling Setup
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: spark-worker-hpa
  namespace: spark
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: spark-worker
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 💰 Cost Optimization

### Resource Limits
```yaml
# Optimized resource configuration
worker:
  resources:
    requests:
      memory: "1Gi"      # Start small
      cpu: "500m"
    limits:
      memory: "3Gi"      # Allow burst
      cpu: "1500m"
```

### Node Auto-scaling
```bash
# Enable cluster autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/linode/examples/cluster-autoscaler-autodiscover.yaml
```

### Spot Instances (if available)
```yaml
nodeSelector:
  linode.com/instance-type: "g6-nanode-1"  # Smaller instances
  preemptible: "true"  # Use spot pricing
```

---

## 🔒 Security Best Practices

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: spark-network-policy
  namespace: spark
spec:
  podSelector:
    matchLabels:
      app: spark-worker
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: spark-master
    ports:
    - protocol: TCP
      port: 7077
```

### RBAC Setup
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: spark-service-account
  namespace: spark
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: spark-cluster-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "get", "list", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: spark-cluster-role-binding
subjects:
- kind: ServiceAccount
  name: spark-service-account
  namespace: spark
roleRef:
  kind: ClusterRole
  name: spark-cluster-role
  apiGroup: rbac.authorization.k8s.io
```

---

## ✅ Verification Commands

```bash
# Check cluster health
kubectl get nodes
kubectl top nodes

# Check Spark components
kubectl get pods -n spark
kubectl get services -n spark

# View Spark UI
kubectl port-forward -n spark service/spark-master-service 8080:8080

# Submit test job
kubectl exec -it -n spark deployment/spark-master -- spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --master spark://spark-master-service:7077 \
  examples/jars/spark-examples_2.12-3.5.0.jar 100

# Monitor resource usage
kubectl top pods -n spark
```

