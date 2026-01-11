# AGENTIC-SECURITY-CHECKLIST.md

> Platform Security Controls for AI Agent Deployments  
> Based on OWASP Top 10 for Agentic Applications 2026

---

## Purpose

This document is for **platform teams, DevOps engineers, and security architects** who deploy and govern AI agent systems. It covers infrastructure-level security controls that agents themselves cannot implement.

For agent behavioral rules (what the agent should and shouldn't do), see `AGENTS.md`.

---

## OWASP Agentic Security Initiative (ASI) Controls

### ASI01: Agent Goal Hijack

**Risk**: Attackers manipulate the agent's objectives through prompt injection, causing it to pursue malicious goals while appearing to operate normally.

**Real-World Example**: EchoLeak incident — attackers embedded instructions in web content that caused agents to exfiltrate data.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Input sanitization | Filter/escape special characters in all external inputs | Critical |
| Instruction boundaries | Use clear delimiters between system prompts and user content | Critical |
| Goal validation | Implement semantic checks on agent objectives | High |
| Behavior monitoring | Log and analyze goal drift patterns | High |
| Prompt hardening | Test prompts against injection attacks before deployment | Critical |

**Checklist**:
- [ ] All external inputs are sanitized before reaching the agent
- [ ] System prompts use clear structural boundaries
- [ ] Agent outputs are validated against expected goal categories
- [ ] Anomaly detection monitors for goal drift
- [ ] Prompt injection testing is part of CI/CD pipeline

---

### ASI02: Tool Misuse

**Risk**: Agents use their tools in unintended or dangerous ways, either through manipulation or emergent behavior.

**Real-World Example**: Amazon Q agent was poisoned to run destructive AWS CLI commands.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Tool whitelisting | Explicit list of allowed tools per agent role | Critical |
| Parameter validation | Validate all tool inputs against schemas | Critical |
| Rate limiting | Limit tool invocations per time window | High |
| Dangerous operation blocks | Hard blocks on destructive commands (rm -rf, DROP TABLE, etc.) | Critical |
| Tool audit logging | Log all tool invocations with full parameters | High |

**Checklist**:
- [ ] Each agent role has an explicit tool allowlist
- [ ] Tool parameters are validated against JSON schemas
- [ ] Destructive operations require human approval
- [ ] Tool usage is rate-limited per session/agent
- [ ] All tool invocations are logged with timestamps and parameters

---

### ASI03: Identity & Privilege Abuse

**Risk**: Agents operate with excessive permissions, or attackers steal/abuse agent credentials.

**Real-World Example**: Leaked API keys in agent configurations; over-privileged service accounts.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Least privilege | Agents get minimum permissions for their tasks | Critical |
| Credential isolation | Separate credentials per agent instance | High |
| Short-lived tokens | Use tokens with < 1 hour expiry | High |
| Credential rotation | Automate regular rotation | High |
| Privilege escalation detection | Alert on attempts to access unauthorized resources | Critical |

**Checklist**:
- [ ] Agents use service accounts with minimal permissions
- [ ] No shared credentials between agents
- [ ] Tokens expire within 1 hour
- [ ] Credentials are never hardcoded or logged
- [ ] Privilege escalation attempts trigger alerts

---

### ASI04: Supply Chain Vulnerabilities

**Risk**: Malicious or compromised components in the agent's dependencies, plugins, or connected services.

**Real-World Example**: Malicious MCP servers; GitHub MCP exploit; poisoned npm/pip packages.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Dependency scanning | Automated vulnerability scanning in CI/CD | Critical |
| Package pinning | Lock all dependencies to specific versions | High |
| Plugin/MCP validation | Vet and approve all external integrations | Critical |
| SBOM generation | Maintain Software Bill of Materials | High |
| Update cadence | Regular security updates with testing | High |

**Checklist**:
- [ ] `npm audit` / `pip-audit` / `cargo audit` runs in CI
- [ ] All dependencies are version-locked
- [ ] MCP servers and plugins are from trusted sources only
- [ ] SBOM is generated and maintained
- [ ] Security updates are applied within 7 days of disclosure

---

### ASI05: Unexpected Code Execution

**Risk**: Agents execute or generate code that performs unauthorized actions.

**Real-World Example**: AutoGPT RCE — agents were tricked into executing shell commands.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Sandboxing | Run agent-generated code in isolated environments | Critical |
| Code review gates | Require approval before executing generated code | High |
| Execution limits | Time, memory, and process limits on code execution | Critical |
| Network isolation | Generated code cannot make arbitrary network calls | High |
| Output sanitization | Filter dangerous patterns in generated code | High |

**Checklist**:
- [ ] Code execution happens in sandboxed containers
- [ ] Containers have resource limits (CPU, memory, time)
- [ ] Network access is restricted to approved endpoints
- [ ] Generated code is scanned for dangerous patterns
- [ ] Production systems cannot be directly modified by agents

---

### ASI06: Memory & Context Poisoning

**Risk**: Attackers corrupt the agent's memory, context, or RAG knowledge base to manipulate future behavior.

**Real-World Example**: Gemini Memory Attack — malicious content persisted in agent memory, affecting subsequent sessions.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Memory validation | Validate content before storing in agent memory | Critical |
| Context isolation | Separate contexts between users/sessions | Critical |
| RAG source vetting | Only index trusted document sources | High |
| Memory expiration | Automatic cleanup of old context | Medium |
| Poisoning detection | Monitor for anomalous memory content | High |

**Checklist**:
- [ ] Memory writes are validated for malicious content
- [ ] User contexts are strictly isolated
- [ ] RAG sources are from approved, vetted origins only
- [ ] Memory has TTL and automatic cleanup
- [ ] Anomaly detection monitors memory content patterns

---

### ASI07: Insecure Inter-Agent Communication

**Risk**: In multi-agent systems, attackers spoof messages between agents or intercept communications.

**Real-World Example**: Man-in-the-middle attacks on agent orchestration; spoofed agent messages.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Message authentication | Sign all inter-agent messages | Critical |
| Transport encryption | TLS for all agent-to-agent communication | Critical |
| Agent identity verification | Verify sender identity before processing | High |
| Message integrity | Detect tampering in transit | High |
| Communication logging | Log all inter-agent messages | Medium |

**Checklist**:
- [ ] All inter-agent communication uses TLS
- [ ] Messages are signed with agent-specific keys
- [ ] Receiving agents verify message signatures
- [ ] Message tampering triggers alerts
- [ ] Communication is logged for audit

---

### ASI08: Cascading Failures

**Risk**: Errors or attacks propagate through agent systems, causing widespread failures.

**Real-World Example**: Single agent failure causing chain reaction across dependent systems.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Circuit breakers | Automatic isolation of failing agents | Critical |
| Error boundaries | Contain failures within agent scope | High |
| Retry limits | Prevent infinite retry loops | High |
| Graceful degradation | Systems continue with reduced functionality | Medium |
| Blast radius limits | Limit each agent's potential impact | High |

**Checklist**:
- [ ] Circuit breakers automatically isolate failing agents
- [ ] Agents have retry limits (max 3-5 retries)
- [ ] Errors are contained and don't cascade
- [ ] Systems degrade gracefully without agents
- [ ] Each agent's blast radius is documented and limited

---

### ASI09: Human-Agent Trust Exploitation

**Risk**: Attackers leverage human trust in AI agents for social engineering.

**Real-World Example**: AI-powered phishing; deepfake agents impersonating trusted entities.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Agent identification | Clear indicators that user is talking to an agent | High |
| Authority limits | Agents cannot authorize high-risk actions alone | Critical |
| Verification protocols | Multi-factor approval for sensitive operations | High |
| Impersonation detection | Detect attempts to impersonate humans or other agents | High |
| User education | Train users on agent interaction security | Medium |

**Checklist**:
- [ ] Agents clearly identify themselves as AI
- [ ] High-risk actions require human verification
- [ ] Multi-factor approval for financial/access changes
- [ ] Users are trained on secure agent interaction
- [ ] Impersonation attempts are detected and logged

---

### ASI10: Rogue Agents

**Risk**: Agents bypass governance, ignore instructions, or operate outside intended boundaries.

**Real-World Example**: Agents ignoring kill switches; circumventing guardrails.

| Control | Implementation | Priority |
|---------|----------------|----------|
| Kill switches | Immediate termination capability for all agents | Critical |
| Behavioral monitoring | Real-time detection of out-of-bounds behavior | Critical |
| Governance enforcement | Technical controls that cannot be bypassed by agents | Critical |
| Heartbeat checks | Continuous verification that agents are responsive | High |
| Containment protocols | Automatic isolation of rogue agents | Critical |

**Checklist**:
- [ ] Kill switches exist and are tested regularly
- [ ] Kill switches work even if agent is unresponsive
- [ ] Behavioral monitoring detects policy violations
- [ ] Agents send regular heartbeats
- [ ] Rogue agents are automatically contained

---

## Implementation Priority Matrix

| Priority | Controls | Timeline |
|----------|----------|----------|
| **Critical** | Kill switches, sandboxing, input sanitization, least privilege, tool whitelisting | Before production |
| **High** | Rate limiting, audit logging, circuit breakers, memory validation | Within 30 days |
| **Medium** | SBOM, user education, communication logging, graceful degradation | Within 90 days |

---

## Incident Response Checklist

When an agentic security incident occurs:

1. **Contain**: Activate kill switch for affected agents
2. **Preserve**: Capture logs, memory state, and context
3. **Investigate**: Determine attack vector (which ASI category)
4. **Remediate**: Patch vulnerability, update controls
5. **Report**: Document incident and lessons learned
6. **Improve**: Update checklist and monitoring

---

## Audit Schedule

| Audit Type | Frequency | Owner |
|------------|-----------|-------|
| Dependency scan | Daily (automated) | CI/CD |
| Permission review | Monthly | Security team |
| Kill switch test | Monthly | Platform team |
| Penetration test | Quarterly | External auditor |
| Full security review | Annually | Security + External |

---

## References

- [OWASP Top 10 for Agentic Applications 2026](https://owasp.org/www-project-top-10-for-agentic-applications/)
- [OWASP Agentic Security Initiative](https://owasp.org/www-project-agentic-security/)
- [MITRE ATLAS (AI Threat Landscape)](https://atlas.mitre.org/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-11  
**Owner:** Platform Security Team
