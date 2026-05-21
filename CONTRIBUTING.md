# Contributing to Nexus Copilot

First off, thank you for considering a contribution to **Nexus Copilot**! Whether you're fixing bugs, adding features, improving documentation, or enhancing our architecture, your effort helps make this enterprise advisory platform better for everyone. We genuinely appreciate your interest and look forward to collaborating with you. 🙏

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to sambitmondal2005@gmail.com.

---

## Development Environment Setup

### Prerequisites

Before you start contributing, ensure you have:

- **Git** (v2.25+)
- **Docker & Docker Compose** (v20.10+)
- **Python 3.11+** (for local backend development)
- **Node.js 18+** (for frontend development)
- **gRPC Tools** (for Protocol Buffer compilation)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Sambit-Mondal/Nexus-Copilot.git
cd Nexus-Copilot
```

#### 2. Install gRPC Tools (Critical for Proto Changes)

The `grpc_tools.protoc` compiler is required if you modify any `.proto` files in the `/protocol` directory.

**For all platforms:**
```bash
pip install grpcio-tools
```

**Verify installation:**
```bash
python -m grpc_tools.protoc --version
```

If you're using a virtual environment, activate it first:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install grpcio-tools
```

#### 3. Set Up Environment File

Create a `.env` file in the repository root with your development API keys:

```bash
# Copy the example
cp .env.example .env

# Edit and add your keys
nano .env
```

Required variables:
- `PINECONE_API_KEY` — Your Pinecone vector database API key
- `GROQ_API_KEY` — Your Groq LLM API key
- `HF_TOKEN` — (Optional) HuggingFace token for gated models

#### 4. Build Docker Images

```bash
# Build all services
docker-compose build

# Verify images were built
docker images | grep nexus
```

#### 5. Start Services

```bash
# Start all services in background
docker-compose up -d

# Check service health
docker-compose ps
curl http://localhost:8000/health
```

#### 6. Verify Local Development Setup

```bash
# Check all services are running
docker-compose logs -f

# Access the frontend
open http://localhost:3000

# View API documentation
open http://localhost:8000/docs
```

---

## Monorepo Guidelines

Nexus Copilot is organized as a **polyglot microservices monorepo** with clear ownership boundaries. Understanding the directory structure is critical for contributing effectively.

### Directory Map

```
nexus-copilot/
│
├── /client                    # ← FRONTEND (Next.js, TypeScript, Tailwind)
│   └── Changes here require:
│       • Updated UI/UX screenshots in PR
│       • Updated types.ts if API contracts change
│       • npm build verification
│
├── /api-gateway               # ← ORCHESTRATION & ROUTING (FastAPI, Python)
│   └── Changes here require:
│       • Updated API documentation (README.md)
│       • Updated models.py if request/response schemas change
│       • pytest unit tests for new routes
│       • Backward compatibility check for existing endpoints
│
├── /ingestion-worker          # ← ML & VECTORIZATION (gRPC, Python)
│   └── Changes here require:
│       • Updated embedding dimensions if model changes
│       • Tests for document processing pipeline
│       • Performance benchmarks for new chunking strategies
│       • Updated proto files if gRPC service signature changes
│
└── /protocol                  # ← gRPC CONTRACTS (Protocol Buffers)
    └── Changes here require:
        • Recompilation via `make all` in /protocol
        • Major version bump if breaking changes
        • Updated API documentation
```

### Where to Make Changes

| Contribution Type | Where | Key Files |
|---|---|---|
| **Frontend UI/UX** | `/client/app/` | `ChatInterface.tsx`, `DocumentUpload.tsx`, `globals.css` |
| **API Endpoints** | `/api-gateway/app/` | `query_route.py`, `upload_route.py`, `models.py` |
| **Document Processing** | `/ingestion-worker/app/` | `document_processor.py`, `embedding.py`, `service.py` |
| **gRPC Service Contract** | `/protocol/` | `document_service.proto` (then regenerate code) |
| **Configuration** | Root or service `.env` | `.env`, `docker-compose.yml` |
| **Documentation** | Root or inline | `README.md`, `SECURITY.md`, docstrings |

### Important: Cross-Service Changes

If your contribution touches **multiple services**, follow this workflow:

