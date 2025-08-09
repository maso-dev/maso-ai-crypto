# 🚀 Deployment Checklist - Masonic AI Crypto Broker

## **📋 Pre-Deployment Checklist**

### **✅ Environment Setup**
- [ ] **Python Environment**: Python 3.9+ installed
- [ ] **Virtual Environment**: Virtual environment created and activated
- [ ] **Dependencies**: All requirements installed (`pip install -r requirements.txt`)
- [ ] **Environment Variables**: `.env` file configured with all necessary API keys
- [ ] **Database Access**: Neo4j and Milvus instances accessible
- [ ] **API Keys**: All required API keys obtained and configured

### **✅ Code Quality Checks**
- [ ] **Linting**: Code passes all linting checks (`flake8`, `black`)
- [ ] **Type Checking**: Type hints validated (`mypy`)
- [ ] **Tests**: All tests passing (`pytest`)
- [ ] **Documentation**: API documentation generated and up-to-date
- [ ] **Security**: No hardcoded secrets or API keys in code

### **✅ Infrastructure Requirements**
- [ ] **Server**: Minimum 2GB RAM, 1 CPU core
- [ ] **Storage**: At least 10GB available disk space
- [ ] **Network**: Outbound internet access for API calls
- [ ] **Ports**: Port 8000 available for FastAPI
- [ ] **SSL Certificate**: Valid SSL certificate for HTTPS (production)

## **🔧 Local Development Deployment**

### **Step 1: Environment Setup**
```bash
# Clone repository
git clone https://github.com/yourusername/maso-ai-crypto.git
cd maso-ai-crypto

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env
```

### **Step 2: Environment Configuration**
```bash
# Edit .env file with your API keys
nano .env

# Required environment variables:
OPENAI_API_KEY=your_openai_key_here
NEWSAPI_API_KEY=your_newsapi_key_here
TAVILY_API_KEY=your_tavily_key_here
LIVECOINWATCH_API_KEY=your_livecoinwatch_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### **Step 3: Database Setup**
```bash
# Start Neo4j (if using Docker)
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

# Start Milvus (if using Docker)
docker run -d \
  --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest
```

### **Step 4: Application Startup**
```bash
# Start the application
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **Step 5: Verification**
- [ ] **Health Check**: `http://localhost:8000/health` returns 200
- [ ] **API Docs**: `http://localhost:8000/docs` accessible
- [ ] **Database Connection**: Neo4j and Milvus connections successful
- [ ] **API Endpoints**: All endpoints responding correctly

## **🌐 Production Deployment**

### **Option 1: Vercel Deployment (Recommended)**

#### **Step 1: Vercel Setup**
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to Vercel
vercel --prod
```

#### **Step 2: Environment Configuration**
```bash
# Set environment variables in Vercel dashboard
vercel env add OPENAI_API_KEY
vercel env add NEWSAPI_API_KEY
vercel env add TAVILY_API_KEY
vercel env add LIVECOINWATCH_API_KEY
vercel env add NEO4J_URI
vercel env add NEO4J_USER
vercel env add NEO4J_PASSWORD
vercel env add MILVUS_HOST
vercel env add MILVUS_PORT
```

#### **Step 3: Custom Domain (Optional)**
```bash
# Add custom domain
vercel domains add yourdomain.com
```

### **Option 2: Docker Deployment**

#### **Step 1: Dockerfile Creation**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **Step 2: Docker Compose Setup**
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEWSAPI_API_KEY=${NEWSAPI_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - LIVECOINWATCH_API_KEY=${LIVECOINWATCH_API_KEY}
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USER=${NEO4J_USER}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - MILVUS_HOST=${MILVUS_HOST}
      - MILVUS_PORT=${MILVUS_PORT}
    depends_on:
      - neo4j
      - milvus
    restart: unless-stopped

  neo4j:
    image: neo4j:latest
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    restart: unless-stopped

  milvus:
    image: milvusdb/milvus:latest
    ports:
      - "19530:19530"
      - "9091:9091"
    volumes:
      - milvus_data:/var/lib/milvus
    restart: unless-stopped

volumes:
  neo4j_data:
  milvus_data:
```

