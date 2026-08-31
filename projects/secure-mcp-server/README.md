Build an MCP server exposing something simple like:

get_security_alert()
search_ioc()
lookup_cve()
query_logs()
create_incident()

But then implement:

authentication
authorization
tool allowlisting
parameter validation
rate limiting
audit logging
secrets management
least privilege
human approval for sensitive actions

Then create a malicious MCP server and show what can happen when an agent blindly trusts tools.

Your report could literally be:

"Threat Modeling Model Context Protocol in Enterprise Agentic Systems."