1. **Update the contract first** — If modifying gRPC, update `/protocol/document_service.proto`
2. **Regenerate code** — Run `cd /protocol && make all`
3. **Update consumers** — Update `/api-gateway` and `/ingestion-worker` to use new proto messages
4. **Test end-to-end** — Ensure all Docker containers build and services communicate
5. **Update documentation** — Reflect contract changes in API docs

**Example:** Adding a new field to the document processing message:
```protobuf
// In /protocol/document_service.proto
message Document {
  string id = 1;
  string filename = 2;
  bytes content = 3;
  string metadata = 4;  // ← NEW FIELD
}
```

Then:
```bash
cd /protocol && make all  # Regenerates document_pb2.py in both services
```

---

## Pull Request Process

### Step 1: Fork & Branch

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/Nexus-Copilot.git
cd Nexus-Copilot

# Add upstream remote for sync
git remote add upstream https://github.com/Sambit-Mondal/Nexus-Copilot.git

# Create feature branch from latest main
git fetch upstream main
git checkout -b feature/your-feature-name
```

### Step 2: Make Changes

Implement your changes following the **Monorepo Guidelines** above. Ensure:

- [ ] Your changes are in the correct directory (`/client`, `/api-gateway`, `/ingestion-worker`, or `/protocol`)
- [ ] You've updated relevant configuration files (`.env.example`, `docker-compose.yml`, etc.)
- [ ] Docstrings/comments are clear and concise
- [ ] No API keys or secrets are committed

### Step 3: Test Locally

**Before submitting your PR, all Docker containers must build and run successfully.**

```bash
# Clean up old images (optional)
docker-compose down
docker system prune -f

# Rebuild all services
docker-compose build --no-cache

# Verify containers start
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View logs for errors
docker-compose logs
```

**For protocol changes:**
```bash
# Recompile protobuf
cd protocol
make clean && make all
cd ..

# Rebuild worker to include new proto bindings
docker-compose build --no-cache ingestion-worker

# Test gRPC connectivity
docker-compose logs ingestion-worker | grep "listening"
```

**For API changes:**
```bash
# Verify Swagger docs render correctly
open http://localhost:8000/docs
```

**For frontend changes:**
```bash
# Check UI loads without errors
open http://localhost:3000
# Check browser console for warnings/errors
```

### Step 4: Update Documentation

If your changes affect:

- **API Contract** → Update `README.md` API Reference section
- **gRPC Service** → Update proto comments and regenerate docs
- **Architecture** → Update `ARCHITECTURE.md` or create new section
- **Configuration** → Update `.env.example` with new variables
- **Setup Process** → Update `README.md` Local Setup section

### Step 5: Commit & Push

Follow the **Commit Message Convention** (see below), then push:

```bash
# Stage changes
git add .

# Commit with proper message (see convention)
git commit -m "feat(api-gateway): add user-specific query caching"

# Push to your fork
git push origin feature/your-feature-name
```

### Step 6: Open Pull Request

1. Go to [Nexus-Copilot](https://github.com/Sambit-Mondal/Nexus-Copilot)
2. Click **"New Pull Request"**
3. Select your fork and feature branch
4. **Fill out the PR template:**

```markdown
## Description
Brief explanation of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update
- [ ] Infrastructure/DevOps

## Changes Made
- Bullet point summary of changes
- Include affected files/services

## Testing
- [ ] Local Docker build successful
- [ ] All services healthy (docker-compose ps)
- [ ] Feature tested manually
- [ ] No secrets committed
- [ ] Documentation updated

## Related Issues
Closes #(issue number)

