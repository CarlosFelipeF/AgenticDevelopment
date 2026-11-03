# Agentic Security Checklist

> **For platform operators and security teams.**
> This checklist covers infrastructure and platform-level controls that secure AI agent operations.
> For agent behavior rules, see `AGENTS.md` and `.agent/SECURITY.md`.

## Purpose

AGENTS.md tells agents how to behave. This checklist ensures the platform enforces security even when agents misbehave.

**Relationship:**
- **AGENTS.md** = Instructions TO the agent (behavioral)
- **This Checklist** = Controls AROUND the agent (infrastructure)

---

## Coding Agent Baseline (start here)

The ten controls that matter most for teams using AI coding agents. Copy-ready versions are in
`examples/enforcement/`; check your setup with `scripts/agent-doctor.sh`.

- [ ] **Protected `main`:** pull request required, at least one human approval, required status checks
- [ ] **CODEOWNERS** on `AGENTS.md`, `.agent/`, tool config and CI workflows
- [ ] **Secret scanning** at three points: pre-commit, CI, and host push protection
- [ ] **Tool permission deny-lists** for secret files, force push, `--no-verify` and `sudo`
- [ ] **Sandboxed execution:** agents run in a container or VM, not on a laptop with your SSH keys
- [ ] **Egress allowlist:** agents can reach package registries and docs, not arbitrary hosts
- [ ] **Separate agent credentials** with least privilege and short lifetimes
- [ ] **Approved MCP servers / plugins list**, reviewed like any other dependency
- [ ] **Dependency review** in CI blocks known-vulnerable and unexpected packages
- [ ] **Audit trail:** agent sessions, tool calls and approvals are logged and kept

## OWASP Agentic Security Controls

### ASI01: Agent Goal Hijack

**Platform Controls:**
- [ ] Untrusted content (issues, web pages, files, tool output) is labelled and isolated from instructions
- [ ] Rule of Two applied: no agent session combines untrusted input, sensitive data and external actions without human approval
- [ ] Instruction hierarchy enforcement (system > user > context)
- [ ] Prompt logging for audit and detection
- [ ] Anomaly detection for injection patterns

**Implementation Notes:**
```
□ Review: Input validation rules documented
□ Test: Injection attack test suite runs on CI
□ Monitor: Unusual prompt patterns trigger alerts
```

### ASI02: Tool Misuse & Exploitation

**Platform Controls:**
- [ ] Tool allowlisting per agent role
- [ ] Parameter validation for all tool calls
- [ ] Rate limiting on tool invocations
- [ ] Tool call logging with full parameters

**Implementation Notes:**
```
□ Config: Tool permissions defined per environment
□ Audit: Tool usage reports generated weekly
□ Alert: Blocked tool calls trigger review
```

### ASI03: Identity & Privilege Abuse

