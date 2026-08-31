# Agentic AI Security Learning & Project Roadmap

This roadmap tracks my progression from traditional cybersecurity into Agentic AI Security Engineering, AI Red Teaming, and AI Governance.

The goal is to build practical, portfolio-ready experience by combining structured coursework, hands-on labs, independent research, security testing, and original projects.

This roadmap is intentionally flexible and will evolve as my skills, interests, and career goals develop.

---

# Long-Term Direction

My primary areas of interest are:

* Agentic AI Security Engineering
* AI Red Teaming
* Secure Agent Architecture
* Model Context Protocol (MCP) Security
* AI Governance and Compliance
* AI Risk Management
* AI Security Monitoring
* Human-in-the-Loop Security Controls
* AI Security Operations

The long-term objective is to demonstrate the ability to:

**Build → Understand → Threat Model → Attack → Secure → Evaluate → Govern**

agentic AI systems.

---

# Phase 1 — Agentic AI Foundations

**Status:** 🟡 In Progress

## Goal

Develop a strong understanding of how agentic AI systems are built before attempting to secure them.

Security analysis is more effective when I understand how agents actually make decisions, invoke tools, maintain context, communicate with other agents, and interact with external systems.

## Current Training

### Ed Donner — Agentic AI Coursework

Focus areas include:

* Agent architecture
* Agent loops
* Tool calling
* Structured output
* Agent orchestration
* Multi-agent systems
* Agent frameworks
* Memory
* Retrieval
* Model Context Protocol
* Human-in-the-loop workflows
* Agent deployment

## Lab Workflow

For meaningful course labs:

1. Complete the original lab.
2. Document what was built.
3. Explain the architecture in my own words.
4. Identify agent capabilities.
5. Identify data and tool access.
6. Identify trust boundaries.
7. Identify potential security concerns.
8. Determine whether the lab is worth extending.
9. Create an independent security extension when appropriate.

## Portfolio Deliverables

* [ ] Document first Agentic AI course lab
* [ ] Document tool-calling lab
* [ ] Document multi-agent lab
* [ ] Document MCP lab
* [ ] Document human-in-the-loop lab
* [ ] Complete at least one independent security extension

## Exit Criteria

Move into the next phase when I can comfortably explain:

* What makes an AI system agentic
* How tool calling works
* How agents receive and process instructions
* How agents interact with external data
* How agents maintain state or memory
* How multi-agent orchestration works
* Why agent autonomy creates additional security risk

---

# Phase 2 — Agentic AI Security Fundamentals

**Status:** ⚪ Planned

## Goal

Develop a practical understanding of common security risks unique to LLM and agentic AI systems.

## Research Areas

* Prompt injection
* Indirect prompt injection
* System prompt extraction
* Sensitive information disclosure
* Excessive agency
* Unauthorized tool invocation
* Insecure output handling
* Agent goal manipulation
* Memory poisoning
* RAG poisoning
* Malicious tool output
* Tool trust
* Agent-to-agent trust
* Credential exposure
* Over-permissioned agents

## Security Concepts

Apply existing cybersecurity principles to Agentic AI:

### Least Privilege

Agents should only receive the permissions necessary to complete their intended tasks.

### Zero Trust

Agent requests, tool calls, retrieved content, external services, and other agents should not automatically be trusted.

### Defense in Depth

No single guardrail should be treated as sufficient protection.

### Secure-by-Design

Security controls should be built into agent architecture rather than added only after development.

### Human Oversight

High-impact or sensitive actions should require explicit human authorization.

## Portfolio Deliverables

* [ ] Create prompt injection research notes
* [ ] Create indirect prompt injection research notes
* [ ] Document excessive agency
* [ ] Document secure tool-calling principles
* [ ] Document agent least-privilege principles
* [ ] Document common Agentic AI attack surfaces
* [ ] Begin first original security project

---

# Phase 3 — Project 1: Agent Security Playground

**Status:** ⚪ Planned

## Objective

Build a deliberately vulnerable tool-enabled AI agent and use it as a controlled environment for testing Agentic AI security failures.

## Initial Architecture

```text
User
  ↓
Agent
  ├── Read Data Tool
  ├── Search Tool
  ├── Write Tool
  └── Sensitive Action Tool
```

## Vulnerabilities to Explore

* Direct prompt injection
* Indirect prompt injection
* Unauthorized tool execution
* Excessive agency
* Sensitive data exposure
* Poor authorization boundaries
* Malicious tool responses

## Defensive Controls

Implement controls such as:

* Input validation
* Tool allowlisting
* Authorization checks
* Least privilege
* Human approval
* Output validation
* Audit logging
* Secrets management

## Required Documentation

