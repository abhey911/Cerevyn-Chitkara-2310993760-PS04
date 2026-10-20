# Cerevyn PS04 — Azure Support Ticket Automation

A local, AI-assisted support-ticket prototype that categorizes tickets, proposes priority, assigns a team, summarizes the request, and prepares a draft response for human approval. It does **not** send email.

## Features
- FastAPI endpoints: health, create/list/get ticket, approve draft.
- SQLite persistence and duplicate ticket ID rejection.
- Categories: Billing, Technical, Access, General.
- Priority policy: High for urgent/critical/outage/production-down language; Medium for time-sensitive or blocked requests; otherwise Low.
- Low-confidence/ambiguous tickets are routed to `pending_review`.
- 30 fictional labelled examples; the final 10 are held out by `scripts/evaluate.py`.
- Pytest suite, Dockerfile, GitHub Actions CI and manual Azure deployment workflow.

## Important methodology note
This first-hour implementation uses a transparent keyword-rule baseline, not a trained ML model or an LLM. Confidence is a heuristic, not a calibrated probability. Reported accuracy on 10 synthetic examples is only a demonstration, not a reliable estimate of real-world performance. The next improvement would be to compare against a trained classifier or semantic model using a larger, representative labelled dataset.

## Run locally
Requires Python 3.11+ (CI uses Python 3.12).

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API.

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

## Example request
```bash
curl -X POST http://127.0.0.1:8000/tickets   -H "Content-Type: application/json"   -d '{"ticket_id":"T-100","message":"URGENT: production is down and all users are blocked"}'
```
Expected: HTTP 201, a category/team, `High` priority, draft reply, confidence heuristic and a pending review/approval status.

Approve a draft:
```bash
curl -X POST http://127.0.0.1:8000/tickets/T-100/approve
```
Approval only changes state; it does not send a message.

## Tests and evaluation
```bash
pytest -q
python scripts/evaluate.py
```
The evaluation script tests S021–S030 as a 10-example holdout. Keep this limitation in the report; do not tune the rules on the holdout and then claim it is unseen.

## Docker
```bash
docker build -t cerevyn-ps04 .
docker run --rm -p 8000:8000 cerevyn-ps04
```
Then open http://127.0.0.1:8000/docs.

## Repository structure
```text
.
├── main.py
├── requirements.txt
├── tests/test_main.py
├── sample_data/tickets.json
├── scripts/evaluate.py
├── Dockerfile
├── .github/workflows/ci.yml
├── .github/workflows/azure-deploy.yml
└── docs/azure-plan.md
```

## Azure deployment
See [`docs/azure-plan.md`](docs/azure-plan.md). Live deployment is optional for the assessment. The deployment workflow requires an App Service, a Microsoft Entra federated credential, and GitHub secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, plus repository variable `AZURE_WEBAPP_NAME`. Do not commit credentials. The workflow is a starting point and may need adjustment to match your App Service configuration.

## Assessment checklist
- [x] Four categories and documented priority policy
- [x] Duplicate ID and invalid input handling
- [x] Human approval endpoint; no real email sending
- [x] 30 labelled fictional sample tickets; 10 held out in evaluation script
- [x] At least five automated test scenarios
- [x] Dockerfile, CI workflow and Azure deployment plan
- [ ] Run tests locally and capture output
- [ ] Create GitHub repository and push
- [ ] Confirm CI passes and record commit hash
- [ ] Record a 3–5 minute demo

## Limitations
The rules are intentionally simple and can misclassify messages. Priority is based on explicit terms, not a learned service-level model. There is no authentication on approval endpoints in this prototype, so do not expose it publicly as-is. SQLite is for local demonstration only.
