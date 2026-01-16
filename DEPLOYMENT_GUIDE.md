# License Plate Scanning System - Deployment Guide

## Production Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Prerequisites
- Docker Desktop for Windows
- Docker Compose
- At least 4GB RAM available
- 10GB disk space

#### Steps

1. **Prepare Environment Files**

```powershell
# Backend
cd backend
Copy-Item .env.example .env
# Edit .env for production settings

# Python Service
cd ..\python-service
Copy-Item .env.example .env
# Update camera URLs and API endpoints
```

2. **Build and Deploy**

```powershell
# From project root
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

3. **Access Services**
- Frontend: http://localhost:4200
- Backend API: http://localhost:3000
- MongoDB: localhost:27017

4. **Maintenance Commands**

```powershell
# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Update and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View logs for specific service
docker-compose logs -f python-service

# Remove everything (including volumes)
docker-compose down -v
```

---

### Option 2: Windows Server Deployment

#### Prerequisites
- Windows Server 2019 or later
- IIS (for frontend hosting)
- Node.js 18+ LTS
- Python 3.10+
- MongoDB 5.0+

#### Backend Deployment

1. **Install Node.js as Windows Service**

```powershell
# Install PM2 globally
npm install -g pm2
npm install -g pm2-windows-startup

# Configure PM2 to start on boot
pm2-startup install

# Start backend
cd c:\Apps\license-plate-backend
npm install --production
pm2 start src/server.js --name lp-backend
pm2 save
```

2. **Configure Windows Firewall**

```powershell
New-NetFirewallRule -DisplayName "License Plate API" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

#### Python Service Deployment

```powershell
# Install as Windows Service using NSSM
# Download NSSM from https://nssm.cc/download

# Install service
nssm install LicensePlateDetector "C:\Python310\python.exe" "c:\Apps\license-plate-detector\main.py --source rtsp"
nssm set LicensePlateDetector AppDirectory "c:\Apps\license-plate-detector"
nssm set LicensePlateDetector AppStdout "c:\Apps\logs\detector-output.log"
nssm set LicensePlateDetector AppStderr "c:\Apps\logs\detector-error.log"

# Start service
nssm start LicensePlateDetector
```

#### Frontend Deployment with IIS

1. **Build Angular App**

```powershell
cd frontend
npm run build
```

2. **Configure IIS**

```powershell
# Install IIS URL Rewrite Module first
# Then create web.config in dist folder
```

Create `web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Angular Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
    <staticContent>
      <mimeMap fileExtension=".json" mimeType="application/json" />
    </staticContent>
  </system.webServer>
</configuration>
```

---

### Option 3: Cloud Deployment (Azure)

#### Azure Resources Needed
- Azure App Service (Backend)
- Azure Static Web Apps (Frontend)
- Azure Cosmos DB (MongoDB API) or Azure VM with MongoDB
- Azure Container Instances (Python Service)

#### Deploy Backend to Azure App Service

```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login
az login

# Create resource group
az group create --name LicensePlateRG --location eastus

# Create App Service Plan
az appservice plan create --name LicensePlatePlan --resource-group LicensePlateRG --sku B1 --is-linux

# Create Web App
az webapp create --name license-plate-api --resource-group LicensePlateRG --plan LicensePlatePlan --runtime "NODE:18-lts"

# Configure environment variables
az webapp config appsettings set --name license-plate-api --resource-group LicensePlateRG --settings MONGODB_URI="your-connection-string"

# Deploy code
cd backend
az webapp up --name license-plate-api --resource-group LicensePlateRG
```

#### Deploy Frontend to Azure Static Web Apps

```powershell
# Install Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Build
cd frontend
npm run build

# Deploy
swa deploy --app-location dist/license-plate-dashboard --env production
```

---

### Option 4: Raspberry Pi / Edge Device Deployment

For edge computing scenarios:

#### Hardware Requirements
- Raspberry Pi 4 (4GB+ RAM recommended)
- MicroSD card (32GB+)
- Power supply
- Network connection

#### Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3-pip nodejs npm mongodb tesseract-ocr

# Install Python packages
cd /home/pi/license-plate-detector
pip3 install -r requirements.txt

# Install backend dependencies
cd /home/pi/license-plate-backend
npm install --production

