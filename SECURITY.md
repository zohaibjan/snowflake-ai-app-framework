# Security Policy

Use private key authentication for all production deployments
Never commit private keys to the repository; use GitHub Actions secrets
Rotate Snowflake user keys and passwords regularly
Limit roles: use APP_SERVICE for services, APP_DEVELOPER for CI, APP_ADMIN sparingly
Review compute pool permissions and service logs for anomalies

Report vulnerabilities by opening a private issue or contacting the maintainer.