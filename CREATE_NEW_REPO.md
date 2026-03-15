# 🆕 Create New Repository on GitHub

## Step-by-Step Instructions

### Step 1: Create Repository on GitHub

1. **Go to GitHub:**
   - Visit: https://github.com/new
   - Or: https://github.com → Click **"+"** → **"New repository"**

2. **Fill in Details:**
   - **Repository name:** `agents` (or any name you prefer)
   - **Description:** (optional) "AI Agents and Stock Assistant Projects"
   - **Visibility:** 
     - ✅ **Public** (recommended for portfolio)
     - ⚪ Private (if you want it private)
   - **⚠️ IMPORTANT:** 
     - ❌ **DO NOT** check "Add a README file"
     - ❌ **DO NOT** check "Add .gitignore"
     - ❌ **DO NOT** check "Choose a license"
   - (Leave all checkboxes empty)

3. **Click "Create repository"**

### Step 2: Update Your Local Remote

After creating the repo, GitHub will show you commands. Use these:

```bash
cd /Users/maneeshmukundan/projects/agents

# Remove old remote
git remote remove origin

# Add your new repository
git remote add origin https://github.com/maneeshmukundan/agents.git

# Verify
git remote -v
```

### Step 3: Push Your Code

```bash
# Push to your new repository
git push -u origin main
```

If you get an error about branch name, try:
```bash
git push -u origin main:main
```

Or if your branch is called `master`:
```bash
git push -u origin master
```

---

## Quick Commands (Copy & Paste)

```bash
cd /Users/maneeshmukundan/projects/agents
git remote remove origin
git remote add origin https://github.com/maneeshmukundan/agents.git
git remote -v
git push -u origin main
```

---

## Verify It Worked

1. Go to: https://github.com/maneeshmukundan/agents
2. You should see all your files including `stockassistantweb/`
3. No more permission errors!

---

## Next Steps

Once your code is on GitHub:
1. Go to Render.com
2. Connect your new repository: `maneeshmukundan/agents`
3. Deploy your Stock Assistant Web!

