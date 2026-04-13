# Rollback Plan - Restructuring Reversal

**Created**: April 9, 2026  
**Purpose**: Step-by-step instructions to reverse the domain-first architecture restructuring if needed

---

## Overview

This document provides instructions to revert the restructuring that moved core algorithm files from `src/models/` to domain-specific folders (`src/nlp/`, `src/anomaly/`, etc.).

**Time to Rollback**: Approximately 5-10 minutes  
**Risk Level**: Low (uses Git to restore files)

---

## Prerequisites

Before starting rollback:
- Git repository must be clean (no uncommitted changes)
- You have access to git history (commits not purged)
- Current working directory: `D:\Kayan\final-year-project\ai-risk-prediction-framework`

---

## Quick Rollback (Recommended)

If the restructuring was committed to git, use this method:

### Step 1: Check Git Status

```powershell
cd "D:\Kayan\final-year-project\ai-risk-prediction-framework"
git status
```

**Expected Output**: Should show clean working directory or list changed files

### Step 2: Identify the Restructuring Commit

```powershell
git log --oneline -10
```

**Look for**: Commit message mentioning "restructuring" or the date of restructuring

### Step 3: Reset to Previous Commit

If you want to undo the most recent commit:
```powershell
git reset --hard HEAD~1
```

Or reset to a specific commit:
```powershell
git reset --hard <commit-hash>
```

**Example**:
```powershell
git reset --hard abc1234
```

### Step 4: Verify Rollback

```powershell
# Check that old files exist
Test-Path "D:\Kayan\final-year-project\ai-risk-prediction-framework\src\models\nlp_risk_engine.py"
Test-Path "D:\Kayan\final-year-project\ai-risk-prediction-framework\src\models\anomaly_detector.py"

# Check that new files are gone
Test-Path "D:\Kayan\final-year-project\ai-risk-prediction-framework\src\nlp\nlp_risk_engine.py"
Test-Path "D:\Kayan\final-year-project\ai-risk-prediction-framework\src\anomaly\anomaly_detector.py"
```

**Expected Results**:
- Old files: `True`
- New files: `False`

### Step 5: Run Tests to Confirm

```powershell
.\.venv\Scripts\pytest tests/ -v
```

**Expected**: All 44 tests should still pass

---

## Manual Rollback (If Git Not Available)

Use this method if git is not available or history is lost.

### Step 1: Restore Files from Backup

If you have backups of the original files:

```powershell
# Copy nlp_risk_engine.py back to src/models/
Copy-Item -Path "backup/nlp_risk_engine.py" -Destination "src/models/nlp_risk_engine.py"

# Copy anomaly_detector.py back to src/models/
Copy-Item -Path "backup/anomaly_detector.py" -Destination "src/models/anomaly_detector.py"

# Copy __init__.py back to src/models/
Copy-Item -Path "backup/models/__init__.py" -Destination "src/models/__init__.py"
```

### Step 2: Delete Files from New Locations

```powershell
# Remove files from domain folders
Remove-Item -Path "src/nlp/nlp_risk_engine.py" -Force
Remove-Item -Path "src/anomaly/anomaly_detector.py" -Force
```

### Step 3: Revert Import Changes

Revert the following files to their original state:

#### Revert `src/__init__.py`
**Change from**:
```python
# Core models
from .nlp import RiskNLPEngine
from .anomaly import AnomalyEngine
```

**Change to**:
```python
# Core models
from .models import RiskNLPEngine, AnomalyEngine
```

#### Revert `src/nlp/__init__.py`
**Change from**:
```python
"""
NLP Module - Natural Language Processing for Risk Detection
Phase 2-C: NLP-Based Risk Detection

Provides text-based risk analysis and entity extraction.
"""

from .nlp_risk_engine import RiskNLPEngine

__all__ = [
    "RiskNLPEngine",
]
```

**Change to**:
```python
"""
NLP Module - Natural Language Processing for Risk Detection
Phase 2-C: NLP-Based Risk Detection

Provides text-based risk analysis and entity extraction.
"""

from .text_risk_detector import RiskTextDetector

__all__ = [
    "RiskTextDetector",
]
```

#### Revert `src/anomaly/__init__.py`
**Change from**:
```python
"""
Anomaly Detection Module
Phase 2-B: Anomaly Detection using Isolation Forest and statistical methods.

Provides anomaly detection using Isolation Forest algorithm.
"""

from .anomaly_detector import AnomalyEngine

__all__ = [
    "AnomalyEngine",
]
```

**Change to**:
```python
"""
Anomaly Detection Module
Phase 2-B: Anomaly Detection using Isolation Forest and statistical methods.

Placeholder for Phase 2-B implementation. Will include:
- Isolation Forest based anomaly detection
- Statistical outlier detection
- Temporal anomaly detection
"""

__all__ = []
```

### Step 4: Revert Test Files

Update the following 5 test files back to original import paths:

