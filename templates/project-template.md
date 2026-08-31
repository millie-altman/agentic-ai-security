# [Project Name]

> [One-sentence description of the project.]

**Status:** 🔵 Planning / 🟡 Development / 🟢 Complete / 🔴 Archived

---

# Overview

## Problem

What security, engineering, or governance problem does this project address?

[Description]

## Solution

What am I building to address it?

[Description]

## Goals

* [Goal]
* [Goal]
* [Goal]

## Non-Goals

Explicitly identify things this project is not intended to accomplish.

* [Non-goal]
* [Non-goal]

---

# Architecture

## System Overview

```text
User
 ↓
[Component]
 ↓
Agent
 ↓
Security Control
 ↓
Tool / External System
 ↓
Response
```

## Components

| Component   | Purpose   | Trust Level       |
| ----------- | --------- | ----------------- |
| [Component] | [Purpose] | Trusted/Untrusted |
| [Component] | [Purpose] | Trusted/Untrusted |

---

# Agent Design

## Agent Responsibilities

The agent is responsible for:

* [Responsibility]
* [Responsibility]

The agent is **not** authorized to:

* [Restriction]
* [Restriction]

## Models

| Model   | Purpose   |
| ------- | --------- |
| [Model] | [Purpose] |

## Tools

| Tool   | Purpose   | Permission | Human Approval |
| ------ | --------- | ---------- | -------------- |
| [Tool] | [Purpose] | Read       | No             |
| [Tool] | [Purpose] | Write      | Yes            |

## Memory

**Memory enabled:** Yes / No

**Type:** [Session / Persistent / Vector / Other]

**Stored information:**

[Description]

**Security considerations:**

[Description]

---

# Data Flow

Document how information moves through the system.

```text
Input
 ↓
Validation
 ↓
Agent
 ↓
Tool Request
 ↓
Authorization
 ↓
Tool
 ↓
Output Validation
 ↓
User
```

## Data Classification

| Data   | Classification            | Storage    | Retention |
| ------ | ------------------------- | ---------- | --------- |
| [Data] | Public/Internal/Sensitive | [Location] | [Period]  |

---

# Threat Model

See:

`threat-model.md`

## Primary Threats

* Prompt injection
* Indirect prompt injection
* Unauthorized tool use
* Excessive agency
* Sensitive data disclosure
* Agent manipulation
* Memory poisoning
* Malicious external content
* Insecure output handling

Additional project-specific threats:

* [Threat]
* [Threat]

---

# Security Architecture

## Authentication

[Approach]

## Authorization

[Approach]

## Least Privilege

[Approach]

## Input Validation

[Approach]

## Output Validation

[Approach]

## Secrets Management

[Approach]

## Human-in-the-Loop Controls

Actions requiring human approval:

* [Action]
* [Action]

## Logging & Monitoring

Security-relevant events:

* Agent execution
* Tool requests
* Tool authorization decisions
* Authentication events
* Security policy violations
* Human approvals
* Failed actions
* Suspicious input
* Sensitive-data access

---

# Security Testing

## Test Categories

* [ ] Prompt injection
* [ ] Indirect prompt injection
* [ ] Authorization bypass
* [ ] Tool misuse
* [ ] Data leakage
* [ ] System prompt extraction
* [ ] Memory poisoning
* [ ] Malicious tool output
* [ ] Excessive agency
* [ ] Unexpected agent behavior

---

## Security Test Results

| Test ID | Attack   | Expected   | Actual   | Result    |
| ------- | -------- | ---------- | -------- | --------- |
| SEC-001 | [Attack] | [Expected] | [Actual] | PASS/FAIL |

---

# Governance

## AI System Classification

**Purpose:** [Purpose]

**Users:** [Users]

**Autonomy Level:** [Low / Moderate / High]

**Human Oversight:** [Description]

**Sensitive Data:** Yes / No

**External Tools:** Yes / No

---

## Risk Register

| Risk   | Likelihood   | Impact       | Rating   | Control   |
| ------ | ------------ | ------------ | -------- | --------- |
| [Risk] | Low/Med/High | Low/Med/High | [Rating] | [Control] |

---

## Framework Mapping

Where appropriate, controls may be mapped against:

* NIST AI Risk Management Framework
* NIST Cybersecurity Framework
* OWASP guidance for LLM/GenAI systems
* MITRE ATLAS
* ISO/IEC 42001
* Applicable AI regulatory requirements

Framework mappings should be treated as engineering/governance exercises unless a formal compliance assessment has been performed.

---

# Testing

## Functional Testing

[Description]

## Security Testing

[Description]

## Evaluation

How will I determine whether the agent behaves correctly and safely?

[Description]

---

# Results

## What Worked

[Results]

## What Failed

[Results]

## Security Findings

[Findings]

## Improvements Made

[Changes]

---

# Evidence

Supporting evidence may include:

```text
evidence/
├── screenshots/
├── logs/
├── traces/
├── test-results/
└── diagrams/
```

---

# Lessons Learned

## AI Engineering

[Lessons]

## Security Engineering

[Lessons]

## Governance

[Lessons]

## What I Would Do Differently

[Lessons]

---

# Future Improvements

* [ ] [Improvement]
* [ ] [Improvement]
* [ ] [Improvement]

---

# References

* [Official documentation]
* [Security research]
* [Framework]
* [Standard]

---

# Disclaimer

This project is an educational security research environment.

Testing is performed against systems, agents, applications, and data that I own or am explicitly authorized to test. Vulnerable components and attack demonstrations are designed for controlled laboratory use.