#### **Step 3: Deployment Commands**
```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### **Option 3: Traditional Server Deployment**

#### **Step 1: Server Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx

# Create application user
sudo useradd -m -s /bin/bash cryptoapp
sudo usermod -aG sudo cryptoapp
```

#### **Step 2: Application Setup**
```bash
# Switch to application user
sudo su - cryptoapp

# Clone repository
git clone https://github.com/yourusername/maso-ai-crypto.git
cd maso-ai-crypto

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
nano .env  # Edit with your API keys
```

#### **Step 3: Systemd Service Setup**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/crypto-broker.service
```

```ini
[Unit]
Description=Masonic AI Crypto Broker
After=network.target

[Service]
Type=simple
User=cryptoapp
WorkingDirectory=/home/cryptoapp/maso-ai-crypto
Environment=PATH=/home/cryptoapp/maso-ai-crypto/venv/bin
ExecStart=/home/cryptoapp/maso-ai-crypto/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **Step 4: Nginx Configuration**
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/crypto-broker
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### **Step 5: Enable Services**
```bash
# Enable and start services
sudo systemctl enable crypto-broker
sudo systemctl start crypto-broker
sudo systemctl status crypto-broker

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/crypto-broker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## **🔍 Post-Deployment Verification**

### **Health Checks**
```bash
# Application health
curl -f http://yourdomain.com/health

# API documentation
curl -f http://yourdomain.com/docs

# Database connections
curl -f http://yourdomain.com/api/admin/status
```

### **Performance Monitoring**
```bash
# Check application logs
sudo journalctl -u crypto-broker -f

# Monitor system resources
htop
df -h
free -h

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **Security Verification**
- [ ] **HTTPS**: SSL certificate properly configured
- [ ] **Firewall**: Only necessary ports exposed
- [ ] **API Keys**: No keys exposed in logs or responses
- [ ] **Rate Limiting**: API rate limiting configured
- [ ] **Input Validation**: All endpoints properly validate input

## **🚨 Troubleshooting Guide**

### **Common Issues**

#### **1. Database Connection Failures**
```bash
# Check Neo4j status
curl -f http://localhost:7474

# Check Milvus status
curl -f http://localhost:9091/healthz

# Verify environment variables
echo $NEO4J_URI
echo $MILVUS_HOST
```

#### **2. API Key Issues**
```bash
# Test API keys individually
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Check environment variable loading
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

#### **3. Port Conflicts**
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Kill conflicting process
sudo kill -9 <PID>
```

#### **4. Memory Issues**
```bash
# Check memory usage
free -h

# Check swap usage
swapon --show

# Restart services if needed
sudo systemctl restart crypto-broker
```

## **📊 Monitoring & Maintenance**

### **Log Rotation**
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/crypto-broker

# Add configuration
/home/cryptoapp/maso-ai-crypto/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 cryptoapp cryptoapp
}
```

### **Backup Strategy**
```bash
# Create backup script
nano backup.sh

# Backup database and configuration
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/crypto-broker/$DATE"

mkdir -p $BACKUP_DIR

# Backup Neo4j data
sudo cp -r /var/lib/neo4j/data $BACKUP_DIR/

# Backup application configuration
cp /home/cryptoapp/maso-ai-crypto/.env $BACKUP_DIR/
cp /home/cryptoapp/maso-ai-crypto/config.py $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### **Update Process**
```bash
# Create update script
nano update.sh

#!/bin/bash
cd /home/cryptoapp/maso-ai-crypto

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart crypto-broker

echo "Update completed successfully"
```

## **🎯 Deployment Success Criteria**

### **Functional Requirements**
- [ ] All API endpoints responding correctly
- [ ] Database connections stable
- [ ] Real-time data ingestion working
- [ ] AI analysis functioning properly
- [ ] User interface accessible and responsive

### **Performance Requirements**
- [ ] API response time < 2 seconds
- [ ] Database query time < 1 second
- [ ] Memory usage < 80% of available
- [ ] CPU usage < 70% under normal load
- [ ] Uptime > 99.5%

### **Security Requirements**
- [ ] HTTPS properly configured
- [ ] API keys secured
- [ ] Input validation working
- [ ] Rate limiting active
- [ ] No sensitive data exposed

---

**🎯 This comprehensive deployment checklist addresses all feedback points about deployment complexity and provides clear, step-by-step instructions for multiple deployment scenarios.** 
