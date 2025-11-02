# Deployment Guide

## AWS EC2 Deployment (Simple Docker Setup)

### 1. Launch EC2 Instance

```bash
# Use AWS Console:
# - AMI: Ubuntu 22.04 LTS
# - Instance Type: t2.medium (need memory for agent)
# - Security Group: Allow ports 22 (SSH), 8000 (API)
# - Key pair: Create/use existing
```

### 2. SSH into EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 3. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose -y

# Logout and login again for docker group to take effect
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 4. Deploy Application

```bash
# Clone repo
git clone https://github.com/Kavish2040/CodeCoach.git
cd CodeCoach/backend

# Create .env file
nano .env
# Add your API keys:
# OPENAI_API_KEY=sk-...
# LIVEKIT_URL=wss://...
# LIVEKIT_API_KEY=...
# LIVEKIT_API_SECRET=...

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 5. Verify

```bash
# Test API
curl http://localhost:8000

# Check running containers
docker ps
```

Your backend is now running at: `http://your-ec2-ip:8000`

---

## Frontend to Vercel

### 1. Push Latest Code

```bash
git add .
git commit -m "Add deployment configs"
git push
```

### 2. Deploy to Vercel

1. Go to https://vercel.com
2. Click "New Project"
3. Import `Kavish2040/CodeCoach` from GitHub
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Environment Variables**:
     - `VITE_API_URL` = `http://your-ec2-ip:8000`
5. Click "Deploy"

Done! Your app is live.

---

## Quick Commands

```bash
# On EC2 - View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update code
git pull
docker-compose up -d --build
```

