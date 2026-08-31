# Threat Model — [System Name]

**Version:** 1.0
**Date:** [YYYY-MM-DD]
**Status:** Draft / Active / Archived
**Author:** [Name]

---

# 1. System Overview

## Purpose

Describe what the AI system does.

[Description]

## Intended Users

* [User type]
* [User type]

## Agent Capabilities

The agent can:

* [Capability]
* [Capability]

The agent cannot:

* [Restriction]
* [Restriction]

---

# 2. Architecture

```text
                    ┌──────────────┐
                    │     User     │
                    └──────┬───────┘
                           │
                           ↓
                    ┌──────────────┐
                    │ Input Layer  │
                    └──────┬───────┘
                           │
                           ↓
                    ┌──────────────┐
                    │    Agent     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
           Memory        Tools        Model
              │            │            │
              └────────────┼────────────┘
                           ↓
                    ┌──────────────┐
                    │    Output    │
                    └──────────────┘
```

Replace this diagram with the actual architecture.

---

# 3. Assets

Identify what needs protection.

| Asset         | Description               | Sensitivity |
| ------------- | ------------------------- | ----------- |
| System Prompt | Agent instructions        | High        |
| Credentials   | API keys/tokens           | Critical    |
| User Data     | User-provided information | Varies      |
| Agent Memory  | Stored context            | High        |
| Tool Access   | External capabilities     | High        |
| Logs          | Agent/security telemetry  | Medium/High |

Additional assets:

* [Asset]
* [Asset]

---

# 4. Trust Boundaries

Identify where data, instructions, or control cross security boundaries.

| Boundary | Source           | Destination | Risk                |
| -------- | ---------------- | ----------- | ------------------- |
| TB-01    | User             | Agent       | Malicious input     |
| TB-02    | External Content | Agent       | Indirect injection  |
| TB-03    | Agent            | Tool        | Unauthorized action |
| TB-04    | Tool             | Agent       | Malicious output    |

Additional boundaries:

[Description]

---

# 5. Entry Points

Potential entry points include:

* User prompts
* Uploaded files
* Websites
* APIs
* MCP servers
* Tool responses
* RAG documents
* Databases
* Agent memory
* Messages from other agents
* External integrations

Project-specific entry points:

* [Entry point]
* [Entry point]

---

# 6. Threat Actors

Potential threat actors include:

### Malicious User

Attempts to manipulate the agent directly.

### External Attacker

Attempts to compromise services, data sources, tools, or infrastructure.

### Malicious Content Author

Creates content designed to manipulate an agent when retrieved or processed.

### Compromised Tool or Service

Returns malicious or misleading instructions/data.

### Compromised Agent

An agent within a multi-agent system behaves maliciously or unexpectedly.

### Insider

An authorized individual abuses legitimate access.

---

# 7. Threat Scenarios

## T-001 — Direct Prompt Injection

**Description:**
An attacker provides instructions designed to override or manipulate intended agent behavior.

**Asset:** [Asset]

**Entry Point:** User Input

**Potential Impact:** [Impact]

**Likelihood:** Low / Medium / High

**Severity:** Low / Medium / High / Critical

**Controls:**

* [Control]
* [Control]

---

## T-002 — Indirect Prompt Injection

**Description:**
The agent retrieves malicious instructions embedded within external content.

**Asset:** Agent behavior / Tool access

**Entry Point:** Retrieved content

**Potential Impact:** [Impact]

**Likelihood:** Low / Medium / High

**Severity:** Low / Medium / High / Critical

**Controls:**

* Content isolation
* Tool authorization
* Least privilege
* Human approval
* [Additional control]

---

## T-003 — Unauthorized Tool Invocation

**Description:**
The agent attempts to execute a tool or action outside the user's or agent's authorized scope.

**Potential Impact:** [Impact]

**Controls:**

* Tool allowlisting
* Authorization enforcement
* Least privilege
* Human approval

---

## T-004 — Sensitive Data Disclosure

**Description:**
Sensitive information is exposed through model output, tool calls, memory, logs, or retrieved context.

**Potential Impact:** [Impact]

**Controls:**

* Data minimization
* DLP controls
* Output filtering
* Access controls
* Secure logging

---

## T-005 — Memory Poisoning

**Description:**
Malicious or inaccurate information is persisted into agent memory and influences future behavior.

**Potential Impact:** [Impact]

**Controls:**

* Memory validation
* Source tracking
* Memory permissions
* Expiration
* Human review

---

## T-006 — Excessive Agency

**Description:**
The system gives the agent more autonomy or permissions than necessary.

**Potential Impact:** [Impact]

**Controls:**

* Least privilege
* Scoped tools
* Human-in-the-loop approval
* Action limits
* Policy enforcement

---

# 8. Risk Register

| ID    | Threat                | Likelihood | Impact | Risk   | Control   |
| ----- | --------------------- | ---------- | ------ | ------ | --------- |
| T-001 | Prompt Injection      | High       | High   | High   | [Control] |
| T-002 | Indirect Injection    | High       | High   | High   | [Control] |
| T-003 | Unauthorized Tool Use | Medium     | High   | High   | [Control] |
| T-004 | Data Disclosure       | Medium     | High   | High   | [Control] |
| T-005 | Memory Poisoning      | Medium     | Medium | Medium | [Control] |
| T-006 | Excessive Agency      | Medium     | High   | High   | [Control] |

Adjust ratings based on the actual system rather than treating these example values as final assessments.

---

# 9. Security Controls

## Preventive

* Authentication
* Authorization
* Least privilege
* Tool restrictions
* Input validation
* Secrets management
* Human approval

## Detective

* Agent tracing
* Security logging
* Tool-call monitoring
* Policy violation detection
* Anomaly detection

## Corrective

* Session termination
* Tool revocation
* Credential rotation
* Memory removal
* Agent isolation
* Incident response

---

# 10. Human Oversight

Actions requiring human approval:

| Action             | Reason   |
| ------------------ | -------- |
| [Sensitive action] | [Reason] |

The system should fail safely when required authorization cannot be obtained.

---

# 11. Logging Requirements

Record:

* Agent ID
* User/session ID where appropriate
* Timestamp
* Requested action
* Tool invoked
* Authorization decision
* Tool parameters where safe
* Result
* Security policy decisions
* Human approval/rejection
* Errors

Do **not** unnecessarily log:

* Passwords
* API secrets
* Authentication tokens
* Sensitive personal information
* Full confidential prompts when avoidable

---

# 12. Residual Risk

After implementing controls, identify risks that remain.

| Risk   | Residual Rating | Accepted? |
| ------ | --------------- | --------- |
| [Risk] | Low/Med/High    | Yes/No    |

---

# 13. Security Testing Plan

* [ ] Direct prompt injection testing
* [ ] Indirect prompt injection testing
* [ ] Tool authorization testing
* [ ] Data leakage testing
* [ ] Memory poisoning testing
* [ ] Privilege-boundary testing
* [ ] Malicious tool-output testing
* [ ] Human-approval bypass testing
* [ ] Logging validation
* [ ] Failure-mode testing

---

# 14. References

Potential references:

* NIST AI Risk Management Framework
* NIST Cybersecurity Framework
* OWASP guidance for LLM and GenAI applications
* MITRE ATLAS
* ISO/IEC 42001
* Vendor security documentation
* Relevant security research

---

# 15. Revision History

| Version | Date         | Change               |
| ------- | ------------ | -------------------- |
| 1.0     | [YYYY-MM-DD] | Initial threat model |
