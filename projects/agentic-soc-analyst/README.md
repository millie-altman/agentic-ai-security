                ┌─ IOC Agent
                │
SIEM Alert → Triage Agent
                │
                ├─ Threat Intel Agent
                │
                ├─ Log Analysis Agent
                │
                └─ MITRE ATT&CK Agent
                         ↓
                  Incident Summary
                         ↓
                   Human Analyst

Give the system synthetic alerts.

The agents could:

parse the alert
extract indicators
enrich IOCs
identify relevant ATT&CK techniques
retrieve supporting intelligence
assign a preliminary severity
generate investigation recommendations
produce an analyst report

But the agent cannot autonomously contain anything.

Containment requires human authorization.

Demonstrating:

AI engineering + SOC + CTI + security controls + human-in-the-loop design.
