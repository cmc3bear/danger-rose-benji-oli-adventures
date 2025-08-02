# Repository Setup & Branch Protection

This document outlines the complete repository setup including branch protection, merge settings, and Dependabot configuration.

## 🔧 Repository Configuration

### Pull Request Settings
Navigate to **Settings** → **General** → **Pull Requests**:

- ✅ **Allow auto-merge** (enables automatic merging when all checks pass)
- ✅ **Allow squash merging** (ONLY - creates clean history)
- ❌ **Allow merge commits** (DISABLE - prevents merge commits)
- ❌ **Allow rebase merging** (DISABLE - use squash only)

### Main Branch Protection
Navigate to **Settings** → **Branches** → **Add rule** for `main` branch:

#### Branch name pattern
- `main`

#### Protection Rules
- ✅ **Require a pull request before merging**
  - ✅ Require approvals: `1`
  - ✅ Dismiss stale PR approvals when new commits are pushed
  - ✅ Require review from code owners (CODEOWNERS)
  - ✅ Restrict pushes that create files to GitHub Apps

- ✅ **Require status checks to pass before merging**
  - ✅ Require branches to be up to date before merging
  - **Required status checks:**
    - `Enforce commit standards`
    - `Security scanning` (early security gate)
    - `Run pytest CI/CD tests (3.11, ubuntu-latest)`
    - `Run pytest CI/CD tests (3.12, ubuntu-latest)`

    **Note:** Security scanning now runs early (after pre-commit) to provide fast feedback and prevent AWS deployment of insecure code.

- ✅ **Require linear history** (NEW - prevents merge commits, enforces rebasing)

- ✅ **Require conversation resolution before merging**

- ✅ **Restrict pushes to matching branches**
  - ✅ Restrict pushes to matching branches to administrators only

### Optional Enhancements 🔧

- ✅ **Allow force pushes to matching branches** (disabled for safety)
- ✅ **Allow deletions to matching branches** (disabled for safety)
- ✅ **Lock branch** (optional - prevents all changes except via PR)

## Why These Settings?

### Linear History Benefits
- **No merge commits**: Clean, linear git history that's easy to follow
- **Forced conflict resolution**: Developers must resolve conflicts before merging
- **Predictable CI**: Every commit on main has passed all checks
- **Easy rollbacks**: Single commits per PR make reverting simple
- **Better bisection**: Git bisect works perfectly with linear history

### Security & Quality
- **Required reviews**: Prevents unreviewed code from reaching production
- **Status checks**: Ensures all tests pass before merge
- **Conversation resolution**: Forces discussion of important changes
- **Stale review dismissal**: Ensures reviews reflect current code state
- **Early security scanning**: Security scans run early in CI to provide fast feedback and prevent deployment of insecure code

### Automation-Friendly
- **Code owner reviews**: CODEOWNERS file automatically requests your review
- **Up-to-date branches**: Prevents merge conflicts and stale integrations
- **Dependabot compatibility**: Auto-merge workflow works within these constraints
- **Squash merging**: One commit per feature maintains clean history

### Administrative Control
- **Push restrictions**: Only administrators (you) can push directly to main
- **Force push protection**: Prevents history rewriting accidents
- **Deletion protection**: Prevents accidental branch deletion

## Setting Up via GitHub CLI

```bash
# Enable branch protection with all recommended settings
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"checks":[{"context":"Enforce commit standards"},{"context":"Run pytest CI/CD tests (3.11, ubuntu-latest)"},{"context":"Run pytest CI/CD tests (3.12, ubuntu-latest)"}]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions='{"users":[],"teams":[]}' \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_conversation_resolution=true
```

## Dependabot Configuration

### Enable Dependabot Features
Navigate to **Settings** → **Security & analysis** → **Dependabot**:

- ✅ **Dependency graph** - Understand your dependencies
- ✅ **Dependabot alerts** - Security vulnerability notifications
- ✅ **Dependabot security updates** - Automatic security patches
- ✅ **Grouped security updates** - Reduces PR noise
- ✅ **Dependabot version updates** - Keep dependencies current
- ❌ **Automatic dependency submission** - Not needed for Python/Poetry
- ❌ **Dependabot on self-hosted runners** - Only if using self-hosted

### Dependabot Integration Benefits

The current setup allows Dependabot to:
- ✅ Create PRs that trigger required status checks
- ✅ Auto-approve and auto-merge **safe updates** (patch/grouped minor)
- ✅ Require manual review for **major updates**
- ✅ Add helpful comments on breaking changes
- ✅ Group updates to minimize PR noise

This balance provides automation for safe updates while maintaining human oversight for potentially breaking changes.

## Troubleshooting

### Common Issues

1. **"Required status check not found"**
   - Check exact job names in pipeline.yaml
   - Status check names must match exactly

2. **"Dependabot can't merge"**
   - Verify auto-merge workflow has necessary permissions
   - Check that CI passes before auto-merge attempts

3. **"Can't push to main"**
   - This is expected! Use PRs for all changes
   - Emergency pushes require admin override
