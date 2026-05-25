# 08 — Git Submodules Workflow

> Guide for working with lab-11, which is hosted on GitLab as a submodule.

---

## Why two repositories?

### Main Repository (GitHub)
- **URL:** `https://github.com/krvax/epam-aws-devops-prep`
- **Purpose:** Preparation material, documentation, labs.
- **Visibility:** Public, for portfolio display.

### Lab-11 Repository (GitLab)
- **URL:** `https://gitlab.com/krvax/gitlab-oidc`
- **Purpose:** GitLab CI/CD lab with OIDC.
- **Reason:** GitLab CI only works within GitLab repositories.

---

## Submodule Architecture

```
epam-aws-devops-prep/ (GitHub)
│
├── labs/
│   ├── lab-01-vpc/           ← Code directly on GitHub
│   ├── lab-02-iam/           ← Code directly on GitHub
│   ├── ...
│   └── lab-11-gitlab-oidc-mini/  ← GIT SUBMODULE → GitLab
│       ├── .git/             ← Points to gitlab.com/krvax/gitlab-oidc
│       ├── app/
│       ├── terraform/
│       └── .gitlab-ci.yml    ← This file must be on GitLab
│
└── .gitmodules               ← Submodule configuration
```

---

## Essential Commands

### 1. Cloning the repo with submodules

```bash
# First time
git clone --recurse-submodules https://github.com/krvax/epam-aws-devops-prep

# If you already cloned without --recurse-submodules
cd epam-aws-devops-prep
git submodule init
git submodule update
```

---

### 2. Viewing submodule status

```bash
# See which submodules you have
git submodule status

# View configuration
cat .gitmodules

# View current commit of the submodule
cd labs/lab-11-gitlab-oidc-mini
git log -1
```

---

### 3. Updating the submodule to the latest version

```bash
# From the root of the main repo
git submodule update --remote labs/lab-11-gitlab-oidc-mini

# Verify what changed
git status
# You will see: modified: labs/lab-11-gitlab-oidc-mini (new commits)

# Commit the change in the main repo
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 to latest version"
git push origin main
```

---

### 4. Making changes in lab-11

#### Option A: Work directly within the submodule

```bash
# 1. Enter the submodule
cd labs/lab-11-gitlab-oidc-mini

# 2. Ensure you are on main
git checkout main
git pull origin main

# 3. Make changes
vim app/app.py

# 4. Commit and push to GitLab
git add .
git commit -m "feat: add new endpoint"
git push origin main

# 5. Return to the main repo
cd ../..

# 6. Update the submodule reference
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 submodule reference"
git push origin main
```

#### Option B: Clone the GitLab repo separately

```bash
# Clone into another folder
cd ~/src/learning/EPAM/
git clone git@gitlab.com:krvax/gitlab-oidc.git lab-11-standalone

# Work there
cd lab-11-standalone
# ... make changes ...
git push origin main

# Then update the submodule in the main repo
cd ~/src/learning/EPAM/epam-aws-devops-prep/
git submodule update --remote labs/lab-11-gitlab-oidc-mini
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: sync lab-11 submodule"
git push origin main
```

---

### 5. Syncing changes between repos

```bash
# Full flow:

# 1. Make changes on GitLab (lab-11)
cd labs/lab-11-gitlab-oidc-mini
git pull origin main
# ... make changes ...
git push origin main

# 2. Update reference on GitHub (main repo)
cd ../..
git submodule update --remote labs/lab-11-gitlab-oidc-mini
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 submodule"
git push origin main
```

---

## Troubleshooting

### Problem: "The submodule is empty"

```bash
# Solution
git submodule init
git submodule update
```

---

### Problem: "Unsaved changes in the submodule"

```bash
# View what changed
cd labs/lab-11-gitlab-oidc-mini
git status

# Option 1: Commit the changes
git add .
git commit -m "fix: save changes"
git push origin main

# Option 2: Discard changes
git reset --hard HEAD
```

---

### Problem: "Submodule points to an old commit"

```bash
# Update to the latest version
git submodule update --remote labs/lab-11-gitlab-oidc-mini

# Commit the change
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11 to latest"
git push origin main
```

---

### Problem: "Conflict when pulling"

```bash
# If the submodule has conflicts
cd labs/lab-11-gitlab-oidc-mini
git status
git pull origin main
# ... resolve conflicts ...
git push origin main

# Return to main repo
cd ../..
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: resolve lab-11 conflicts"
git push origin main
```

---

## Alternatives Considered

### 1. Duplicating code (NOT recommended)

```
❌ Pros:
- Simpler for new users
- No submodule knowledge required

❌ Cons:
- Duplicate maintenance
- Easy to go out of sync
- Changes in one repo aren't reflected in the other
```

### 2. Everything on GitLab (NOT recommended)

```
❌ Pros:
- Everything in one place
- No submodules needed

❌ Cons:
- Lose GitHub visibility
- GitHub is more common for portfolios
- GitLab has less traffic for public projects
```

### 3. Git Submodule (RECOMMENDED) ⭐

```
✅ Pros:
- Best of both worlds
- Each repo on its correct platform
- Easy to maintain with git submodule update
- Changes are explicitly synced

⚠️ Cons:
- Users must know how to use submodules
- Requires two steps to update (GitLab + GitHub)
```

---

## Best Practices

### 1. Always commit in the submodule first

```bash
# ✅ CORRECT
cd labs/lab-11-gitlab-oidc-mini
git add .
git commit -m "feat: new feature"
git push origin main

cd ../..
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: update lab-11"
git push origin main
```

```bash
# ❌ INCORRECT (committing in main repo without submodule commit)
cd labs/lab-11-gitlab-oidc-mini
# ... make changes but no commit ...

cd ../..
git add labs/lab-11-gitlab-oidc-mini  # ← This does not save submodule changes
git commit -m "update lab-11"
```

---

### 2. Keep the submodule updated

```bash
# Every time someone updates lab-11 on GitLab
git submodule update --remote labs/lab-11-gitlab-oidc-mini
git add labs/lab-11-gitlab-oidc-mini
git commit -m "chore: sync lab-11"
git push origin main
```

---

### 3. Document in the README

The main README should explain:
- That lab-11 is a submodule.
- Why it is on GitLab.
- How to clone with submodules.
- How to update the submodule.

---

## Interview Questions

### "Why do you use Git submodules?"

```
"Lab-11 demonstrates GitLab CI/CD with OIDC, so it must be on GitLab for the pipeline to function. I use git submodule to keep all preparation material in one place (GitHub) while allowing lab-11 to function independently on GitLab. This gives me the best of both worlds: GitHub visibility and GitLab CI functionality."
```

### "What alternatives did you consider?"

```
"I considered duplicating the code in both repos, but that creates duplicate maintenance. I also considered moving everything to GitLab, but GitHub has more visibility for portfolios. Git submodule is the correct solution because it maintains the necessary separation while allowing centralized management."
```

### "How do you handle synchronization?"

```
"When I make changes in lab-11, I first commit and push them to GitLab. Then, in the main GitHub repo, I run 'git submodule update --remote' to update the reference to the latest submodule commit. Finally, I commit that change on GitHub. This keeps both repos explicitly synced."
```

---

## Resources

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub: Working with Submodules](https://github.blog/2016-02-01-working-with-submodules/)
- [Atlassian: Git Submodules](https://www.atlassian.com/git/tutorials/git-submodule)

---

**Last updated:** 2026-04-13

---

## 📖 Navigation

- **⬅️ Previous:** [07-kubernetes-deep-dive.en.md](./07-kubernetes-deep-dive.en.md) — Kubernetes Deep Dive
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
