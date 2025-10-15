# PyFSD GenAI - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the PyFSD GenAI platform in various environments, from local development to production cloud deployments.

## Prerequisites

### System Requirements
- **CPU**: Minimum 4 cores, Recommended 8+ cores
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 100GB SSD, Recommended 500GB+
- **Network**: Stable internet connection for AI model access

### Software Requirements
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Python**: Version 3.9+
- **Node.js**: Version 16+ (for frontend)
- **Git**: Latest version

## Local Development Deployment

### 1. Clone Repository
```bash
git clone https://github.com/sosravi/pyfsdgenai.git
cd pyfsdgenai
```

### 2. Environment Setup
```bash
# Copy environment template
cp config.env.example .env

# Edit configuration
nano .env
```

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Start Services with Docker
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 5. Initialize Database
```bash
# Run database migrations
python src/core/db_migrations.py

# Create initial admin user
python scripts/create_admin_user.py
```

### 6. Verify Deployment
```bash
# Check API health
curl http://localhost:8000/health

# Check service logs
docker-compose logs -f app
```

## Production Deployment

### AWS Deployment

#### 1. Infrastructure Setup
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

#### 2. Terraform Infrastructure
```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

#### 3. Application Deployment
```bash
# Build Docker image
docker build -t pyfsdgenai:latest .

# Tag for ECR
docker tag pyfsdgenai:latest <account>.dkr.ecr.<region>.amazonaws.com/pyfsdgenai:latest

# Push to ECR
docker push <account>.dkr.ecr.<region>.amazonaws.com/pyfsdgenai:latest

# Deploy to ECS
aws ecs update-service --cluster pyfsdgenai-cluster --service pyfsdgenai-service --force-new-deployment
```

#### 4. Environment Configuration
```bash
# Set environment variables in ECS task definition
export DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/pyfsdgenai"
export REDIS_URL="redis://elasticache-endpoint:6379/0"
export OPENAI_API_KEY="your-openai-key"
```

### Azure Deployment

#### 1. Azure CLI Setup
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login
```

#### 2. Container Registry
```bash
# Create container registry
az acr create --resource-group pyfsdgenai-rg --name pyfsdgenaiacr --sku Basic

# Build and push image
az acr build --registry pyfsdgenaiacr --image pyfsdgenai:latest .
```

#### 3. App Service Deployment
```bash
# Create App Service plan
az appservice plan create --name pyfsdgenai-plan --resource-group pyfsdgenai-rg --sku B1

# Create web app
az webapp create --resource-group pyfsdgenai-rg --plan pyfsdgenai-plan --name pyfsdgenai-app --deployment-container-image-name pyfsdgenaiacr.azurecr.io/pyfsdgenai:latest
```

### Google Cloud Platform Deployment

#### 1. Google Cloud SDK Setup
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Initialize SDK
gcloud init
```

#### 2. Container Registry
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Build and push image
docker build -t gcr.io/PROJECT_ID/pyfsdgenai:latest .
docker push gcr.io/PROJECT_ID/pyfsdgenai:latest
```

#### 3. Cloud Run Deployment
```bash
# Deploy to Cloud Run
gcloud run deploy pyfsdgenai --image gcr.io/PROJECT_ID/pyfsdgenai:latest --platform managed --region us-central1 --allow-unauthenticated
```

## Kubernetes Deployment

### 1. Create Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pyfsdgenai
```

### 2. ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pyfsdgenai-config
  namespace: pyfsdgenai
data:
  APP_NAME: "PyFSD GenAI"
  LOG_LEVEL: "INFO"
  MAX_CONCURRENT_AGENTS: "20"
```

### 3. Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pyfsdgenai-secrets
  namespace: pyfsdgenai
type: Opaque
data:
  DATABASE_URL: <base64-encoded-url>
  OPENAI_API_KEY: <base64-encoded-key>
  SECRET_KEY: <base64-encoded-secret>
