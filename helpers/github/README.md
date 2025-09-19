# GitHub Actions Deployment Templates

This directory contains GitHub Actions workflow templates for automated deployment of Streamlit applications to Snowflake Container Services (SPCS).

## Available Templates

### 1. `deploy-spcs.yml`
Complete SPCS deployment workflow with:
- Docker image building
- Snowflake authentication
- Container service deployment
- Automatic rollback on failure

### 2. `build-only.yml`
Build and push Docker images without deployment:
- Useful for development/testing
- Creates images in Snowflake registry
- Can be triggered manually or on PR

### 3. `deploy-staging.yml`
Staging environment deployment:
- Deploys to separate staging service
- Reduced resource allocation
- Testing-focused configuration

## Quick Start

1. Copy the appropriate template to `.github/workflows/` in your project
2. Update the environment variables section
3. Add required secrets to your GitHub repository
4. Customize service configuration as needed

## Required GitHub Secrets

All templates require these secrets to be configured in your repository:

```
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PRIVATE_KEY=your_private_key_content
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
SNOWFLAKE_WAREHOUSE=your_warehouse
```

Additional optional secrets used by some templates:

```
APP_USER_PASSWORD=strong-password-for-app-user
```

## Configuration Notes

- Service names are auto-generated based on repository name
- Resource allocation can be customized per environment
- All deployments use private key authentication for security
- Workflows include automatic cleanup on failure

### Container Registry Login
- Workflows use the Snowflake registry returned by `SYSTEM$REGISTRY_HOSTNAME()`
- Docker authenticates to the Snowflake registry via `docker login` using the Snowflake user and the private key provided in secrets
- Ensure the Snowflake user has rights to the image repository in APPS_DB.AI_APPS

## Troubleshooting

Common issues and solutions:

### Authentication Failures
- Verify private key format (PEM, no password)
- Check account identifier format
- Ensure user has required privileges

### Image Build Failures
- Check Dockerfile syntax
- Verify all requirements are installable
- Ensure base image compatibility

### Deployment Failures
- Verify compute pool exists
- Check service resource limits
- Review container service logs in Snowflake
	- `SELECT SYSTEM$GET_SERVICE_LOGS('<service_name>', 0, '<container_name>');`
	- Check `SHOW SERVICES LIKE '<service_name>'` for status

## Customization

Templates are designed to be modified:
- Adjust resource allocation in `spec` section
- Add environment-specific variables
- Modify trigger conditions
- Add additional deployment steps

For detailed customization guide, see the main INSTRUCTIONS.md file.