## Screenshots (if UI change)
Add screenshots for frontend changes.
```

### Step 7: Code Review

- Respond to reviewer comments promptly
- Don't push `--force` to your feature branch during review
- Resolve merge conflicts with `main` before merging
- Ensure all CI checks pass (when available)

### Step 8: Merge

Maintainers will merge your PR once:
- ✅ Code review approved
- ✅ All tests pass
- ✅ CI/CD pipeline succeeds
- ✅ No merge conflicts with `main`

---

## Commit Message Convention

We follow **Conventional Commits** for clear, semantic commit history. This enables automated changelog generation and better project tracking.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

| Type | Scope | Example |
|------|-------|---------|
| `feat` | Feature | `feat(api-gateway): add semantic caching layer` |
| `fix` | Bug fix | `fix(client): resolve streaming response display bug` |
| `docs` | Documentation | `docs: update setup instructions for gRPC tools` |
| `style` | Formatting | `style(ingestion-worker): format code with black` |
| `refactor` | Code refactor | `refactor(protocol): simplify document message schema` |
| `perf` | Performance | `perf(api-gateway): optimize pinecone query latency` |
| `test` | Tests | `test(client): add ChatInterface unit tests` |
| `chore` | Build/CI | `chore: update python dependencies` |

### Scope

Pick the affected service:
- `client` — Frontend (Next.js)
- `api-gateway` — API orchestration (FastAPI)
- `ingestion-worker` — Document processing (gRPC)
- `protocol` — gRPC contracts
- (blank) — Multiple or repository-wide changes

### Examples

#### Good ✅
```
feat(api-gateway): add per-user query rate limiting with Redis counter

- Implement sliding window rate limit algorithm
- Add RateLimitExceeded exception
- Update API documentation with 429 status code
- Add unit tests for edge cases

Closes #42
```

```
fix(client): prevent response text from disappearing after streaming completes

- Capture finalResponse before async state update
- Add unit test for response persistence
- Refactor ChatInterface state management

Fixes #38
```

```
docs: update CONTRIBUTING.md with gRPC protoc compiler requirements

- Add grpc_tools installation steps
- Include verification command
- Add recompilation workflow for proto changes
```

```
chore(ingestion-worker): upgrade sentence-transformers to 2.2.2

- Update requirements.txt
- No breaking changes in embedding output
- All tests pass
```

#### Bad ❌
```
fixed bugs
```

```
wip: frontend stuff
```

```
Updated some files
```

### Commit Best Practices

- **Atomic commits** — One logical change per commit (don't mix features and fixes)
- **Small commits** — Easier to review and revert if needed
- **Tested commits** — Each commit should leave the repo in a working state
- **Descriptive subjects** — Use imperative mood: "add feature" not "added feature"
- **No secrets** — Never commit API keys, tokens, or `.env` files

---

## Testing

### Backend (Python)

```bash
# Run API gateway tests
cd api-gateway
pytest tests/ -v --cov=app

# Run ingestion worker tests
cd ../ingestion-worker
pytest tests/ -v --cov=app
```

### Frontend (TypeScript/React)

```bash
cd client
npm test -- --coverage
```

### Integration Testing

```bash
# All Docker containers running locally
docker-compose up -d

# Run end-to-end tests
npm run test:e2e  # (if available)

# Manual verification
curl http://localhost:8000/health
open http://localhost:3000
```

---

## Code Review Checklist

When reviewing PRs, maintainers look for:

- ✅ Follows **Conventional Commits** format
- ✅ Correct directory per **Monorepo Guidelines**
- ✅ **Docker builds successfully** locally
- ✅ **All services healthy** after changes (`docker-compose ps`)
- ✅ No secrets committed (check `.env`, API keys)
- ✅ Documentation updated (README, docstrings, `.proto` comments)
- ✅ Breaking changes documented clearly
- ✅ Tests included or updated for new functionality
- ✅ Performance impact considered (especially for API/embeddings)
- ✅ Cross-service changes properly coordinated

---

## Getting Help

- **Questions?** Open a GitHub Discussion
- **Need help setting up?** Email sambitmondal2005@gmail.com
- **Bug report?** See [SECURITY.md](./SECURITY.md) for security issues; otherwise open an issue
- **Documentation unclear?** Edit and submit a PR!

---

## Recognition

Contributors are recognized in:
- Pull request history on GitHub
- CHANGELOG (when available)
- Project documentation

We value all contributions, whether code, documentation, bug reports, or feature requests. Thank you for making Nexus Copilot better! 🚀

---

## Quick Links

- [README.md](./README.md) — Getting started & architecture
- [SECURITY.md](./SECURITY.md) — Security policy & production requirements
- [Code of Conduct](./CODE_OF_CONDUCT.md) — Community standards
- [GitHub Issues](https://github.com/Sambit-Mondal/Nexus-Copilot/issues) — Bug reports & features
- [GitHub Discussions](https://github.com/Sambit-Mondal/Nexus-Copilot/discussions) — Questions & ideas

---

**Happy coding! We look forward to your contributions.** 💚
