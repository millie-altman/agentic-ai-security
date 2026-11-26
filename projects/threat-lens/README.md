# ThreatLens
*An Agentic AI-Powered Cyber Threat Intelligence Platform*

## Project Objectives
1. Personal research assistant: Automate repetitive threat intelligence collection and analysis.
2. Public educational resource: Translate complex cybersecurity incidents and language into understandable intelligence briefs.
3. Professional portfolio deliverable: Demonstrate agentic AI engineering, cybersecurity, automation, and secure system design.

## Core Capabilities
- **Intelligence Collection** | collect recent cybersecurity news, vulnerability disclosures, government advisories, vendor reports, and threat actor activity from trusted, verifiable sources.
- **Source Verification** | cross-reference claims, identify conflicting information, distinguish speculation from confirmed facts, and evaluate source credibility
- **Threat Intelligence Analysis** | extract CVEs, IoCs, affected organizations, threat actors, attack vectors, and relevant MITRE ATT&CK techniques where supported by evidence.
- **Risk & Impact Assessment** | evaluate potential impacts on individuals, businesses, government organizations, and critical infrastructure.
- **Intelligence Report Generation** | generate technical intelligence reports, executrive summaries, public-facing explanations, and draft CGC research articles.
- **Human in the Loop Review** | require human verification and approval before any intellignece is published or externally distributed.

## Agentic Architecture
Intelligence Sources (CISA, NVD, MITRE, Vendor advisories, News, RSS)

--> 

Threat Lens Orchestrator (Task delegation, workflow state, and permissions)

--> 

Collection Agent (retrieves and normalizes intelligence), 
Verification Agent (validates claims and sources), 
Analysis Agent (extracts threats, CVEs and IoCs), 
Enrichment Agent (adds MITRE and vulnerability context),
Risk Agent (evaluates severity and impact), and 
Reporting Agent (generates intelligence products)

--> 

Security & Quality Validation (schema validation, citation checks, injection defense, confidence assessment)

--> 

Human Review & Approval (with links to sites and sources for verification)

--> 

Technical CTI Report, Executive Brief, Public Cyber Advisory, CGC Research Article

## Intelligence Sources
**Source** |	*Intelligence type*
[CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |	Known exploited vulnerabilities
[NIST NVD](https://nvd.nist.gov)	| CVEs and vulnerability metadata
[MITRE ATT&CK](https://attack.mitre.org)	| Adversary tactics and techniques
[FIRST EPSS](https://www.first.org/epss/)	| Vulnerability exploitation probability
[AlienVault OTX](https://otx.alienvault.com)	| Community threat intelligence
[Microsoft Security Blog](https://cloud.google.com/blog/topics/threat-intelligence)	| Threat research and advisories
[Google Threat Intelligence](https://cloud.google.com/blog/topics/threat-intelligence) | Threat actors and campaigns
[BleepingComputer](https://www.bleepingcomputer.com)	| Cybersecurity news
[The Hacker News](https://thehackernews.com)	| Emerging cybersecurity events
[Cisco Talos](https://blog.talosintelligence.com)	| Technical threat research

---

## Development Checklist
### Phase 1 — Intelligence collection
- [ ] Create GitHub repository and local environment
- [ ] Integrate CISA KEV and NVD
- [ ] Implement RSS feed collection
- [ ] Normalize intelligence into structured JSON
- [ ] Implement deduplication and timestamps

### Phase 2 — AI analysis
- [ ] Connect LLM API
- [ ] Create structured intelligence schemas
- [ ] Implement incident summarization
- [ ] Extract CVEs, IOCs and threat actors
- [ ] Implement source citations and uncertainty labels

### Phase 3 — Agentic workflows
- [ ] Implement LangGraph orchestration
- [ ] Create specialized agents
- [ ] Implement workflow state and persistence
- [ ] Add human-in-the-loop review
- [ ] Implement failure handling and retries

### Phase 4 — Security engineering
- [ ] Create system threat model
- [ ] Implement prompt injection defenses
- [ ] Restrict agent tool permissions
- [ ] Test hallucinations and unsupported attribution
- [ ] Implement audit logging and API budget limits

### Phase 5 — Dashboard and reporting
- [ ] Build Streamlit dashboard
- [ ] Generate technical intelligence briefs
- [ ] Generate public-facing summaries
- [ ] Export reports to Markdown and JSON
- [ ] Implement review and approval queue

### Phase 6 — Portfolio publication
- [ ] Complete functional and security evaluations
- [ ] Create architecture diagrams
- [ ] Record demonstration video
- [ ] Publish sanitized GitHub repository
- [ ] Publish CGC Research Lab write-up

## Technology Stack (estimated implemetnation phase)
- Python (MVP)
- Requests/HTTPX (MVP)
- Feedparser (MVP)
- Pydantic (MVP)
- OpenAI API (MVP)
- SQL Lite (MVP)
- Pytest (MVP)
- Streamlit (dashboard)
- LangGraph (agentic orchestration)
- ChromaDB (optional historical intelligence retrieval)
- n8n (scheduled intelligence collection)
- Docker (deployment)
- GitHub Actions (CI/CD)
- AWS (optional cloud deployment)

## Security Engineering Considerations
**Security Risk** | *Proposed Control*
Indirect prompt injection |	Separate retrieved content from instructions and restrict tool execution
Hallucinated intelligence |	Evidence-backed claims and citation validation
False threat attribution |	Explicit confidence and uncertainty labels
Data poisoning |	Source provenance and cross-source verification
Excessive agency |	Least-privilege tools and approval gates
Malicious URLs |	No automatic execution or unrestricted browsing
SSRF	| Allowlisted sources and network restrictions
API abuse |	Rate limits, token budgets and execution limits
Sensitive data exposure |	Secret management and output filtering
Duplicate or outdated intelligence |	Deduplication and freshness checks
