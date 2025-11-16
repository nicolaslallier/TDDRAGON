# Release v0.3.1 - Instructions

## ✅ Completed Steps

1. ✅ Fixed all regression test failures
2. ✅ Achieved 100% test coverage for regression test suite
3. ✅ Created release documentation (`docs/releases/v0.3.1.md`)
4. ✅ Created git tag `v0.3.1`
5. ✅ Created PR description (`PR_DESCRIPTION.md`)

## 📋 Next Steps

### 1. Push Branch and Tag to Remote

```bash
# Push the branch
git push origin feature/implement-v0.3.0

# Push the tag
git push origin v0.3.1
```

### 2. Create Pull Request on GitHub

1. Go to: https://github.com/nicolaslallier/TDDRAGON
2. Click "New Pull Request"
3. Select:
   - **Base branch**: `main`
   - **Compare branch**: `feature/implement-v0.3.0`
4. Use the content from `PR_DESCRIPTION.md` as the PR description
5. Add reviewers if needed
6. Submit the PR

### 3. After PR is Merged

Once the PR is merged to `main`:

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Verify tag is present
git tag -l "v0.3.1"

# Create GitHub Release (optional)
# Go to: https://github.com/nicolaslallier/TDDRAGON/releases/new
# Select tag: v0.3.1
# Title: Release v0.3.1
# Description: Copy content from docs/releases/v0.3.1.md
```

## 📊 Summary

- **Version**: v0.3.1
- **Type**: Patch Release
- **Branch**: `feature/implement-v0.3.0`
- **Tag**: `v0.3.1` (created locally)
- **Release Notes**: `docs/releases/v0.3.1.md`
- **PR Description**: `PR_DESCRIPTION.md`

## 🧪 Verification

All tests passing:
```bash
make test-regression
# Expected: 137 passed, 100% coverage
```

