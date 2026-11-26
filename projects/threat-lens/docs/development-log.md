# ThreatLens — Development Log (Condensed)

**Project:** ThreatLens, a security-first threat intelligence pipeline, part of the Agentic AI Security Lab
**Date:** November 25, 2026
**Branch:** `feature/threatlens-mvp`
**Stack:** Python 3.12.10, HTTPX, Pydantic, PyYAML, pytest, coverage.py, Bandit, pip-audit, pip-tools (hash-locked dependencies)

---

## 1. Summary

ThreatLens is built deterministic-first: a secure, fully tested intelligence pipeline comes **before** any AI or agentic functionality. External intelligence is treated as untrusted data at every stage, and AI features stay disabled until the foundation is verified.

**Where it stands (end of Phase 1D.1):**

| Metric | Result |
|---|---:|
| Automated tests | 231 / 231 passing |
| Statement / branch / combined coverage | 99% / 99% / 99.30% combined (98% minimum threshold proposed) |
| Bandit findings (1,260 lines scanned) | 0 |
| pip-audit known vulnerabilities (all 7 assessment targets) | 0 |
| Hash-pinned lock file entries | 997 |
| Clean-environment rebuilds verified | Runtime, development, remediated runtime |
| Live CISA KEV records processed | 1,805 |
| End-to-end pipeline time | 2.20–2.27 s (clean environments) |
| Pipeline exit code | 0 (SUCCESS) |

---

## 2. Pipeline Architecture

```
CISA KEV (HTTPS) → Collector → Schema validation → Normalizer → Deduplicator → JSON storage (+SHA-256) → Reload & verify
                   └──────────── orchestrated by main.py, with logging, stats, and exit codes ────────────┘
```

**Core design principles**

- Centralized, allowlisted source configuration (HTTPS only, exact hostnames, fail-closed)
- Structured data contracts (Pydantic) with provenance, UTC timestamps, and human-review defaults
- Deterministic UUID5 record IDs, enabling idempotent processing and deduplication
- Bounded resources: response size, retries, delays, file sizes
- Evidence preservation: raw and processed snapshots stored separately, integrity-checked

---

## 3. Phase 1B: Building the Pipeline

| Phase | What was built | Tests added | Cumulative tests |
|---|---|---:|---:|
| **1A** Project init | Modular repo, Python 3.12 venv, `.gitignore` for secrets/data/IDE, feature branch | n/a | n/a |
| **1B.1** Planning | Source allowlists, request limits, untrusted-data posture, AI disabled | n/a | n/a |
| **1B.2** Data contracts | Pydantic schemas for CISA KEV and a standard intelligence record; CVE format, date, and length validation; AI-analysis and human-review status fields | 7 | n/a |
| **1B.3** Secure config | Safe YAML loader; HTTPS-only, exact-hostname allowlist; rejects embedded credentials, odd ports, fragments, malformed URLs (SSRF-oriented) | parameterized | n/a |
| **1B.4** CISA collector | HTTPX collector, TLS verification, redirects disabled, bounded retries with backoff, streaming size cap, content-type and JSON validation, catalog count checks | 12 | n/a |
| **1B.5** Normalization | Source-to-standard field mapping, UUID5 IDs, rule-based tagging, conservative severity defaults | 10 | 48 |
| **1B.6** Deduplication | Dictionary-based dedup, latest-timestamp selection, deterministic tie handling, source attribution preserved | 10 | 58 |
| **1B.7** Persistence | Timestamped JSON snapshots, atomic writes, SHA-256 checksums, path restrictions, schema revalidation on load | 13 | 71 |
| **1B.8** Orchestration | `main.py` entry point, UTC logging, pipeline stats, end-to-end integrity checks, controlled exit codes | 13 | 84 |

**Notable live validations**

- **Dedup (1B.6):** 1,805 live records were deliberately duplicated to 3,610. The deduplicator retained 1,805 unique records and removed all 1,805 injected duplicates, with 100% of the originals retained.
- **Full pipeline (1B.8):** 1,805 collected → 1,805 normalized → 1,805 unique → 1,805 reloaded. Integrity check passed in 2.09 s.

**Troubleshooting note (1B.5):** Normalization tests failed after the schemas were expanded (source version, publication timestamp, supporting notes). Replacing the schema module with a consolidated implementation fixed it, and all 48 tests passed. This reinforced that schema changes ripple downstream and that regression tests catch integration breaks early.

---

## 4. Phase 1C: Security Hardening

**Method:** pip-audit (dependencies), Bandit (static analysis), statement and branch coverage, targeted adversarial regression tests, repository and secret hygiene checks, and finally threat modeling.

### 1C.1: Baseline audit

- pip-audit v2.10.1: **0** known vulnerabilities (installed and declared)
- Bandit v1.9.4: **0** findings across 956 lines
- Tests: 84/84 · Statement 95% · Branch 84% · Combined 93%
- Secret and repository hygiene verified (`.env`, venv, coverage artifacts, snapshots, and audit reports are all git-ignored; only `.env.example` was found)

