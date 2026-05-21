# Security Policy

## Supported Versions

Only the **current `main` branch** is supported for security updates and fixes. We recommend all users keep their installation up-to-date with the latest commits on the `main` branch.

| Version | Supported | Notes |
|---------|-----------|-------|
| `main` branch (current) | ✅ Yes | Latest development; receives all security patches |
| Tagged releases | ⚠️ Best effort | No guaranteed support; recommend tracking `main` |
| Older branches | ❌ No | No security patches provided |

---

## Reporting a Vulnerability

We take security vulnerabilities seriously and appreciate responsible disclosure. **Do not open a public GitHub issue** to report a security vulnerability, as this exposes the problem before a fix is available.

### How to Report

1. **Email Address:** sambitmondal2005@gmail.com
2. **Include in your report:**
   - Description of the vulnerability (what component, what risk)
   - Steps to reproduce (if applicable)
   - Potential impact (data exposure, unauthorized access, etc.)
   - Your suggested fix (optional)

3. **What to expect:**
   - **Acknowledgment** within **48 hours** of receipt
   - Initial assessment of severity and impact
   - Timeline for fix and patch release
   - Credit in the security advisory (if desired)

### Responsible Disclosure Timeline

- **T+0 hours:** Vulnerability reported
- **T+48 hours:** Acknowledgment from maintainers
- **T+5-10 days:** Security patch prepared and tested
- **T+15 days:** Patch released and advisory published
- **Advisory:** Published on GitHub Security Advisories

---

## ⚠️ Architectural Disclaimer: NOT PRODUCTION-READY AS-IS

**This repository represents a localized enterprise architecture demonstration.** The codebase prioritizes clarity, modularity, and educational value. **It is NOT suitable for direct deployment to live production environments without significant hardening.**

### Pre-Production Requirements

Before deploying **any component** of Nexus Copilot to a production environment, implementors **must** add the following security layers:

#### 1. Authentication & Authorization

- **Implement OAuth 2.0 / OpenID Connect** for user authentication
  - Recommended providers: AWS Cognito, Azure AD, Auth0, Okta
  - All API endpoints in `api-gateway` must validate JWT tokens
  - Example: Add `@auth_required` decorator to all routes
  
- **Role-Based Access Control (RBAC)**
  - Implement permission checks before document retrieval
  - Restrict document access by user/department
  - Audit all query operations for compliance

**Reference:** See `api-gateway/app/main.py` for middleware architecture; authentication should be added here.

#### 2. Secure gRPC Communication

- **Enable TLS 1.3 for all gRPC channels** between `api-gateway` and `ingestion-worker`
  - Generate self-signed certificates for local testing
  - Use managed certificates (AWS ACM, GCP Certificate Manager) in production
  - Enforce mutual TLS (mTLS) for service-to-service authentication

**Current State:** Plain-text gRPC communication in `docker-compose.yml`  
**Required for Production:**
```yaml
# In docker-compose.yml or Kubernetes manifests:
# - Configure TLS certificates in gRPC server initialization
# - Validate certificate chains on client side
# - Enable certificate rotation
```

**Reference:** `ingestion-worker/app/main.py` line where gRPC server is initialized.

#### 3. Data Storage & Network Security

- **Pinecone Network Restrictions**
  - Enable IP whitelisting for API access
  - Use VPC Service Endpoints where available
  - Rotate API keys every 90 days
  - Disable public internet access; use private network links

- **Redis Network Security**
  - Enable Redis ACL (Access Control Lists) for user authentication
  - Enforce TLS encryption in transit
  - Use AWS ElastiCache with encryption at rest in production
  - Restrict to private subnets; no internet exposure

**Reference:** `api-gateway/app/cache.py` and `docker-compose.yml` Redis configuration.

#### 4. API Security

- **Rate Limiting**
  - Implement per-user/per-IP rate limits (recommended: 100 requests/min)
  - Use middleware like `slowapi` in FastAPI

- **CORS Hardening**
  - Current `CORSMiddleware` allows `*` (all origins)
  - Production: Restrict to specific domains
  - See `api-gateway/app/main.py` for CORS configuration

- **Input Validation**
  - All file uploads limited to 50MB (already enforced)
  - Implement malware scanning for uploaded PDFs
  - Validate all query parameters and JSON payloads

#### 5. Secrets Management

- **Remove hardcoded secrets**
  - All API keys (.env) must use external secret managers
  - AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault recommended

- **API Key Rotation**
  - Groq API Key: Rotate every 180 days
  - Pinecone API Key: Rotate every 90 days
  - HuggingFace Token: Rotate every 180 days

**Current State:** `.env` file in repository root (development only)  
**Production:** Use external secret management; never commit `.env`

#### 6. Logging & Monitoring

- **Centralized Logging**
  - Ship logs to ELK Stack, Splunk, or CloudWatch
  - Retain audit logs for 1+ years
  - Monitor for suspicious patterns (failed auth, rate limit violations)