# Configure to start on boot
sudo nano /etc/systemd/system/lp-backend.service
```

Create service file:

```ini
[Unit]
Description=License Plate Backend API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/license-plate-backend
ExecStart=/usr/bin/node src/server.js
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable lp-backend
sudo systemctl start lp-backend
```

---

## Security Hardening

### 1. Enable HTTPS

#### For IIS
```powershell
# Bind SSL certificate
New-IISSiteBinding -Name "LicensePlate" -BindingInformation "*:443:" -Protocol https -CertificateThumbprint "YOUR_CERT_THUMBPRINT"
```

#### For Node.js Backend
```javascript
// Add to server.js
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('path/to/private-key.pem'),
  cert: fs.readFileSync('path/to/certificate.pem')
};

https.createServer(options, app).listen(443);
```

### 2. Environment Variables Security

```powershell
# Use Azure Key Vault or similar
$env:MONGODB_URI = "encrypted-connection-string"
```

### 3. Rate Limiting

Add to backend:

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

### 4. Authentication

Implement JWT authentication:

```javascript
const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
};

app.use('/api/plates', authMiddleware, plateRoutes);
```

---

## Monitoring & Logging

### 1. Application Insights (Azure)

```powershell
npm install applicationinsights
```

```javascript
const appInsights = require('applicationinsights');
appInsights.setup('YOUR_INSTRUMENTATION_KEY').start();
```

### 2. Winston Logging

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

### 3. Health Check Endpoint

Already implemented at `/health`

---

## Backup & Recovery

### MongoDB Backup

```powershell
# Automated backup script
$date = Get-Date -Format "yyyyMMdd_HHmmss"
mongodump --uri="mongodb://localhost:27017/license_plates" --out="C:\Backups\mongodb_$date"

# Schedule with Task Scheduler
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-File C:\Scripts\backup-mongodb.ps1'
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "MongoDB Backup" -Description "Daily MongoDB backup"
```

---

## Performance Optimization

### 1. MongoDB Indexes

Already implemented in Plate model

### 2. Caching with Redis

```powershell
docker run -d -p 6379:6379 redis
```

```javascript
const redis = require('redis');
const client = redis.createClient();

// Cache statistics
app.get('/api/plates/statistics', async (req, res) => {
  const cached = await client.get('stats');
  if (cached) return res.json(JSON.parse(cached));
  
  const stats = await Plate.getStats();
  await client.setEx('stats', 300, JSON.stringify(stats)); // Cache for 5 minutes
  res.json(stats);
});
```

### 3. Load Balancing

Use Nginx or Azure Load Balancer for multiple backend instances.

---

## Scaling

### Horizontal Scaling

Deploy multiple backend instances behind a load balancer:

```yaml
# docker-compose-scaled.yml
services:
  backend:
    deploy:
      replicas: 3
```

### Vertical Scaling

Increase resources for intensive tasks:

```yaml
services:
  python-service:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Maintenance

### Update Dependencies

```powershell
# Backend
cd backend
npm update
npm audit fix

# Frontend
cd frontend
npm update
npm audit fix

# Python
cd python-service
pip install --upgrade -r requirements.txt
```

### Database Maintenance

```javascript
// Cleanup old records (add to scheduled task)
const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
await Plate.deleteMany({ timestamp: { $lt: thirtyDaysAgo }, verified: false });
```

---

## Troubleshooting Production Issues

### View Logs

```powershell
# Docker logs
docker-compose logs -f --tail=100

# Windows Service logs
Get-EventLog -LogName Application -Source "License Plate*" -Newest 50

# PM2 logs
pm2 logs lp-backend
```

### Performance Monitoring

```powershell
# Check resource usage
docker stats

# Check MongoDB performance
mongo
> db.currentOp()
> db.serverStatus()
```

---

## Disaster Recovery Plan

1. **Regular Backups**: Daily MongoDB backups
2. **Snapshot Images**: Docker images stored in registry
3. **Configuration Backup**: Store .env files securely
4. **Documentation**: Keep deployment procedures updated
5. **Testing**: Regular disaster recovery drills

---

## Production Checklist

- [ ] All .env files configured with production values
- [ ] HTTPS enabled
- [ ] Authentication implemented
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backups automated
- [ ] Firewall rules configured
- [ ] Error handling tested
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Recovery procedures tested

---

**Your License Plate Scanning System is now production-ready!** 🚀