```

### 4. Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyfsdgenai-app
  namespace: pyfsdgenai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pyfsdgenai
  template:
    metadata:
      labels:
        app: pyfsdgenai
    spec:
      containers:
      - name: pyfsdgenai
        image: pyfsdgenai:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: pyfsdgenai-config
        - secretRef:
            name: pyfsdgenai-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### 5. Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: pyfsdgenai-service
  namespace: pyfsdgenai
spec:
  selector:
    app: pyfsdgenai
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Database Setup

### PostgreSQL Configuration
```sql
-- Create database
CREATE DATABASE pyfsdgenai;

-- Create user
CREATE USER pyfsdgenai_user WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE pyfsdgenai TO pyfsdgenai_user;
```

### MongoDB Configuration
```javascript
// Create database and collections
use pyfsdgenai;

// Create collections
db.createCollection("contracts");
db.createCollection("invoices");
db.createCollection("processing_jobs");
db.createCollection("agent_results");

// Create indexes
db.contracts.createIndex({ "contract_id": 1 });
db.invoices.createIndex({ "invoice_number": 1 });
db.processing_jobs.createIndex({ "status": 1 });
```

## Monitoring and Logging

### Application Monitoring
```bash
# Install Prometheus
helm install prometheus prometheus-community/prometheus

# Install Grafana
helm install grafana grafana/grafana

# Configure monitoring
kubectl apply -f monitoring/prometheus-config.yaml
kubectl apply -f monitoring/grafana-dashboard.yaml
```

### Log Aggregation
```bash
# Install ELK Stack
docker-compose -f docker-compose.elk.yml up -d

# Configure log shipping
kubectl apply -f logging/fluentd-config.yaml
```

## Security Configuration

### SSL/TLS Setup
```bash
# Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure nginx with SSL
server {
    listen 443 ssl;
    server_name api.pyfsdgenai.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Configuration
```bash
# Configure UFW
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

## Backup and Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U pyfsdgenai_user pyfsdgenai > backup_$(date +%Y%m%d).sql

# MongoDB backup
mongodump --db pyfsdgenai --out /backup/mongodb/$(date +%Y%m%d)
```

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/$DATE"

mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -h localhost -U pyfsdgenai_user pyfsdgenai > $BACKUP_DIR/postgres.sql

# MongoDB backup
mongodump --db pyfsdgenai --out $BACKUP_DIR/mongodb

# Upload to S3
aws s3 sync $BACKUP_DIR s3://pyfsdgenai-backups/$DATE/
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connectivity
docker exec -it pyfsdgenai-db psql -U pyfsdgenai_user -d pyfsdgenai -c "SELECT 1;"

# Check connection string
echo $DATABASE_URL
```

#### 2. AI Agent Failures
```bash
# Check agent logs
docker-compose logs celery-worker

# Restart agents
docker-compose restart celery-worker
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits
# Edit docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_invoices_contract_id ON invoices(contract_id);
CREATE INDEX idx_processing_jobs_created_at ON processing_jobs(created_at);
```

#### 2. Caching Configuration
```python
# Redis caching
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
}
```

## Scaling

### Horizontal Scaling
```yaml
# Scale application pods
kubectl scale deployment pyfsdgenai-app --replicas=5

# Scale database
kubectl scale statefulset postgres --replicas=3
```

### Load Balancing
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pyfsdgenai-ingress
spec:
  rules:
  - host: api.pyfsdgenai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pyfsdgenai-service
            port:
              number: 80
```

## Maintenance

### Regular Maintenance Tasks
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Run database migrations
python src/core/db_migrations.py

# Clean up old logs
find /var/log/pyfsdgenai -name "*.log" -mtime +30 -delete

# Update SSL certificates
certbot renew
```

---

**Deployment Guide Version**: 1.0.0  
**Last Updated**: January 2025  
**Compatible with**: PyFSD GenAI v1.0.0+

