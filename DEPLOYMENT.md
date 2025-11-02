# Deployment Guide

## AWS EC2 Deployment (Step-by-Step)

### Step 1: Create EC2 Instance

1. Go to **AWS Console** → https://console.aws.amazon.com
2. Search for **"EC2"** in the top search bar
3. Click **"Launch Instance"** (orange button)

**Configure Instance:**

| Setting | Value |
|---------|-------|
| **Name** | `codecoach-backend` |
| **AMI** | Ubuntu Server 22.04 LTS |
| **Instance Type** | t2.medium (or t2.small if budget tight) |
| **Key pair** | Create new → Name it `codecoach-key` → Download `.pem` file |

4. Under **Network Settings**, click **"Edit"**
5. Click **"Add security group rule"** twice to add:
   - **Rule 1**: Type: SSH, Port: 22, Source: My IP
   - **Rule 2**: Type: Custom TCP, Port: 8000, Source: Anywhere (0.0.0.0/0)

6. Click **"Launch Instance"** (bottom right)
7. Wait 1-2 minutes, then click **"Connect to instance"**
8. Copy the **Public IPv4 address** (looks like: 54.123.45.67)

---

### Step 2: Connect to EC2

**On Mac/Linux:**
```bash
# Move your key to a safe place
mv ~/Downloads/codecoach-key.pem ~/.ssh/
chmod 400 ~/.ssh/codecoach-key.pem

# Connect (replace with YOUR IP)
ssh -i ~/.ssh/codecoach-key.pem ubuntu@YOUR-EC2-IP
```

**On Windows (PowerShell):**
```powershell
# Connect (replace with YOUR IP)
ssh -i C:\Users\YourName\Downloads\codecoach-key.pem ubuntu@YOUR-EC2-IP
```

Type "yes" when asked about fingerprint.

---

### Step 3: Install Docker (Copy-Paste Each Block)

```bash
# Update system
sudo apt update && sudo apt upgrade -y
```

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

```bash
# Install Docker Compose
sudo apt install docker-compose -y
```

```bash
# Install Git
sudo apt install git -y
```

**Important:** Log out and back in:
```bash
exit
```

Then reconnect:
```bash
ssh -i ~/.ssh/codecoach-key.pem ubuntu@YOUR-EC2-IP
```

---

### Step 4: Deploy Your App

```bash
# Clone your repo
git clone https://github.com/Kavish2040/CodeCoach.git
cd CodeCoach/backend
```

```bash
# Create environment file
nano .env
```

**In the nano editor, paste this (replace with YOUR keys):**
```
OPENAI_API_KEY=sk-proj-your-key-here
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-livekit-key
LIVEKIT_API_SECRET=your-livekit-secret
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

```bash
# Start the application
docker-compose up -d
```

Wait 2-3 minutes for Docker to download and build everything.

---

### Step 5: Test It Works

```bash
# Check if containers are running
docker ps
```

You should see 2 containers: `backend-api-1` and `backend-agent-1`

```bash
# Test the API
curl http://localhost:8000
```

You should see: `{"status":"ok","service":"Interview Coach API"...}`

**Your backend is now live at:** `http://YOUR-EC2-IP:8000`

Test in browser: `http://YOUR-EC2-IP:8000` (replace with your actual IP)

---

### Step 6: View Logs (If Something Goes Wrong)

```bash
# See all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# See only API logs
docker-compose logs api

# See only agent logs
docker-compose logs agent
```

Press `Ctrl + C` to stop following logs.

---

### Common Issues & Fixes

**Problem: "Connection refused"**
```bash
# Check if containers are running
docker ps

# Restart if needed
docker-compose restart
```

**Problem: "Port 8000 already in use"**
```bash
# Stop everything
docker-compose down

# Start again
docker-compose up -d
```

**Problem: Agent keeps crashing**
```bash
# Check agent logs
docker-compose logs agent

# Usually means API keys are wrong - edit .env
nano .env
docker-compose restart
```

---

## Frontend to Vercel (After Backend is Running)

### Step 1: Sign Up for Vercel

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub

---

### Step 2: Deploy Frontend

1. Click **"Add New..."** → **"Project"**
2. Find **"CodeCoach"** in your repo list → Click **"Import"**
3. Configure Project:

| Setting | Value |
|---------|-------|
| **Project Name** | `codecoach` (or whatever you want) |
| **Framework Preset** | Vite |
| **Root Directory** | Click **"Edit"** → Type `frontend` |
| **Build Command** | `npm run build` (auto-filled) |
| **Output Directory** | `dist` (auto-filled) |

4. Click **"Environment Variables"** section
5. Add variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `http://YOUR-EC2-IP:8000` (use your actual EC2 IP!)
6. Click **"Deploy"**

Wait 1-2 minutes. Done! 🎉

Your app is live at: `https://codecoach-xxx.vercel.app`

---

### Step 3: Test Your Live App

1. Open your Vercel URL
2. Click **"Start Call"**
3. Allow microphone access
4. Say: "What are the top easy questions for Meta?"
5. Should work! 🚀

---

## Quick Reference Commands

**On EC2 (SSH into your instance first):**

```bash
# View logs
cd ~/CodeCoach/backend
docker-compose logs -f

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Start everything
docker-compose up -d

# Update code from GitHub
git pull
docker-compose up -d --build
```

**Update Frontend (after changing code):**
```bash
# Just push to GitHub
git add .
git commit -m "Update frontend"
git push

# Vercel auto-deploys! (takes 1-2 min)
```

---

## Costs

- **AWS EC2 t2.medium**: ~$0.05/hour (~$35/month) or use free tier
- **Vercel**: Free for hobby projects
- **LiveKit Cloud**: Free tier (50 concurrent connections)
- **OpenAI API**: Pay per use (~$0.01 per conversation)

**Total for demo**: ~$1-5 depending on usage

---

## When You're Done (Clean Up)

**Stop AWS to avoid charges:**

1. Go to AWS Console → EC2
2. Select your instance
3. **Instance State** → **Stop Instance**
4. (Or **Terminate** to delete completely)

**Vercel stays free** - no need to delete

