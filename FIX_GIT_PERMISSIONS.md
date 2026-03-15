# 🔧 Fix Git Permission Error

## Problem
```
Permission to ed-donner/agents.git denied to maneeshmukundan1379
```

## Solution Options

### Option 1: Fork the Repository (Recommended)

1. **Fork on GitHub:**
   - Go to: https://github.com/ed-donner/agents
   - Click **"Fork"** button (top right)
   - Select your account (`maneeshmukundan1379`)

2. **Update Remote URL:**
   ```bash
   cd /Users/maneeshmukundan/projects/agents
   git remote set-url origin https://github.com/maneeshmukundan1379/agents.git
   ```

3. **Verify:**
   ```bash
   git remote -v
   ```
   Should show: `origin https://github.com/maneeshmukundan1379/agents.git`

4. **Push:**
   ```bash
   git push origin main
   ```

---

### Option 2: Create Your Own Repository

1. **Create New Repo on GitHub:**
   - Go to: https://github.com/new
   - Name: `agents` (or any name)
   - Choose Public/Private
   - **Don't** initialize with README
   - Click **"Create repository"**

2. **Update Remote:**
   ```bash
   cd /Users/maneeshmukundan/projects/agents
   git remote set-url origin https://github.com/maneeshmukundan1379/your-repo-name.git
   ```

3. **Push:**
   ```bash
   git push -u origin main
   ```

---

### Option 3: Add Upstream Remote (Keep Original + Your Fork)

1. **Fork the repo** (see Option 1, step 1)

2. **Add Your Fork as Origin:**
   ```bash
   git remote set-url origin https://github.com/maneeshmukundan1379/agents.git
   ```

3. **Add Original as Upstream:**
   ```bash
   git remote add upstream https://github.com/ed-donner/agents.git
   ```

4. **Verify:**
   ```bash
   git remote -v
   ```
   Should show:
   - `origin` → your fork
   - `upstream` → original repo

5. **Push to Your Fork:**
   ```bash
   git push origin main
   ```

6. **Sync with Original (when needed):**
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

---

## Quick Fix (Choose One)

### If You Already Forked:
```bash
cd /Users/maneeshmukundan/projects/agents
git remote set-url origin https://github.com/maneeshmukundan1379/agents.git
git push origin main
```

### If You Need to Fork First:
1. Go to: https://github.com/ed-donner/agents
2. Click "Fork"
3. Then run the commands above

---

## Verify It Works

After updating remote:
```bash
git remote -v
git push origin main
```

Should work without permission errors!

