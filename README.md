# Snowflake AI App Framework

Reusable Streamlit and Snowflake Cortex application templates, document processing components, Docker packaging and Snowpark Container Services (SPCS) deployment examples.

## What to explore

| Path | Purpose |
|---|---|
| `apps/app-template/` | Starting app with UI components, environment example and setup script |
| `templates/components/` | Sidebar, upload and feedback components |
| `templates/utils/` | Snowflake connection, staging, document processing and AI helpers |
| `helpers/scaffold_app.py` | App-scaffolding helper |
| `helpers/docker/` | Alternative container examples |
| `helpers/snowflake/` | Account setup, permissions and troubleshooting examples |
| `helpers/github/`, `templates/deployment/` | Deployment templates for adaptation |

These are templates and examples, not a configured service or a claim of validated production readiness. Some helper paths and instructions describe a larger parent-project layout; inspect them before use.

## Start locally

From the repository root, copy the complete starter into a new app directory:

```bash
cp -r apps/app-template apps/my-ai-app
cd apps/my-ai-app
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Replace the starter's app-name placeholders and configure your own Snowflake account, database, roles and authentication. Review its [setup guide](apps/app-template/README.md) before running `streamlit run app.py`. Windows users should use the equivalent virtual-environment activation and copy commands.

No configured account, provider key, private key or production dataset is included. Keep real configuration outside version control. The app-template setup script provisions no default password; configure key-pair authentication separately.

## Deployment boundary

YAML files under `helpers/` and `templates/` are examples. This repository has no active GitHub Actions deployment workflow. Nothing deploys merely because this code is public or a commit is pushed.

The SQL and shell setup examples can create cloud objects and incur charges when run against your account. Adapt object names, permissions, compute pools, image repositories and secrets to your environment before running them. The deployment helpers have not been executed against a live Snowflake account during this review.

## Development

Read [INSTRUCTIONS.md](INSTRUCTIONS.md) and [AGENTS.md](AGENTS.md) for the original implementation patterns. Use the actual repository paths above if those historical instructions assume a parent `framework/` folder. Preserve established component interfaces and test with synthetic documents.

The public source received Python syntax and shell syntax checks. These checks do not validate Snowflake permissions, SQL execution, model access, image builds or end-to-end app behaviour.

See [SECURITY.md](SECURITY.md) for security reporting and [SUPPORT.md](SUPPORT.md) for support scope.
