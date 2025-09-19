# 🛠️ SPCS Troubleshooting Utilities

This directory contains comprehensive troubleshooting and diagnostic tools for Snowflake Container Services (SPCS) deployments.

## 📁 Available Tools

### 1. troubleshoot.py - Comprehensive Diagnosis Tool
**Purpose**: Complete system health check and diagnosis for SPCS deployments

**Usage**:
```bash
# Full comprehensive diagnosis
python3 troubleshoot.py

# Quick health check only  
python3 troubleshoot.py --quick

# Diagnose specific app
python3 troubleshoot.py --app forms_review

# JSON output for automation
python3 troubleshoot.py --json
```

**Features**:
- ✅ Snowflake CLI availability check
- ✅ Connection testing and authentication validation
- ✅ SPCS prerequisites verification (compute pools, image repositories)
- ✅ App-specific deployment status
- ✅ Service health monitoring
- ✅ Permission analysis
- ✅ GitHub Actions setup validation
- ✅ Detailed recommendations and next steps

### 2. log-monitor.sh - Live Log Monitoring
**Purpose**: Real-time log monitoring, analysis, and troubleshooting for SPCS services

**Usage**:
```bash
# Monitor live logs
./log-monitor.sh monitor forms_review

# Show recent logs (last 100 lines)
./log-monitor.sh recent forms_review

# Show only errors from last 24 hours
./log-monitor.sh errors forms_review

# Search logs for specific pattern
./log-monitor.sh search forms_review "authentication"

# Analyze log patterns and health
./log-monitor.sh analyze forms_review

# Export logs to file
./log-monitor.sh export forms_review

# List all available services
./log-monitor.sh list
```

**Features**:
- 📊 Live log streaming with auto-refresh
- 🔍 Pattern-based log searching
- ⚠️ Error detection and filtering
- 📈 Log pattern analysis and health assessment
- 💾 Log export for further analysis
- 🧹 Automatic cleanup of old exports

### 3. spcs-setup.sh - Interactive SPCS Setup
**Purpose**: One-time interactive setup for SPCS infrastructure

**Features**:
- 🎯 Interactive menu-driven setup
- ✅ Prerequisite validation
- 🏗️ Compute pool creation
- 📦 Image repository setup
- 👤 Role and permission configuration
- 🔧 Environment validation

### 4. permissions.sql - Role-Based Access Control
**Purpose**: Complete RBAC setup with procedures for app management

**Features**:
- 👥 APP_DEVELOPER, APP_SERVICE, APP_ADMIN roles
- 🔧 CREATE_APP_USER procedure
- ⚙️ SETUP_APP_PERMISSIONS procedure
- 🧹 CLEANUP_APP_RESOURCES procedure

## 🚀 Quick Start Troubleshooting

### For New Deployments:
```bash
# 1. Check overall system health
python3 troubleshoot.py --quick

# 2. If issues found, run comprehensive diagnosis
python3 troubleshoot.py --app your_app_name

# 3. Follow the recommended next steps
```

### For Running Services:
```bash
# 1. Check service logs
./log-monitor.sh recent your_app_name

# 2. Monitor for errors
./log-monitor.sh errors your_app_name

# 3. Live monitoring during debugging
./log-monitor.sh monitor your_app_name
```

### For Authentication Issues:
```bash
# 1. Test basic connection
python3 troubleshoot.py --quick

# 2. Check user permissions
./spcs-setup.sh --validate-permissions

# 3. Review setup documentation
cat ../../../INSTRUCTIONS.md
```

## 🔧 Common Issues and Solutions

### Issue: "Snowflake CLI not found"
**Solution**: Install Snowflake CLI
```bash
pip install snowflake-cli-labs
snow --version
```

### Issue: "Connection failed"
**Solution**: Check authentication setup
```bash
# Verify private key format
python3 troubleshoot.py --app your_app

# Check environment variables
echo $SNOWFLAKE_PRIVATE_KEY_PATH
echo $SNOWFLAKE_USER
```

### Issue: "No compute pools found"
**Solution**: Run SPCS setup
```bash
./spcs-setup.sh
# Choose option 2: "Create Compute Pool"
```

### Issue: "Service deployment failed"
**Solution**: Check service logs and permissions
```bash
./log-monitor.sh errors your_app_name
python3 troubleshoot.py --app your_app_name
```

## 📊 Log Analysis Examples

### Error Pattern Detection:
```bash
# Find authentication issues
./log-monitor.sh search your_app "authentication\|auth\|login"

# Find database connection issues  
./log-monitor.sh search your_app "connection\|database\|snowflake"

# Find permission issues
./log-monitor.sh search your_app "permission\|access\|denied"
```

### Health Monitoring:
```bash
# Get health summary
./log-monitor.sh analyze your_app_name

# Monitor service startup
./log-monitor.sh monitor your_app_name

# Export logs for external analysis
./log-monitor.sh export your_app_name --output app_logs.txt
```

## 🔍 Integration with CI/CD

### GitHub Actions Integration:
```yaml
- name: Health Check Before Deployment
  run: |
    python3 framework/helpers/snowflake/troubleshoot.py --quick --json > health.json
    
- name: Monitor Deployment Logs
  run: |
    framework/helpers/snowflake/log-monitor.sh recent ${{ env.APP_NAME }} --lines 50
```

### Tool Dependencies

**Required**:
- `snowflake-cli-labs` (pip package)
- `jq` (for JSON processing in log-monitor.sh)
- `curl` (for health checks)
- Python 3.8+ (for troubleshoot.py)
- Bash 4.0+ (for shell scripts)

**Install dependencies**:
```bash
# Python dependencies
pip install snowflake-cli-labs

# System dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install jq curl

# System dependencies (macOS)  
brew install jq
```