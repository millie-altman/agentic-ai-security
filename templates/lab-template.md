# Lab: [Lab Name]

## Lab Information

**Course:** [Course Name]
**Instructor:** [Instructor Name]
**Platform:** [Udemy / Other]
**Module:** [Module or Section]
**Date Completed:** [YYYY-MM-DD]
**Status:** 🟡 In Progress / 🟢 Complete

---

## Objective

Briefly describe what this lab was designed to teach.

**Primary concepts:**

* [Concept]
* [Concept]
* [Concept]

---

## What I Built

Describe the system, agent, workflow, or application created during the lab.

### Components

* **Agent(s):** [Description]
* **Model(s):** [Description]
* **Tools:** [Description]
* **Data Sources:** [Description]
* **Memory:** [None / Description]
* **External Services:** [Description]

---

## Architecture

Describe how the components interact.

```text
User
  ↓
Agent
  ↓
[Tool / Model / Service]
  ↓
Response
```

> Add an architecture diagram here later if the lab becomes significant enough to warrant one.

---

## How It Works

1. [Step]
2. [Step]
3. [Step]
4. [Step]

---

## Key Concepts Learned

### [Concept 1]

Explain the concept in your own words.

### [Concept 2]

Explain the concept in your own words.

### [Concept 3]

Explain the concept in your own words.

---

# Security Analysis

## Agent Capabilities

What is the agent actually capable of doing?

* [Capability]
* [Capability]

## Data Access

What information can the agent access?

* [Data]
* [Data]

**Sensitive data involved:** Yes / No

If yes, describe:

[Description]

---

## Tool Access

| Tool   | Purpose   | Read/Write | Risk Level |
| ------ | --------- | ---------- | ---------- |
| [Tool] | [Purpose] | Read       | Low        |
| [Tool] | [Purpose] | Write      | High       |

---

## Trust Boundaries

Identify where information or instructions cross between different components.

Examples:

* User → Agent
* Agent → Tool
* Agent → External API
* Retrieved content → Agent
* Agent → Database
* Agent → Agent

**Identified trust boundaries:**

1. [Boundary]
2. [Boundary]

---

## Potential Attack Surface

Consider whether the system could be affected by:

* [ ] Direct prompt injection
* [ ] Indirect prompt injection
* [ ] System prompt extraction
* [ ] Sensitive information disclosure
* [ ] Unauthorized tool invocation
* [ ] Excessive agency
* [ ] Malicious tool output
* [ ] Memory poisoning
* [ ] Retrieval/RAG poisoning
* [ ] Insecure output handling
* [ ] Credential or secret exposure
* [ ] Agent goal manipulation
* [ ] Other: __________

---

## Security Questions

### What happens if the user provides malicious instructions?

[Analysis]

### Could external content manipulate the agent?

[Analysis]

### Could the agent perform an action the user should not be authorized to perform?

[Analysis]

### Does the agent have more permissions than it actually needs?

[Analysis]

### Could sensitive information appear in prompts, logs, memory, or outputs?

[Analysis]

### Which actions should require human approval?

[Analysis]

### What should be logged for security monitoring?

[Analysis]

---

# Security Extension

> Complete this section if I extend the original lab with independent security work.

**Security Extension Status:** Not Started / Planned / In Progress / Complete

## Security Problem

Describe the security issue being investigated.

## Hypothesis

What do I expect to happen?

## Attack Scenario

Describe the attack or failure scenario.

```text
Attacker / Malicious Input
          ↓
        Agent
          ↓
     [Weakness]
          ↓
   Security Impact
```

## Security Controls Implemented

* [Control]
* [Control]
* [Control]

## Results

Describe what happened before and after implementing the security controls.

### Before

[Result]

### After

[Result]

---

## Evidence

Evidence may include:

* Screenshots
* Logs
* Agent traces
* Test results
* Prompt/response examples
* Security events
* Architecture diagrams

Store supporting evidence in the lab directory where appropriate.

---

## Lessons Learned

### Technical

[What I learned about Agentic AI engineering.]

### Security

[What I learned about securing the system.]

### What I Would Change

[What I would design differently.]

---

## Next Steps

* [ ] [Next step]
* [ ] [Next step]
* [ ] Consider security extension
* [ ] Consider converting this lab into an independent project

---

## References

* [Course/module]
* [Official documentation]
* [Security reference]
* [Framework or standard]

---

## Attribution

This lab was completed as part of **[Course Name]** by **[Instructor]**.

The implementation, notes, security analysis, testing, modifications, and security extensions documented here represent my own learning and independent work unless otherwise noted.
