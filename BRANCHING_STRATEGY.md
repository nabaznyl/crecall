# Branching Strategy

This document explains the crecall repository's branch workflow and version management.

## Branch Structure

### `main` (Frozen Archive)
- **Purpose**: Pristine baseline, never modified
- **State**: Frozen at v0.1.0-dev-7
- **Use**: Emergency fallback, historical reference
- **Updates**: Never (except catastrophic recovery scenarios)

### `stablemain` (Rolling Baseline)
- **Purpose**: Current stable baseline, tracks proven stable releases
- **State**: Starts as exact copy of `main`, updated with each verified stable release
- **Use**: Source of truth for stable production code
- **Updates**: Merges from `stable` branch after verification

### `stable` (Release Candidate)
- **Purpose**: Production release testing
- **State**: Currently v0.1.0-stable-1
- **Use**: Test releases before deploying to production
- **Updates**: Manual updates when preparing new releases

**Workflow:**
1. Create `stable` branch from `stablemain` for new release
2. Test thoroughly in `stable`
3. If issues found → revert `stable` to `stablemain` state
4. If release works → merge `stable` into `stablemain`, create fresh `stable` for next cycle

### `dev` (Active Development)
- **Purpose**: Main development branch for tested features
- **State**: v0.1.0-dev-7
- **Use**: Day-to-day development, feature integration
- **Updates**: Frequent commits, merge-ready features

### `nightly` (Bleeding Edge)
- **Purpose**: Experimental features, instant updates
- **State**: v0.1.0-nightly-8
- **Use**: Testing latest changes, contributor preview
- **Updates**: Multiple times daily during active development

## Version Flow

```
main (frozen v0.1.0-dev-7)
  ↓ (one-time copy)
stablemain (rolling baseline) ←──── stable (release testing)
  ↓                                    ↑
dev (active features) ────→ nightly (experiments)
```

## Release Workflow

### Stable Release Process

1. **Prepare Release**
   ```bash
   git checkout stablemain
   git pull origin stablemain
   git checkout -b stable
   # Update VERSION: CHANNEL=stable, increment BUILD_NUMBER
   # Merge features from dev if needed
   ```

2. **Test Release**
   - Run full test suite
   - Perform integration testing
   - Security audit
   - Performance validation

3. **On Success**
   ```bash
   git checkout stablemain
   git merge stable --no-ff -m "chore: merge stable v0.1.x-stable-N"
   git push origin stablemain
   git tag -a v0.1.x-stable-N -m "Stable release N"
   git push origin v0.1.x-stable-N
   # Create fresh stable branch for next cycle
   git branch -D stable
   git checkout -b stable
   ```

4. **On Failure**
   ```bash
   git checkout stable
   git reset --hard stablemain  # Revert to last known good
   # Fix issues, repeat testing
   ```

### Development Workflow

1. **Feature Development**
   ```bash
   git checkout dev
   git checkout -b feature/my-feature
   # Develop and test
   git checkout dev
   git merge feature/my-feature
   git push origin dev
   ```

2. **Nightly Updates**
   ```bash
   git checkout nightly
   git merge dev
   # Update BUILD_NUMBER in VERSION
   git push origin nightly
   ```

## Version Numbering

Format: `MAJOR.MINOR.PATCH-CHANNEL-BUILD`

- **MAJOR**: Breaking changes (0 during pre-release)
- **MINOR**: New features, significant updates
- **PATCH**: Bug fixes, minor improvements
- **CHANNEL**: stable | dev | nightly
- **BUILD**: Incremental build number per channel

### Current Versions
- `main`: v0.1.0-dev-7 (frozen)
- `stablemain`: v0.1.0-dev-7 (baseline)
- `stable`: v0.1.0-stable-1
- `dev`: v0.1.0-dev-7
- `nightly`: v0.1.0-nightly-8

## Emergency Procedures

### Revert to Original Baseline
If `stablemain` becomes corrupted:
```bash
git checkout stablemain
git reset --hard main  # Revert to pristine frozen state
git push origin stablemain --force
```

### Catastrophic Recovery
If all active branches fail:
```bash
# main branch is frozen and pristine - always safe to restart from
git checkout main
git checkout -b recovery
# Rebuild from known-good state
```

## Best Practices

1. **Never commit directly to `main`** - It's frozen for archival purposes
2. **Always test in `stable` before merging to `stablemain`**
3. **Keep `stablemain` clean** - Only merge verified, working releases
4. **Use `nightly` for experiments** - Don't risk `dev` stability
5. **Tag every `stablemain` merge** - Maintain clear version history
6. **Document failures** - Note why stable releases were reverted

## Branch Protection Rules (Recommended)

Configure on GitHub:
- `main`: No direct pushes, no force pushes, no deletions
- `stablemain`: Require PR reviews, require CI passing
- `stable`: Require CI passing before merge
- `dev`: Require CI passing
- `nightly`: Allow direct pushes for rapid iteration
