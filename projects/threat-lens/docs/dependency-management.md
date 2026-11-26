# ThreatLens — Dependency Management and Software Supply Chain Security

## 1. Purpose

ThreatLens implements controlled dependency management to improve environment reproducibility, package integrity, and software supply chain security.

This strategy supports the mitigation of E-03 — Software Supply Chain Compromise, identified in the ThreatLens STRIDE threat model.

## 2. Verified Environment

**Assessment date:** November 25, 2026 (Alaska local time).

| Attribute | Value |
|---|---|
| Python | 3.12.10 |
| Operating system | Windows 11 |
| Architecture | AMD64 |
| Package installer | pip 26.3 |
| Dependency resolver | pip-tools 7.7.0 |
| Testing framework | pytest 9.2.0 |
| Coverage tooling | coverage 7.17.5 |
| Static security analysis | Bandit 1.9.4 |
| Dependency vulnerability analysis | pip-audit 2.10.1 |

Cross-platform reproducibility requires separate verification.

## 3. Dependency Architecture

ThreatLens separates packaging infrastructure, application dependencies, and development tooling.

| File | Responsibility |
|---|---|
| .python-version | Documents the tested Python version |
| requirements-bootstrap.txt | Pinned packaging infrastructure |
| requirements-bootstrap-lock.txt | Resolved bootstrap package and artifact hashes |
| requirements.txt | Pinned direct runtime dependencies |
| requirements-lock.txt | Resolved runtime dependencies and artifact hashes |
| requirements-dev.txt | Pinned direct development dependencies |
| requirements-dev-lock.txt | Resolved development dependencies and artifact hashes |
| constraints-baseline.txt | Previously verified dependency versions |

### Dependency Inventory

| Dependency category | Direct packages | Resolved packages | Hash entries |
|---|---:|---:|---:|
| Bootstrap | 1 | 1 | 2 |
| Runtime | 6 | 16 | 243 |
| Development | 5 additional | 49 | 752 |

Total artifact hash entries across all lock files: 997.

Package and hash counts overlap between lock files and do not represent unique artifacts across the entire project.

## 4. Dependency Resolution Environment

Dependency lock files are generated in an isolated tooling environment to avoid modifying the working application environment.

### Verified Tooling Inventory

| Package | Version |
|---|---|
| pip | 26.3 |
| pip-tools | 7.7.0 |
| build | 1.6.1 |
| click | 8.5.1 |
| colorama | 0.4.6 |
| packaging | 26.4 |
| pyproject-hooks | 1.3.3 |
| setuptools | 84.2.1 |
| wheel | 0.48.0 |

The tooling environment passed dependency consistency and vulnerability assessments.

### Bootstrap Lock Generation

```powershell
python -m piptools compile `
    --generate-hashes `
    --allow-unsafe `
    --resolver=backtracking `
    --output-file requirements-bootstrap-lock.txt `
    requirements-bootstrap.txt
```

### Runtime Lock Generation

```powershell
python -m piptools compile `
    --constraint constraints-baseline.txt `
    --generate-hashes `
    --allow-unsafe `
    --resolver=backtracking `
    --output-file requirements-lock.txt `
    requirements.txt
```

### Development Lock Generation

```powershell
python -m piptools compile `
    --constraint constraints-baseline.txt `
    --constraint requirements-lock.txt `
    --generate-hashes `
    --allow-unsafe `
    --resolver=backtracking `
    --output-file requirements-dev-lock.txt `
    requirements-dev.txt
```

Execute these commands using the designated dependency resolution environment.

The --allow-unsafe option permits required packaging infrastructure to be included in the dependency lock. It does not disable package hash verification.

The recorded tooling inventory provides a reproducibility reference but is not yet maintained as a separate hash-verified tooling lock.

## 5. Controlled Environment Provisioning

All new ThreatLens environments must install the bootstrap dependency lock before installing application or development dependencies.

### Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install Packaging Infrastructure

```powershell
python -m pip install `
    --require-hashes `
    --no-cache-dir `
    --only-binary=:all: `
    -r requirements-bootstrap-lock.txt
```

Verify the installer version:

```powershell
python -m pip --version
```

Expected version: pip 26.3.

### Runtime Installation

```powershell
python -m pip install `
    --require-hashes `
    --no-cache-dir `
    --only-binary=:all: `
    -r requirements-lock.txt
```

### Development Installation

For development environments, install the development lock instead of the runtime lock.

```powershell
python -m pip install `
    --require-hashes `
    --no-cache-dir `
    --only-binary=:all: `
    -r requirements-dev-lock.txt
```

### Dependency Consistency Verification

```powershell
python -m pip check
```

### Application Execution

```powershell
python main.py
```

## 6. Software Supply Chain Security Controls

Implemented controls include:

- Exact direct dependency version pinning.
- Resolved transitive dependency locking.
- SHA-256 package artifact hash verification.
- Binary-only package installation.
- Runtime and development dependency separation.
- Independent packaging infrastructure management.
- Isolated dependency resolution tooling.
- Clean environment installation verification.
- Dependency consistency validation.
- Dependency vulnerability assessments.
- Functional and security regression testing.
- Static application security testing.

## 7. Security Finding TL-SCA-001

### Vulnerable Bootstrap Package Installer

**Status:** Remediated and verified in tested environments.

**Related threat model risk:** E-03 — Software Supply Chain Compromise.

**Affected component:** pip 25.0.1.

**Remediated version:** pip 26.3.

### Discovery

Application dependency lock audits initially returned no known vulnerabilities.

However, an installed runtime environment audit identified 12 reported vulnerability findings representing six unique advisory identifiers affecting the bootstrap package installer.

### Identified Advisories

