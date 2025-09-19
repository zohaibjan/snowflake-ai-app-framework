# Docker Configuration Templates

This directory contains Docker templates and configurations for containerizing Streamlit applications for Snowflake Container Services deployment.

## Available Templates

### 1. `Dockerfile.streamlit`
Optimized Dockerfile for Streamlit applications:
- Python 3.11 slim base
- Efficient layer caching
- Security best practices
- SPCS-compatible configuration

### 2. `Dockerfile.heavy`
Dockerfile for applications with heavy dependencies:
- Includes data science libraries
- PDF processing capabilities
- ML libraries (scikit-learn, etc.)
- Extended build time optimization

### 3. `Dockerfile.minimal`
Minimal Dockerfile for simple applications:
- Smallest possible image size
- Basic Python + Streamlit only
- Fast build and deployment

### 4. `.dockerignore`
Optimized Docker ignore file:
- Excludes development files
- Reduces build context size
- Improves build performance

## Quick Start

1. Copy the appropriate Dockerfile template to your project root
2. Rename it to `Dockerfile`
3. Customize the configuration as needed
4. Build and test locally before deployment

## Template Selection Guide

### Use `Dockerfile.streamlit` (Recommended) when:
- Building standard Streamlit applications
- Need balance of features and image size
- Working with Snowflake integration
- Want reliable, tested configuration

### Use `Dockerfile.heavy` when:
- Your app processes PDFs or documents
- Need machine learning libraries
- Require data science packages
- Build time is not critical

### Use `Dockerfile.minimal` when:
- Building simple, lightweight apps
- Minimizing resource usage
- Fast deployment is priority
- Limited functionality requirements

## Customization Guidelines

### Environment Variables
Add environment variables for configuration:
```dockerfile
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_ENABLE_CORS=false
```

### Dependencies
Modify requirements.txt installation:
- Pin specific versions for production
- Use `--no-cache-dir` to reduce image size
- Consider multi-stage builds for complex dependencies

### Security
Follow security best practices:
- Use non-root user
- Minimize attack surface
- Scan for vulnerabilities

## Testing Locally

Before deploying to SPCS, test your container locally:

```bash
# Build the image
docker build -t my-app .

# Run locally
docker run -p 8501:8501 my-app

# Test the application
curl http://localhost:8501
```

## Troubleshooting

### Common Issues

#### Build Failures
- Check requirements.txt syntax
- Verify base image availability
- Review dependency conflicts

#### Runtime Issues
- Check port configuration (must be 8501)
- Verify file permissions
- Review environment variables

#### Size Optimization
- Use multi-stage builds
- Minimize installed packages
- Clean up caches and temporary files

## SPCS Requirements

All templates are configured for SPCS compatibility:
- Port 8501 exposed and used
- Non-interactive mode
- Proper signal handling
- Health check support

## Best Practices

1. **Layer Optimization**: Order commands by change frequency
2. **Caching**: Copy requirements.txt before source code
3. **Security**: Run as non-root user when possible
4. **Size**: Use .dockerignore to exclude unnecessary files
5. **Testing**: Always test locally before deployment

For detailed deployment instructions, see the GitHub Actions templates in `../github/`.