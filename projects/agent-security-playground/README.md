Agent Security Playground

Difficulty: Beginner → Intermediate

Build a deliberately vulnerable agent with several tools.

For example:

User
  ↓
LLM Agent
  ├── read_file()
  ├── search_documents()
  ├── send_email()
  └── update_database()

Then demonstrate vulnerabilities:

prompt injection
indirect prompt injection
unauthorized tool calls
excessive agency
sensitive-data disclosure
poisoned RAG content
memory poisoning
malicious tool output

Then build the hardened version.

User
 ↓
Input Validation
 ↓
Agent
 ↓
Policy Engine
 ↓
Tool Authorization
 ↓
Tool
 ↓
Output Validation
 ↓
Audit Log

Portfolio deliverables:

architecture.md
threat-model.md
attack-scenarios.md
security-controls.md
demo.py
tests/
README.md
