# Azure deployment plan

## Proposed architecture
- **Compute:** Azure App Service (Linux, Python runtime) hosts the FastAPI API.
- **Storage:** For a real deployment, replace local SQLite with Azure Database for PostgreSQL or Azure SQL. SQLite is suitable for the local assessment demo but is not appropriate for a horizontally scaled App Service because its filesystem may be ephemeral and instances do not share a database.
- **Identity and secrets:** GitHub Actions authenticates to Azure using OpenID Connect (OIDC). Store `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` as GitHub Actions secrets; set `AZURE_WEBAPP_NAME` as a repository variable. Never commit credentials.
- **Monitoring:** Enable Application Insights and App Service logs. Avoid logging sensitive ticket content unnecessarily.
- **Deployment:** The manual `workflow_dispatch` workflow runs tests, authenticates using OIDC, and deploys the app. Configure a federated credential in Microsoft Entra ID for the repository/branch.
- **Cost control:** Start with the smallest suitable non-production App Service plan, set budget alerts, and stop/delete resources after evaluation if no longer needed.

## Configuration notes
Set the App Service startup command to:
`python -m uvicorn main:app --host 0.0.0.0 --port 8000`

This sample uses SQLite and a local file database to keep the assessment runnable without cloud credentials. Before production, use a managed database, authentication/authorization for approval actions, rate limiting, and secure handling/retention of customer data.
