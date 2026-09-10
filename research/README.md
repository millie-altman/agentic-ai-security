# Agentic AI Security Research

This directory contains technical research and working notes related to the security of autonomous and agentic AI systems.

The goal of this research is not only to document AI security concepts, but to connect each concept to practical attack paths, defensive controls, testing methods, threat models, and future portfolio projects.

## Research Areas

Research may cover topics including:

* Prompt injection
* Indirect prompt injection
* Agent goal hijacking
* Excessive agency
* Tool misuse and tool abuse
* Agent identity
* Agent authentication and authorization
* Identity and privilege abuse
* Model Context Protocol (MCP) security
* Agentic supply chain security
* Memory poisoning
* Context poisoning
* RAG poisoning
* Vector and embedding weaknesses
* Multi-agent security
* Insecure inter-agent communication
* AI red teaming
* Secure agent architecture
* Agent observability and telemetry
* Human-agent trust
* Cascading agent failures
* Unexpected code execution
* Rogue or misaligned agents
* Emerging AI attack techniques

Research notes may later support labs, threat models, security experiments, detection engineering, red-team exercises, or full portfolio projects.

---

## Research Approach

Where possible, each research topic should answer the following questions.

### 1. What is the security issue?

Define the vulnerability, weakness, attack technique, or security concern.

### 2. Why does it exist?

Identify the architectural, technical, or behavioral conditions that allow the weakness to occur.

Examples may include:

* insufficient trust boundaries
* excessive permissions
* excessive autonomy
* untrusted context
* weak authorization
* unsafe tool access
* persistent memory
* insecure agent communication
* insufficient output validation

### 3. What asset is at risk?

Identify what an attacker could affect.

Examples include:

* credentials
* sensitive data
* system prompts
* agent memory
* APIs
* files
* databases
* cloud resources
* user accounts
* connected tools
* business workflows
* other agents

### 4. What would exploitation look like?

Describe a realistic attack path or abuse case.

Research should distinguish between theoretical attacks and attacks that have been demonstrated or observed in real systems.

### 5. What controls could reduce the risk?

Consider controls such as:

* least privilege
* scoped tool permissions
* human approval
* input isolation
* output validation
* authentication
* authorization
* sandboxing
* allowlists
* policy enforcement
* memory validation
* monitoring
* rate limiting
* agent identity controls

### 6. How could the control be tested?

Identify ways to validate whether the defensive control actually works.

Testing may include:

* adversarial prompts
* malicious retrieved documents
* poisoned tool responses
* privilege escalation attempts
* unauthorized tool calls
* memory manipulation
* MCP server abuse
* multi-agent spoofing
* simulated compromised agents

### 7. How does this apply specifically to agentic systems?

Identify what changes when an LLM is able to:

* plan
* reason across multiple steps
* use tools
* access external systems
* retain memory
* communicate with other agents
* execute actions
* make decisions with limited human supervision

The primary question should be:

> What happens when an AI system can act on manipulated information rather than merely generate a response?

---

## Threat Analysis Model

Where appropriate, research notes should document the following attack chain:

**Attacker → Input/Attack Surface → Agent → Decision/Reasoning → Tool or Resource → Security Impact**

Example:

**Malicious webpage → indirect prompt injection → research agent → manipulated reasoning → email tool → unauthorized data disclosure**

This structure helps distinguish traditional LLM security problems from risks created by agent autonomy and tool access.

---

## Security Framework Mapping

Research should be mapped to relevant security frameworks when applicable.

Primary references include:

**OWASP**

* OWASP Top 10 for Agentic Applications
* OWASP Top 10 for LLM Applications
* OWASP GenAI Security Project

**MITRE**

* MITRE ATLAS
* MITRE ATT&CK where traditional infrastructure techniques apply

**NIST**

* NIST AI Risk Management Framework
* NIST Generative AI Profile

**Protocols and Standards**

* Model Context Protocol specification
* OAuth and identity standards where applicable

Mappings should be used to connect research with established security terminology rather than forcing every AI attack into a traditional cybersecurity category.

---

## Research Evidence Levels

Each note may classify evidence as:

**Conceptual**
A theoretically possible weakness or proposed attack.

**Demonstrated**
Researchers have reproduced the attack in a controlled environment.

**Observed**
The weakness has appeared in a real product, deployment, security incident, or disclosed vulnerability.

**Portfolio Tested**
The attack or defensive control has been reproduced safely within this repository.

---

## From Research to Portfolio Project

Research should eventually answer one additional question:

> Can this topic become something I can build, attack, defend, detect, or measure?

Potential outputs include:

**Research Note → Threat Model → Lab → Security Control → Test → Detection → Portfolio Project**

For example:

**Indirect Prompt Injection**

Research
↓
Threat model an AI research agent
↓
Create a malicious webpage or document
↓
Allow the agent to retrieve it
↓
Attempt to manipulate an agent tool call
↓
Implement tool authorization controls
↓
Retest the attack
↓
Document results

This approach turns theoretical research into demonstrable security engineering experience.

---

## Source Standards

Sources should prioritize:

1. Official specifications and standards
2. Government cybersecurity organizations
3. OWASP
4. MITRE
5. Academic research
6. Established security research organizations
7. Vendor security research
8. Reputable independent technical research

Blog posts, social media, and community discussions may be useful for identifying emerging techniques but should not be treated as authoritative without additional verification.

---

## Research Status

Research notes can use the following status labels:

`NOT STARTED`

`RESEARCHING`

`READY FOR LAB`

`LAB IN PROGRESS`

`TESTED`

`PORTFOLIO PROJECT`

The long-term objective is to move high-value research topics from **RESEARCHING** toward **TESTED** or **PORTFOLIO PROJECT** whenever practical.