**Platform Controls:**
- [ ] Agents have their own identities (not a human's personal token)
- [ ] Least-privilege IAM roles for agent operations
- [ ] Short-lived, task-scoped credentials where possible
- [ ] Credential rotation automated (< 90 days)
- [ ] No long-lived credentials in agent context
- [ ] Secrets injected at runtime, never stored in prompts

**Implementation Notes:**
```
□ Review: IAM policies audited quarterly
□ Scan: Credential scanning in CI pipeline
□ Rotate: Automated rotation schedule configured
```

### ASI04: Agentic Supply Chain Vulnerabilities

**Platform Controls:**
- [ ] MCP server validation and signing
- [ ] Dependency scanning in CI/CD
- [ ] SBOM generation for agent deployments
- [ ] Verified publisher requirements for plugins/tools
- [ ] New dependencies checked for existence and reputation (AI "slopsquatting" defence)
- [ ] GitHub Actions and other CI dependencies pinned to commit SHAs

**Implementation Notes:**
```
□ Scan: Dependabot/Snyk/etc. configured
□ Policy: Only approved MCP servers allowed
□ Audit: Dependency changes reviewed before merge
```

### ASI05: Unexpected Code Execution (RCE)

**Platform Controls:**
- [ ] Container/VM isolation for agent execution
- [ ] Network policies restricting agent egress
- [ ] Filesystem access limited to working directories
- [ ] Resource limits (CPU, memory, disk) enforced

**Implementation Notes:**
```
□ Infra: Containers run with restricted privileges
□ Network: Egress allowlist defined and enforced
□ Monitor: Resource usage tracked and alerted
```

### ASI06: Memory & Context Poisoning

**Platform Controls:**
- [ ] Session isolation between users/tasks
- [ ] RAG source vetting before inclusion
- [ ] Context window size limits
- [ ] Persisted state encryption and integrity checks

**Implementation Notes:**
```
□ Design: Sessions cannot access other sessions' data
□ Validate: RAG sources are vetted and signed
□ Encrypt: At-rest encryption for persisted context
```

### ASI07: Insecure Inter-Agent Communication

**Platform Controls:**
- [ ] Agent-to-agent authentication required
- [ ] Message signing and verification
- [ ] TLS for all inter-agent communication
- [ ] Message logging for audit trail

**Implementation Notes:**
```
□ Auth: Agents authenticate via mutual TLS or tokens
□ Verify: Message signatures validated before processing
□ Log: All inter-agent messages logged with timestamps
```

### ASI08: Cascading Failures

**Platform Controls:**
- [ ] Circuit breakers between agent components
- [ ] Rate limiting on cascading calls
- [ ] Graceful degradation paths defined
- [ ] Timeout enforcement at all boundaries

**Implementation Notes:**
```
□ Pattern: Circuit breaker pattern implemented
□ Limits: Maximum call depth configured
□ Fallback: Degraded mode behavior defined
```

### ASI09: Human-Agent Trust Exploitation

**Platform Controls:**
- [ ] Agent identity verification mechanisms
- [ ] Claimed permission validation against actual grants
- [ ] Audit logging of permission checks
- [ ] Human-in-the-loop for privilege escalation
- [ ] Reviewers can see which changes were agent-authored (commit trailers, PR template)
- [ ] Approval prompts show the exact action, not a summary an agent wrote

**Implementation Notes:**
```
□ Verify: Permission claims checked against IAM
□ Log: All escalation requests logged
□ Approve: Human approval workflow implemented
```

### ASI10: Rogue Agents

**Platform Controls:**
- [ ] Kill switch for immediate agent termination
- [ ] Real-time monitoring of agent behavior
- [ ] Automated policy violation response
- [ ] Guardrail bypass detection and alerting
- [ ] Agents cannot change their own governance files or permissions (CODEOWNERS, deny rules)

**Implementation Notes:**
```
□ Ops: Kill switch tested monthly
□ Monitor: Real-time behavior analysis running
□ Alert: Policy violations trigger immediate review
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Security controls from above implemented
- [ ] Penetration testing completed
- [ ] Threat model reviewed
- [ ] Incident response runbook prepared

### Production Readiness

- [ ] Monitoring and alerting configured
- [ ] Logging and audit trail verified
- [ ] Backup and recovery tested
- [ ] Access controls reviewed

### Post-Deployment

- [ ] Security metrics baseline established
- [ ] Regular security reviews scheduled
- [ ] Incident response drills conducted
- [ ] Continuous improvement process active

---

## Audit Evidence Locations

| Control Area | Evidence Location |
|--------------|-------------------|
| Access Logs | `/var/log/agent-access/` or CloudWatch |
| Tool Invocations | Audit table in database |
| Configuration | Version control + config management |
| Incidents | Incident management system |

---

## Review Schedule

| Review Type | Frequency | Owner |
|-------------|-----------|-------|
| Control Verification | Weekly | Security Team |
| Access Review | Monthly | Platform Team |
| Penetration Testing | Quarterly | Security Team |
| Full Security Audit | Annually | External Auditor |

---

*This checklist aligns with the [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), ASI01–ASI10.*
*Last updated: 2026-11*
