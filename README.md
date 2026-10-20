# Cerevyn PS04 — Azure Support Ticket Automation

Cerevyn Chitkara University, Round One Technical Assessment - Problem Statement PS04.

- Candidate Name: [Insert candidate name]
- Roll Number: 2310993760
- Branch: main
- GitHub Repository: https://github.com/abhey911/Cerevyn-Chitkara-2310993760-PS04

## Table of Contents

- [1. Project Title and Assessment Details](#1-project-title-and-assessment-details)
- [2. Project Overview](#2-project-overview)
- [3. Objectives](#3-objectives)
- [4. Features](#4-features)
- [5. Technology Stack](#5-technology-stack)
- [6. System Architecture](#6-system-architecture)
- [7. Classification and Priority Policy](#7-classification-and-priority-policy)
- [8. Repository Structure](#8-repository-structure)
- [9. Prerequisites](#9-prerequisites)
- [10. Installation and Local Setup](#10-installation-and-local-setup)
- [11. API Documentation](#11-api-documentation)
- [12. Testing and Classification Evaluation](#12-testing-and-classification-evaluation)
- [13. Docker](#13-docker)
- [14. GitHub Actions and CI](#14-github-actions-and-ci)

## 1. Project Title and Assessment Details

This repository contains the implementation for the Cerevyn PS04 — Azure Support Ticket Automation assessment. It is designed as a prototype support-ticket automation service for the Cerevyn Chitkara University Round One Technical Assessment, Problem Statement PS04.

- Assessment: Cerevyn Chitkara University, Round One Technical Assessment
- Problem Statement: PS04
- Candidate Roll Number: 2310993760
- Repository: https://github.com/abhey911/Cerevyn-Chitkara-2310993760-PS04
- Candidate Name: [Insert candidate name]
- Current Branch: main

## 2. Project Overview

This project is an API-based support-ticket automation prototype that accepts customer messages, classifies each ticket into a category, proposes a priority, assigns a support team, creates a short summary, and generates a draft response for human review.

The implementation is built around a FastAPI service that stores ticket records in SQLite and exposes endpoints for creating, listing, fetching, and approving tickets. It does not send emails or automatically communicate with customers. Any draft response must be reviewed by a human before external communication is sent.

## 3. Objectives

The core goals implemented in this repository are:

- Ticket classification into one of the defined categories.
- Priority assignment using a small rule-based policy.
- Support-team assignment based on the category.
- Summary generation and draft-response creation.
- Human review for lower-confidence or uncertain classifications.
- Duplicate ticket prevention and input validation.
- Ticket persistence and approval workflow.
- Automated testing and Azure deployment planning.

Only the items above are claimed as implemented behavior based on the code in this repository.

## 4. Features

Implemented features in the current codebase include:

- FastAPI endpoints for health checks, ticket creation, listing, retrieval, and approval workflow.
- Rule-based ticket classification with categories: Billing, Technical, Access, and General.
- Priority assignment based on urgency-related keywords, fallback to Low when no urgent terms are found.
- Support-team routing by category.
- Short summary generation from the incoming ticket message.
- Draft-response generation for each category.
- SQLite persistence with duplicate ticket ID protection.
- Input validation using Pydantic field constraints.
- Human approval workflow whereby a ticket can be marked approved without sending any outside message.
- Automated pytest scenarios covering classification, duplicate rejection, invalid payloads, and approval behavior.
- Docker support through the repository Dockerfile.
- GitHub Actions workflows for CI and Azure deployment preparation.
- Azure deployment documentation in the project docs folder.

Note: deployment to Azure is planned and documented, not a verified live production deployment in this repository.

## 5. Technology Stack

| Technology | Purpose |
| --- | --- |
| Python 3.12 | Runtime version used by the project and CI workflow. |
| FastAPI | Web API framework for the ticket-processing service. |
| Pydantic | Request validation and schema enforcement for ticket payloads. |
| SQLite | Local ticket persistence for the prototype. |
| Uvicorn | ASGI server used to serve the FastAPI app. |
| Pytest | Automated test execution for API and classification behavior. |
| HTTPX | HTTP client library used for API testing. |
| Docker | Containerized execution for the service. |
| GitHub Actions | CI and manual Azure deployment workflow automation. |
| Azure App Service | Planned hosting target described in the Azure deployment documentation. |

The actual dependency list is kept in [requirements.txt](requirements.txt).

## 6. System Architecture

The application follows a simple processing flow:

Client request → FastAPI → Input validation → Classification and priority assignment → Team assignment → Summary and draft generation → Review status → SQLite storage → Human approval.

```mermaid
flowchart LR
    A[Client Request] --> B[FastAPI API]
    B --> C[Input Validation]
    C --> D[Rule-based Classification]
    D --> E[Priority Selection]
    E --> F[Team Assignment]
    F --> G[Summary + Draft Response]
    G --> H[Review Status]
    H --> I[SQLite Storage]
    I --> J[Human Approval]
```

This is not a multi-service architecture; it is a single FastAPI application with local data persistence and a review-based workflow. The repository is intentionally lightweight for an assessment prototype.

## 7. Classification and Priority Policy

The current implementation uses a transparent, rule-based classifier rather than a trained ML model or LLM. The exact logic lives in [main.py](main.py).

### Categories

The implemented categories are:

- Billing
- Technical
- Access
- General

### Team Assignment

| Category | Assigned Team |
| --- | --- |
| Billing | Billing Support |
| Access | Identity & Access Support |
| Technical | Technical Support |
| General | Customer Support |

### Priority Rules

The priority logic is straightforward and keyword-driven:

- If the message contains urgent terms such as `urgent`, `critical`, `outage`, `all users`, `security breach`, `cannot work`, or `production down`, the priority is set to `High`.
- If the message contains moderate urgency markers such as `today`, `blocked`, `deadline`, `lost access`, or `charged twice`, the priority is set to `Medium`.
- Otherwise, it defaults to `Low`.

### Confidence and Review Handling

The `classify()` function uses keyword counts to assign categories. Confidence values are heuristic values, not calibrated probabilities. The implementation currently does the following:

- If no category keywords match, the category is `General` and confidence is set to `0.35`.
- If multiple categories have matching words or the best category only has a single hit, confidence is set to `0.60`.
- Otherwise, confidence is set to `0.85`.

Tickets with confidence below `0.7` are assigned a `pending_review` status; otherwise, they are stored with `pending_approval` status. This is the current ambiguity-handling policy and is intentionally conservative.

### Honest limitation

This is a rule-based baseline. It is not a production-grade ML classifier, and it should not be described as an LLM-powered or trained model.

## 8. Repository Structure

The repository structure is as follows:

```text
.
├── .dockerignore
├── .github/
│   └── workflows/
│       ├── azure-deploy.yml
│       └── ci.yml
├── .gitignore
├── Dockerfile
├── README.md
├── docs/
│   └── azure-plan.md
├── main.py
├── requirements.txt
├── sample_data/
│   └── tickets.json
├── scripts/
│   └── evaluate.py
├── tests/
│   └── test_main.py
└── .venv/
```

The project is intentionally compact and focused on the assessment workflow.

## 9. Prerequisites

Before running the service locally, ensure the following are available:

- Python 3.12
- `pip` for dependency installation
- A virtual environment tool such as `venv`
- A local terminal or IDE with shell access

The project does not require cloud credentials for local execution. Azure credentials are only needed for the GitHub Actions deployment workflow described in the deployment plan.

## 10. Installation and Local Setup

### Windows PowerShell

```powershell
git clone https://github.com/abhey911/Cerevyn-Chitkara-2310993760-PS04.git
cd Cerevyn-Chitkara-2310993760-PS04
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### macOS/Linux

```bash
git clone https://github.com/abhey911/Cerevyn-Chitkara-2310993760-PS04.git
cd Cerevyn-Chitkara-2310993760-PS04
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Local URLs

Once the server is running:

- API root: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs

## 11. API Documentation

The application exposes the following endpoints.

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Returns basic service metadata and links to the docs and health endpoint. |
| `/health` | GET | Returns the application health status. |
| `/tickets` | POST | Creates a new ticket using a `ticket_id` and message. |
| `/tickets` | GET | Lists all stored tickets in descending creation order. |
| `/tickets/{ticket_id}` | GET | Fetches one stored ticket by ID. |
| `/tickets/{ticket_id}/approve` | POST | Marks a ticket as approved and returns confirmation. |

### Example Create Ticket Request

```json
{
  "ticket_id": "T-101",
  "message": "I cannot log in to my account after resetting my password"
}
```

Example response behavior:

- It classifies the ticket using the keyword rules.
- It assigns a team based on the detected category.
- It proposes a priority based on urgency keywords.
- It stores the record in SQLite.
- It returns a response payload containing the generated category, priority, summary, draft response, confidence, and status.

The exact response depends on the message content, but the response model includes the following keys:

- `ticket_id`
- `category`
- `priority`
- `assigned_team`
- `summary`
- `draft_response`
- `confidence`
- `status`
- `created_at`

### Approval Endpoint

The approval endpoint does the following:

```http
POST /tickets/{ticket_id}/approve
```

This marks the ticket as `approved` in the local database. It does not send email, notification, or external communication. The implementation explicitly returns a message stating that no email was sent.

### HTTP Errors Supported by the Current API

The API currently supports the following relevant error scenarios:

- `422 Unprocessable Entity` for invalid request payloads, such as an empty ticket ID or too-short message.
- `409 Conflict` when a duplicate `ticket_id` is submitted.
- `404 Not Found` when a requested ticket ID does not exist.

## 12. Testing and Classification Evaluation

### Running the Tests

```bash
pytest -q
```

The repository contains automated tests in [tests/test_main.py](tests/test_main.py). They cover:

- health check response
- billing category classification
- urgent ticket priority assignment
- duplicate ticket rejection
- invalid input validation
- approval workflow
- ambiguous ticket handling
- missing ticket retrieval

### Evaluation Script

The repository includes an evaluation script at [scripts/evaluate.py](scripts/evaluate.py).

```bash
python scripts/evaluate.py
```

This script reads the labelled sample tickets in [sample_data/tickets.json](sample_data/tickets.json), reserves the last ten entries as a holdout set, and prints the resulting accuracy. The script also prints a note stating that this is a small synthetic dataset and is not evidence of production performance.

### Sample Data Layout

The sample data file contains 30 labelled fictional tickets in four categories:

- Billing
- Access
- Technical
- General

The script intentionally keeps the last 10 examples out of the main evaluation logic by selecting `data[20:]` as the holdout set. This is a compact assessment dataset, not a broad or production-quality benchmark.

### Accuracy Reporting

Accuracy is reported by the evaluation script only when it is run. This repository does not claim a production-grade performance result. The script itself warns that the dataset is small and synthetic.

## 13. Docker

The repository contains a [Dockerfile](Dockerfile) that installs dependencies and runs the FastAPI app with Uvicorn.

### Build the Container

```bash
docker build -t cerevyn-ps04 .
```

### Run the Container

```bash
docker run --rm -p 8000:8000 cerevyn-ps04
```

The service is exposed on port `8000` and can be reached at:

- http://localhost:8000/
- http://localhost:8000/health
- http://localhost:8000/docs

## 14. GitHub Actions and CI

The repository includes a CI workflow in [.github/workflows/ci.yml](.github/workflows/ci.yml) and an Azure deployment workflow in [.github/workflows/azure-deploy.yml](.github/workflows/azure-deploy.yml).

### CI Workflow

The `CI` workflow triggers on:

- push
- pull_request

It performs the following steps:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs dependencies from [requirements.txt](requirements.txt).
4. Runs `pytest -q`.
5. Runs `python scripts/evaluate.py`.

This workflow is defined in the repository, but the actual GitHub Actions run result must be verified manually in the GitHub Actions tab.

### Azure Deployment Workflow

The deployment workflow is a `workflow_dispatch` manual trigger and uses OIDC for Azure authentication. It includes:

- `permissions: id-token: write`
- Azure login through `azure/login@v2`
- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` from GitHub secrets
- `AZURE_WEBAPP_NAME` from GitHub variables
- deployment via `azure/webapps-deploy@v3`

The workflow file does not prove a successful Azure deployment; it only defines the deployment mechanism described in the plan.