* [ ] README
* [ ] Architecture
* [ ] Threat model
* [ ] Attack scenarios
* [ ] Security test results
* [ ] Defensive controls
* [ ] Lessons learned

## Success Criteria

The project should demonstrate both:

**How an insecure agent fails**

and

**How architectural controls reduce the risk.**

---

# Phase 4 — Model Context Protocol Security

**Status:** ⚪ Planned

## Goal

Understand MCP architecture and investigate the security implications of allowing AI agents to discover and invoke external tools.

## Topics

* MCP architecture
* MCP servers
* MCP clients
* Tool discovery
* Tool permissions
* Trust relationships
* Authentication
* Authorization
* Data exposure
* Malicious MCP servers
* Tool poisoning
* Logging
* Secrets management

## Project: Secure MCP Server

Build a controlled MCP environment exposing security-focused tools.

Possible tools:

* `lookup_ioc`
* `search_cve`
* `query_security_logs`
* `retrieve_alert`
* `create_incident`

## Security Controls

* Authentication
* Authorization
* Input validation
* Tool allowlisting
* Least privilege
* Audit logging
* Human approval for sensitive actions

## Advanced Experiment

Create a controlled malicious MCP server and demonstrate how an agent could be manipulated if tools are trusted without validation.

## Portfolio Deliverables

* [ ] MCP architecture notes
* [ ] MCP threat model
* [ ] Secure MCP server
* [ ] Tool authorization model
* [ ] Malicious MCP lab
* [ ] Security analysis report

---

# Phase 5 — Multi-Agent Security

**Status:** ⚪ Planned

## Goal

Understand how security changes when multiple agents communicate, delegate tasks, and share information.

## Research Areas

* Agent identity
* Agent authentication
* Delegation
* Privilege inheritance
* Agent-to-agent trust
* Compromised agents
* Shared memory
* Cross-agent prompt injection
* Task manipulation
* Privilege escalation
* Orchestrator security

## Lab Questions

For every multi-agent system:

* Which agent is trusted?
* Why is it trusted?
* Can an agent impersonate another?
* Can an agent issue unauthorized instructions?
* Can one compromised agent manipulate the rest?
* Are permissions inherited?
* How is delegation authorized?
* What happens if agents disagree?

## Portfolio Deliverables

* [ ] Multi-agent threat model
* [ ] Compromised-agent experiment
* [ ] Agent delegation security experiment
* [ ] Least-privilege multi-agent architecture

---

# Phase 6 — AI Red Teaming

**Status:** ⚪ Planned

## Goal

Move beyond individual attack experiments and build repeatable adversarial testing workflows for Agentic AI systems.

## Project: Agentic AI Red Team Harness

Create an automated security testing environment.

```text
Red Team Agent
      ↓
Attack Generator
      ↓
Target Agent
      ↓
Security Evaluator
      ↓
Risk Score
      ↓
Security Report
```

## Attack Categories

* Prompt injection
* Indirect prompt injection
* System prompt extraction
* Sensitive data disclosure
* Unauthorized tool invocation
* Human-approval bypass
* Memory poisoning
* Goal hijacking
* RAG poisoning
* Malicious tool responses

## Test Format

Each attack should include:

* Test ID
* Attack description
* Input
* Expected behavior
* Actual behavior
* Result
* Severity
* Security recommendation

Example:

```text
Test ID: PI-001

Attack:
Direct prompt injection

Expected:
Agent refuses unauthorized instruction.

Actual:
Agent attempted privileged tool execution.

Result:
FAIL

Severity:
HIGH

Recommendation:
Require authorization before sensitive tool invocation.
```

## Portfolio Deliverables

* [ ] Attack library
* [ ] Automated testing workflow
* [ ] Security scoring
* [ ] Test reporting
* [ ] Remediation recommendations

---

# Phase 7 — Agentic Cybersecurity System

**Status:** ⚪ Planned

## Project: Agentic SOC Analyst

Apply Agentic AI engineering to a cybersecurity use case.

## Proposed Architecture

```text
Security Alert
      ↓
Triage Agent
      ↓
      ├── IOC Enrichment Agent
      ├── Threat Intelligence Agent
      ├── Log Analysis Agent
      └── MITRE ATT&CK Agent
                    ↓
             Incident Summary
                    ↓
               Human Analyst
```

## Capabilities

The system may:

* Parse alerts
* Extract indicators
* Enrich IOCs
* Retrieve threat intelligence
* Analyze security logs
* Map activity to MITRE ATT&CK
* Generate investigation recommendations
* Create analyst summaries

## Security Boundary

The agent should **not autonomously perform containment actions**.

High-impact actions should require human approval.

Examples:

* Disabling accounts
* Blocking domains
* Isolating endpoints
* Modifying firewall rules
* Deleting data