#### `tests/unit/test_nlp_risk_engine.py` (Line 9)
**From**: `from src.nlp import RiskNLPEngine`  
**To**: `from src.models.nlp_risk_engine import RiskNLPEngine`

#### `tests/unit/test_nlp_tokenizer_fix.py` (Line 44)
**From**: `import src.nlp.nlp_risk_engine as nlp_mod`  
**To**: `import src.models.nlp_risk_engine as nlp_mod`

#### `tests/unit/test_anomaly_engine.py` (Line 9)
**From**: `from src.anomaly import AnomalyEngine`  
**To**: `from src.models.anomaly_detector import AnomalyEngine`

#### `tests/integration/test_nlp_integration.py` (Line 5)
**From**: `from src.nlp import RiskNLPEngine`  
**To**: `from src.models.nlp_risk_engine import RiskNLPEngine`

#### `tests/integration/benchmark_nlp_engine.py` (Line 11)
**From**: `from src.nlp import RiskNLPEngine`  
**To**: `from src.models.nlp_risk_engine import RiskNLPEngine`

### Step 5: Recreate models Folder Structure

```powershell
# Recreate src/models folder if deleted
mkdir -Force src/models

# Ensure it has proper structure
dir src/models
```

---

## Verification Steps

### Verify Old Structure Restored

```powershell
# Old files should exist in src/models/
Test-Path "src/models/nlp_risk_engine.py"  # Should be True
Test-Path "src/models/anomaly_detector.py"  # Should be True
Test-Path "src/models/__init__.py"  # Should be True
Test-Path "src/models"  # Should be True

# New files should NOT exist
Test-Path "src/nlp/nlp_risk_engine.py"  # Should be False
Test-Path "src/anomaly/anomaly_detector.py"  # Should be False
```

### Verify Imports Work

```powershell
python -c "from src.models import RiskNLPEngine, AnomalyEngine; print('✓ Old imports work!')"
```

### Run Full Test Suite

```powershell
.\.venv\Scripts\pytest tests/ -v
```

**Expected Result**: All 44 tests pass

---

## Troubleshooting Rollback Issues

### Issue 1: "File already exists" errors

**Cause**: File exists in both old and new location

**Solution**:
```powershell
# Delete files from new location first
Remove-Item -Path "src/nlp/nlp_risk_engine.py" -Force
Remove-Item -Path "src/anomaly/anomaly_detector.py" -Force

# Then restore to old location
Copy-Item -Path "backup/nlp_risk_engine.py" -Destination "src/models/nlp_risk_engine.py"
```

### Issue 2: "Git status shows uncommitted changes"

**Cause**: Changes made after restructuring

**Solution**:
```powershell
# Stash changes
git stash

# Then reset
git reset --hard HEAD~1

# Retrieve stashed changes (optional)
git stash pop
```

### Issue 3: Tests still fail after rollback

**Cause**: Incomplete rollback of imports

**Solution**:
```powershell
# Verify all 5 test files were updated
grep -r "src.models" tests/

# Should show imports from src.models
# If not, manually update them

# Run individual test to debug
.\.venv\Scripts\pytest tests/unit/test_nlp_risk_engine.py -v
```

---

## Rollback Checklist

Before considering rollback complete, verify:

- ✅ `src/models/` folder exists
- ✅ `nlp_risk_engine.py` in `src/models/`
- ✅ `anomaly_detector.py` in `src/models/`
- ✅ `__init__.py` in `src/models/`
- ✅ `src/nlp/nlp_risk_engine.py` does NOT exist
- ✅ `src/anomaly/anomaly_detector.py` does NOT exist
- ✅ `src/__init__.py` imports from `.models`
- ✅ `src/nlp/__init__.py` imports from `.text_risk_detector`
- ✅ `src/anomaly/__init__.py` is empty
- ✅ All 5 test files import from `src.models.*`
- ✅ All 44 tests pass
- ✅ Import test works: `from src.models import RiskNLPEngine, AnomalyEngine`

---

## Time Estimates

| Method | Time | Complexity |
|--------|------|------------|
| Git Rollback | 2-3 minutes | Low |
| Manual Rollback | 5-10 minutes | Medium |
| Verification | 5-7 minutes | Low |
| **Total** | **10-20 minutes** | **Low-Medium** |

---

## Support

If rollback fails or you encounter issues:

1. Check all 5 test files are properly reverted
2. Verify file paths use `src/models/` not `src/nlp/` or `src/anomaly/`
3. Run individual tests to isolate issues
4. Review git history: `git log --oneline` to find restructuring commit

---

## When to Use This Plan

Use this rollback plan if:

- ✗ Tests are failing after restructuring
- ✗ New imports are not working
- ✗ You need to revert to models-centric architecture
- ✗ External dependencies break with new structure
- ✗ You want to cancel the restructuring

---

**Rollback Plan Complete** ✓

For more information, see `RESTRUCTURING_COMPLETED.md`