![Coverage baseline: 93% combined](images/coverage-1c1-baseline-93.png)

*Weakest areas at baseline: `config_loader.py` (85% combined), `json_storage.py` (89%), `main.py` (95%), `cisa_collector.py` (94%).*

### 1C.2: Configuration security regression tests

Added 30 adversarial tests covering malformed or missing config, **unsafe YAML object construction**, bad registries, wrong URL and allowlist types, explicit source enablement, case-insensitive hostnames, and standard HTTPS port handling.

![Coverage after configuration hardening: 96% combined](images/coverage-1c2-config-96.png)

### 1C.3: Storage hardening

- 50 MiB snapshot cap, 128-byte checksum-file cap, bounded reads
- SHA-256 format and encoding validation
- Strict JSON parsing: **duplicate key rejection**, **nonstandard constant rejection** (`NaN`/`Infinity`), top-level structure validation
- Improved atomic write handling, cleanup of incomplete snapshots, filename collision protection
- Live run re-verified: 1,805 records, integrity True, 2.27 s

![Coverage after storage hardening: 97% combined](images/coverage-1c3-storage-97.png)

### 1C.4: Collector hardening

- Revalidation of limits and source URL *before* every request
- Strict `Content-Length` validation; compressed-response rejection; declared-vs-received size consistency; empty-response rejection
- Duplicate JSON keys, nonstandard constants, and **duplicate CVE IDs** rejected
- Retry delay capped at 60 s
- Live run re-verified: 200 OK, 1 attempt, 1,805 records, 2.51 s

![Coverage after collector hardening: 98% combined](images/coverage-1c4-collector-98.png)

### 1C.5: Application integrity testing

Goal: **detected tampering, inconsistency, or incomplete processing must never yield a successful run.**

- Normalized-record verification: deterministic IDs, provenance, collection timestamps, source field comparisons, duplicate CVE detection
- Independent deep-copy baseline for dedup identity, content, and latest-record checks
- Tested same-count modifications, in-place mutations, storage failure propagation, sanitized exception logging, and entry-point behavior
- Third-party HTTP logging restricted
- Live run re-verified: 1,805 records, integrity True, 2.45 s, exit 0

![Coverage after application integrity testing: 99% combined](images/coverage-1c5-integrity-99.png)

### Hardening progression

| Metric | Baseline (1C.1) | 1C.2 | 1C.3 | 1C.4 | 1C.5 |
|---|---:|---:|---:|---:|---:|
| Automated tests | 84 | 114 | 139 | 184 | **231** |
| Statement coverage | 95% | 96% | 98% | 99% | **99%** |
| Branch coverage | 84% | 91% | 94% | 96% | **99%** |
| Combined coverage | 93% | 96% | 97% | 98% | **99%** |
| Executable statements | 453 | 453 | 499 | 533 | 574 |
| Uncovered statements | 24 | 16 | 11 | 7 | **4** |
| Partial branches | 13 | 7 | 6 | 4 | **1** |

*Remaining gap: 4 statements and 1 partial branch in `json_storage.py`. Engineering decision: stop chasing coverage for its own sake and prioritize threat modeling, dependency reproducibility, CI, and release prep.*

---

## 5. Phase 1C.6: Threat Model and Residual Risk Documentation

**Deliverables:** architecture (current and future agentic), data flow diagram, trust boundaries, asset inventory, STRIDE assessment, residual risk register, control traceability matrix, future AI threat assessment, and risk-acceptance requirements.

| Metric | Result |
|---|---:|
| STRIDE categories assessed | 6 |
| Protected assets | 14 |
| Trust boundaries (current / future) | 4 / 3 |
| Current threat scenarios | 17 |
| Documented security controls | 15 |
| Future AI threat scenarios | 14 |
| Residual risks: Critical / High / Medium / Low | 0 / 1 / 15 / 1 |

**Decisions:** STRIDE as the methodology; qualitative likelihood-impact scoring; implemented controls kept distinct from future requirements; deterministic processing preserved before AI; all external intelligence untrusted; **verified-run acceptance required before any automated downstream consumption**.

---

## 6. Phase 1D.1: Dependency Pinning and Reproducible Environments

**Goal:** Make the environment reproducible, harden the software supply chain, and confirm the 231-test and security baseline still holds.

**What was done**

- Documented Python 3.12.10 as the tested runtime and captured the original dependency inventory
- Split **runtime** (6 direct, 16 resolved packages) from **development** (5 additional direct, 49 resolved) dependencies
- Generated lock files with **SHA-256 artifact hashes**: 243 runtime, 752 development, 2 bootstrap (997 total)
- Verified **binary-only, hash-enforced installs** in independent runtime and development environments (0 dependency conflicts)
- Reproduced the full regression baseline and left the original working environment untouched (0 changes detected)

| Regression check | Result |
|---|---:|
| Tests passed | 231 (65 functional, 166 security-focused) |
| Combined coverage | 99.30% (proposed 98% minimum) |
| Bandit findings (1,260 lines) | 0 |
| Regression time | 20.25 s |