| Advisory ID | Reported fixed version |
|---|---|
| PYSEC-2026-1795 | 25.3 |
| PYSEC-2026-1796 | 26.0 |
| PYSEC-2026-2875 | 26.1 |
| PYSEC-2026-2876 | 26.1 |
| PYSEC-2026-196 | 26.1.2 |
| PYSEC-2026-3721 | 26.2 |

The advisory identifiers and fixed versions were obtained from pip-audit output.

### Root Cause

Python 3.12.10 virtual environment creation introduced pip 25.0.1 independently of the ThreatLens application dependency lock.

The runtime dependency lock did not manage the package installer itself.

### Corrective Action

- Created a dedicated bootstrap requirements file.
- Generated a hash-verified bootstrap dependency lock.
- Upgraded the affected installer to pip 26.3.
- Repeated installed environment vulnerability assessments.
- Created an additional clean verification environment.
- Installed the bootstrap lock before application dependencies.
- Verified dependency consistency and application functionality.

### Verification Results

| Metric | Before | After |
|---|---:|---:|
| Pip version | 25.0.1 | 26.3 |
| Reported vulnerability findings | 12 | 0 |
| Unique advisory IDs reported | 6 | 0 |
| Audit exit code | 1 | 0 |

### Preventive Action

Integrate bootstrap dependency installation, dependency lock verification, and installed environment auditing into the GitHub Actions continuous integration workflow.

## 8. Vulnerability Assessment Procedures

Execute dependency audits using the verified development environment.

### Bootstrap Lock Audit

```powershell
python -m pip_audit -r requirements-bootstrap-lock.txt --require-hashes --strict
```

### Runtime Lock Audit

```powershell
python -m pip_audit -r requirements-lock.txt --require-hashes --strict
```

### Development Lock Audit

```powershell
python -m pip_audit -r requirements-dev-lock.txt --require-hashes --strict
```

### Installed Environment Audit

```powershell
python -m pip_audit --local --strict
```

When auditing a separate environment, explicitly identify its Python interpreter using PIPAPI_PYTHON_LOCATION and ensure that an unrelated virtual environment is not activated.

### Final Assessment Results

| Assessment target | Known vulnerabilities | Exit code |
|---|---:|---:|
| Bootstrap lock | 0 | 0 |
| Runtime lock | 0 | 0 |
| Development lock | 0 | 0 |
| Remediated runtime environment | 0 | 0 |
| Development environment | 0 | 0 |
| Newly provisioned runtime environment | 0 | 0 |
| Dependency resolution tooling | 0 | 0 |

These results represent the vulnerability information available at the time of assessment.

## 9. Functional and Security Verification

### Regression Testing

```powershell
python -m pytest tests/ -v `
    --cov=src `
    --cov=main `
    --cov-branch `
    --cov-report=term-missing `
    --cov-fail-under=98
```

### Static Application Security Testing

```powershell
python -m bandit -r src main.py
```

### Verified Regression Baseline

| Metric | Result |
|---|---:|
| Automated tests passed | 231 |
| Failed tests | 0 |
| Functional tests | 65 |
| Security-focused tests | 166 |
| Combined coverage | 99.30% |
| Minimum coverage threshold | 98% |
| Regression execution time | 20.25 seconds |
| Bandit findings | 0 |
| Lines scanned | 1,260 |
| Suppressed lines | 0 |
| Skipped files | 0 |

### Live Intelligence Pipeline Verification

| Metric | Runtime | Development | Remediated runtime |
|---|---:|---:|---:|
| Records collected | 1,805 | 1,805 | 1,805 |
| Records normalized | 1,805 | 1,805 | 1,805 |
| Unique records | 1,805 | 1,805 | 1,805 |
| Records reloaded | 1,805 | 1,805 | 1,805 |
| Duplicates removed | 0 | 0 | 0 |
| Integrity verified | True | True | True |
| Execution time (seconds) | 2.20 | 2.26 | 2.27 |
| Exit code | 0 | 0 | 0 |

The original working environment remained unchanged throughout verification.

## 10. Dependency Update Policy

Dependency updates must be intentional, reviewed, and validated.

1. Review the reason for the proposed update.
2. Evaluate applicable security advisories.
3. Update direct dependency pins and relevant constraints.
4. Regenerate affected dependency lock files.
5. Review dependency and artifact hash changes.
6. Create clean verification environments.
7. Install bootstrap and application dependencies.
8. Verify dependency consistency.
9. Audit dependency locks and installed environments.
10. Execute functional and security regression tests.
11. Conduct static application security testing.
12. Document results and residual risks.
13. Submit changes through the established Git review process.

## 11. Security Limitations and Residual Risks

- Package hashes verify artifact integrity but do not independently establish publisher trustworthiness.
- Vulnerability assessments cannot detect every malicious package or undisclosed vulnerability.
- Version pinning requires ongoing security maintenance.
- Binary-only installation reduces exposure to source distribution build execution but does not guarantee package safety.
- Virtual environments provide dependency isolation, not security sandboxing.
- The initial bootstrap upgrade still executes the older bundled installer.
- Python interpreter security requires independent assessment.
- Windows-generated dependency locks require cross-platform verification.
- Dependency resolution tooling is inventoried and audited but does not yet have a dedicated reproducible lock.
- Continuous integration enforcement and automated dependency monitoring remain pending.

The E-03 residual risk classification remains High pending additional supply chain security assessment and CI implementation.

## 12. Conclusion

ThreatLens has established a reproducible, hash-verified Windows dependency management baseline.

Independent environment auditing identified a vulnerable bootstrap installer that was not captured by application dependency lock assessments. The issue was remediated through controlled packaging infrastructure management and verified through clean environment provisioning, vulnerability reassessment, and successful application execution.

The next implementation milestone extends these controls through automated continuous integration and security enforcement.