- **Security Monitoring**
  - Set up alerts for failed document uploads
  - Alert on unusual query patterns
  - Monitor gRPC error rates and latencies

**Reference:** `api-gateway/app/logger.py` and `ingestion-worker/app/logger.py` for logging architecture.

#### 7. Database & Data Protection

- **Encryption at Rest**
  - Pinecone: Ensure encryption enabled at account level
  - Redis: Use managed services with encryption at rest
  - All backups must be encrypted

- **Data Retention & Deletion**
  - Implement document retention policies
  - Provide user-requested data deletion workflows
  - Comply with GDPR, CCPA, and regional regulations

---

## Security Best Practices

### During Development

- [ ] Never commit API keys, tokens, or database passwords
- [ ] Use `.env.example` as a template; document all required variables
- [ ] Review dependencies monthly for known vulnerabilities:
  ```bash
  cd api-gateway && pip install -U pip && pip install pipdeptree && pip-audit
  cd ingestion-worker && pip-audit
  cd client && npm audit
  ```
- [ ] Enable branch protection on `main`; require code reviews before merges

### During Testing

- [ ] Test with example/non-sensitive data only
- [ ] Verify all authentication flows work correctly
- [ ] Load test to establish baseline latencies (see README.md benchmarks)
- [ ] Penetration test gRPC channels for vulnerabilities

### During Deployment

- [ ] Run security scans on Docker images before pushing to registry:
  ```bash
  docker scan nexus-api-gateway
  docker scan nexus-ingestion-worker
  docker scan nexus-client
  ```
- [ ] Use container signing (Docker Content Trust) in production
- [ ] Implement admission controllers in Kubernetes (Pod Security Policies, OPA)
- [ ] Enable audit logging on all infrastructure (AWS CloudTrail, GCP Audit Logs, etc.)

### Production Checklist

- [ ] Authentication enabled (OAuth 2.0 / JWT)
- [ ] gRPC channels secured with TLS 1.3
- [ ] Pinecone network restrictions active
- [ ] Redis encryption enabled and restricted
- [ ] Rate limiting implemented
- [ ] CORS restricted to trusted domains
- [ ] Secrets stored in external manager (no .env files)
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery plan documented
- [ ] Incident response procedure established

---

## Dependency Vulnerabilities

Nexus Copilot depends on several open-source packages. Security updates are available as follows:

### Python Backend

- **FastAPI:** Check for updates monthly — [FastAPI Security](https://fastapi.tiangolo.com/)
- **LangChain:** Check for updates monthly — [LangChain GitHub](https://github.com/langchain-ai/langchain/security/advisories)
- **Pinecone SDK:** Check for updates monthly — [Pinecone GitHub](https://github.com/pinecone-io/pinecone-python)
- **Sentence Transformers:** Check for updates monthly — [Hugging Face Hub](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **gRPC Python:** Check for updates monthly — [gRPC GitHub](https://github.com/grpc/grpc/security/advisories)

**To update Python dependencies:**
```bash
cd api-gateway && pip install --upgrade -r requirements.txt
cd ../ingestion-worker && pip install --upgrade -r requirements.txt
```

### Frontend (Node.js)

- **Next.js:** Check for updates monthly — [Next.js Security](https://github.com/vercel/next.js/security)
- **React:** Updates included via Next.js
- **TypeScript:** Check for updates monthly

**To update frontend dependencies:**
```bash
cd client && npm audit fix && npm update
```

### Docker Base Images

- **Python 3.11:** Security updates released monthly by Docker
- **Node.js 18+:** Security updates released monthly by Docker

**To check for updates:**
```bash
docker pull python:3.11-slim
docker pull node:18-alpine
docker-compose build --no-cache  # Rebuild with latest base images
```

---

## Known Limitations

1. **No built-in authentication:** Designed for internal networks; OAuth/JWT required for external use
2. **Plain-text gRPC:** Suitable for Docker Compose local networks only; TLS required for production
3. **Redis without ACL:** Default open; network isolation assumed; ACL must be enabled in production
4. **No audit logging:** Queries and uploads not logged by default; implement in production
5. **Single-instance architecture:** No built-in high availability; Kubernetes recommended for production

---

## Security Contacts

- **Security Email:** sambitmondal2005@gmail.com
- **Expected Response Time:** Within 48 hours
- **GitHub Issues:** Do NOT use for security vulnerabilities

---

## Security Advisories

All security advisories are published on [GitHub Security Advisories](https://github.com/Sambit-Mondal/Nexus-Copilot/security/advisories) after patches are released.

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [gRPC Security](https://grpc.io/docs/guides/security/)
- [Pinecone Security](https://docs.pinecone.io/guides/security/)

---

**Last Updated:** May 2026  
**Version:** 1.0.0