### Finding TL-SCA-001: Vulnerable bootstrap installer

| | |
|---|---|
| **Affected component** | pip 25.0.1 |
| **How it was found** | pip-audit on the *installed* environment (the lock files audited clean) |
| **Initial result** | 12 findings, 6 unique advisories, 1 package, exit code 1 |
| **Root cause** | Virtual environment creation bundled an outdated pip, outside the application dependency lock |
| **Remediation** | Added a dedicated bootstrap lock (`requirements-bootstrap.txt` → `requirements-bootstrap-lock.txt`), pinned pip 26.3 with hash verification, and updated the provisioning sequence |
| **Verification** | Re-audit plus a fresh runtime environment: 0 vulnerabilities, exit code 0 |
| **Status** | Remediated and verified in tested environments |

**Final audits:** all 7 targets (bootstrap, runtime, and development locks; remediated runtime, development, and newly provisioned environments; resolution tooling) reported 0 known vulnerabilities.

**Live pipeline across clean environments**

| Metric | Runtime | Development | Remediated runtime |
|---|---:|---:|---:|
| Records collected / normalized / unique / reloaded | 1,805 | 1,805 | 1,805 |
| Duplicates removed | 0 | 0 | 0 |
| Integrity verified | True | True | True |
| Execution time | 2.20 s | 2.26 s | 2.27 s |
| Exit code | 0 | 0 | 0 |

**Decisions:** keep previously verified dependency versions; separate packaging infrastructure from application dependencies; require hash verification and binary-only installs; isolate resolution tooling; audit both declarations *and* installed environments.

**Limitations:** hashes don't prove publisher authenticity; audits can't catch malicious or undisclosed vulnerabilities; cross-platform reproducibility is unverified (Windows baseline only); the Python interpreter itself isn't assessed; bootstrap remediation still runs the bundled installer once; resolution tooling has no hash-locked file yet; CI enforcement is pending.

**Cost:** $0.00 in additional API or infrastructure spend.

---

## 7. Key Residual Risks

- **No DNS-level SSRF protection or network egress restriction** (URL validation alone doesn't eliminate SSRF)
- **Checksums prove integrity, not authenticity** (SHA-256 doesn't authenticate the source)
- **Persistence is not fully transactional**, so failed runs may leave unverified snapshots; filesystem race conditions are possible; no retention policy
- **Size limits don't bound parsing memory or time**; no strict end-to-end timeout; no `Retry-After` handling
- **Verification shares the app's trust boundary** and adds memory overhead via deep copies
- **Structurally valid ≠ trustworthy:** intelligence can still be misleading or adversarial (including prompt injection once AI is introduced)
- **Tie handling:** identical collection timestamps retain the first record encountered
- **Compressed-response rejection** may limit future provider compatibility
- **Supply chain:** package hashes don't prove publisher authenticity, the bootstrap installer is still executed once, resolution tooling isn't hash-locked, the Python interpreter is unassessed, and cross-platform reproducibility is unverified
- **High coverage and clean scans do not prove the absence of vulnerabilities**
- **AI-specific controls are out of scope** for the foundational MVP

---

## 8. Lessons Learned (writeup-ready)

1. **Build the deterministic foundation first.** AI analysis is far easier to secure when the data underneath it is validated, provenance-tracked, and integrity-checked.
2. **Validation is not verification.** Schema checks improve integrity but don't establish factual accuracy or stop prompt injection.
3. **Fail closed, and verify before succeeding.** The pipeline can only report SUCCESS after end-to-end consistency checks pass.
4. **Adversarial tests find what happy-path tests miss:** duplicate JSON keys, `NaN` constants, compressed responses, oversized or mismatched bodies, same-count tampering.
5. **Coverage is a signal, not proof.** The numbers helped guide the work, but threat modeling is what exposed the residual risks.
6. **Schema changes need regression tests.** The 1B.5 failure showed how data-contract changes break downstream components.
7. **Document limitations honestly.** Every phase lists residual risks, which makes the project more credible, not less.
8. **Audit what's installed, not just what's declared.** Clean lock files hid a vulnerable pip that virtual environment creation had bundled in (TL-SCA-001). Scanning the real environment caught it.
9. **Reproducibility is a security control.** Hash-pinned, binary-only installs mean a rebuilt environment matches the tested one, and the 231-test baseline reproduced with no changes.

---

## 9. Next Steps

- [ ] Review and commit the Phase 1C.6 threat model documentation (if not already pushed)
- [x] **Phase 1D.1:** Dependency pinning and reproducible environments
- [ ] **Phase 1D.2:** GitHub Actions CI with automated security gates (tests, Bandit, pip-audit, 98% coverage threshold)
- [ ] Hash-locked lock file for dependency resolution tooling
- [ ] Verify cross-platform reproducibility (beyond Windows)
- [ ] Foundational MVP release preparation
- [ ] Use the residual-risk roadmap as the entry point for future agentic and AI security controls