## Portfolio Value

This project demonstrates:

* Cybersecurity domain knowledge
* AI engineering
* Multi-agent architecture
* AI security controls
* Human oversight
* Threat intelligence
* Security operations

---

# Phase 8 — AI Governance & Compliance

**Status:** ⚪ Planned

## Goal

Develop practical experience evaluating AI systems from governance, compliance, and risk-management perspectives.

## Research Areas

* NIST AI Risk Management Framework
* NIST Cybersecurity Framework
* ISO/IEC 42001
* MITRE ATLAS
* OWASP AI/LLM security guidance
* AI inventories
* AI risk registers
* Human oversight
* AI incident response
* Third-party AI risk
* Evidence management
* AI policy
* Relevant regulatory requirements

## Project

Perform a governance and security assessment of one of my own Agentic AI projects.

## Deliverables

* [ ] AI system inventory
* [ ] System description
* [ ] Data flow diagram
* [ ] Threat model
* [ ] AI risk assessment
* [ ] Risk register
* [ ] Control matrix
* [ ] Human oversight plan
* [ ] Logging requirements
* [ ] Incident response plan
* [ ] AI acceptable-use policy
* [ ] Vendor-risk considerations
* [ ] Framework mapping

## Goal

Demonstrate that I can evaluate an AI system from both:

**Engineering**

and

**Governance/Risk**

perspectives.

---

# Phase 9 — Agent Security Gateway

**Status:** ⚪ Future

## Goal

Build a centralized security layer for Agentic AI interactions.

## Conceptual Architecture

```text
User / Agent
     ↓
Security Gateway
     ↓
 ┌───────────────┐
 │ Prompt Checks │
 │ Data Controls │
 │ Policy Engine │
 │ Authorization │
 │ Logging       │
 └───────┬───────┘
         ↓
        Agent
         ↓
     Tool Request
         ↓
     Authorization
         ↓
        Tool
```

## Potential Capabilities

* Prompt inspection
* Prompt injection detection
* Sensitive-data detection
* Tool-call authorization
* Policy enforcement
* Human approval
* Security logging
* Agent tracing
* Rate limiting
* Risk scoring

This may become a flagship Agentic AI Security Engineering project.

---

# Phase 10 — Portfolio Capstone

**Status:** ⚪ Future

## Goal

Combine the skills developed throughout this repository into a complete enterprise-style Agentic AI security project.

Potential capstone components:

```text
Agentic Application
        +
Secure MCP Environment
        +
Least-Privilege Architecture
        +
Human Approval
        +
Security Monitoring
        +
Red Team Testing
        +
Threat Model
        +
Risk Register
        +
Governance Controls
```

The final capstone should demonstrate the full lifecycle:

**Design**

↓

**Build**

↓

**Threat Model**

↓

**Attack**

↓

**Harden**

↓

**Evaluate**

↓

**Monitor**

↓

**Govern**

---

# Certification Development

Certifications may be used to reinforce the practical work performed in this repository.

Potential areas include:

* AI security
* Secure AI engineering
* Cloud security
* AI governance
* Risk management

Certification study should support hands-on skills rather than replace project experience.

Where possible, certification objectives will be mapped to labs and projects inside this repository.

---

# Project Prioritization

Projects should generally be completed in this order:

1. Agentic AI course labs
2. Agent Security Playground
3. Secure MCP Server
4. Multi-Agent Security Labs
5. Agentic AI Red Team Harness
6. Agentic SOC Analyst
7. AI Governance Assessment
8. Agent Security Gateway
9. Portfolio Capstone

Projects may overlap when coursework introduces relevant concepts earlier.

---

# Current Priorities

## Now

* [ ] Continue Ed Donner Agentic AI coursework
* [ ] Document meaningful labs
* [ ] Practice explaining agent architecture
* [ ] Identify security implications of course projects
* [ ] Build Agentic AI vocabulary
* [ ] Learn tool-calling fundamentals

## Next

* [ ] Research Agentic AI attack surfaces
* [ ] Create first security extension
* [ ] Begin Agent Security Playground
* [ ] Develop first formal AI threat model

## Later

* [ ] Secure MCP project
* [ ] Multi-agent security experiments
* [ ] AI red teaming
* [ ] Agentic SOC project
* [ ] AI governance assessment
* [ ] Agent Security Gateway

---

# Guiding Principle

The purpose of this portfolio is not to collect as many AI projects as possible.

The purpose is to demonstrate increasingly sophisticated understanding of:

**what agents can do,**

**how they can fail,**

**how they can be attacked,**

**how they should be secured,**

and

**how organizations can govern them responsibly.**

Every meaningful project should answer at least one of those questions.
