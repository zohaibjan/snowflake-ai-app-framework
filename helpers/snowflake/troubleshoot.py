#!/usr/bin/env python3
"""
Snowflake SPCS Deployment Troubleshooting Tool

This script helps diagnose and troubleshoot SPCS deployment issues,
connectivity problems, and permission errors.
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

    @classmethod
    def red(cls, text): return f"{cls.RED}{text}{cls.ENDC}"
    @classmethod
    def green(cls, text): return f"{cls.GREEN}{text}{cls.ENDC}"
    @classmethod
    def yellow(cls, text): return f"{cls.YELLOW}{text}{cls.ENDC}"
    @classmethod
    def blue(cls, text): return f"{cls.BLUE}{text}{cls.ENDC}"
    @classmethod
    def purple(cls, text): return f"{cls.PURPLE}{text}{cls.ENDC}"
    @classmethod
    def cyan(cls, text): return f"{cls.CYAN}{text}{cls.ENDC}"
    @classmethod
    def bold(cls, text): return f"{cls.BOLD}{text}{cls.ENDC}"

class SnowflakeTroubleshooter:
    """Main troubleshooting class for Snowflake SPCS deployments"""
    
    def __init__(self, app_name: Optional[str] = None):
        self.app_name = app_name
        self.connection_working = False
        
    def run_sql(self, query: str, format_output: str = "json") -> Tuple[bool, any]:
        """Execute Snowflake SQL command and return results"""
        try:
            cmd = ["snow", "sql", "-q", query]
            if format_output:
                cmd.extend(["--format", format_output])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                if format_output == "json" and result.stdout.strip():
                    try:
                        return True, json.loads(result.stdout)
                    except json.JSONDecodeError:
                        return True, result.stdout
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Query timeout after 60 seconds"
        except Exception as e:
            return False, str(e)
    
    def check_snowflake_cli(self) -> bool:
        """Check if Snowflake CLI is available and working"""
        print(Colors.blue("🔍 Checking Snowflake CLI availability..."))
        
        try:
            result = subprocess.run(["snow", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(Colors.green(f"✅ Snowflake CLI found: {version}"))
                return True
            else:
                print(Colors.red("❌ Snowflake CLI not working properly"))
                return False
        except FileNotFoundError:
            print(Colors.red("❌ Snowflake CLI not found. Please install snowflake-cli-labs"))
            return False
        except Exception as e:
            print(Colors.red(f"❌ Error checking Snowflake CLI: {e}"))
            return False
    
    def test_connection(self) -> bool:
        """Test basic Snowflake connection"""
        print(Colors.blue("🔗 Testing Snowflake connection..."))
        
        success, result = self.run_sql("SELECT CURRENT_VERSION(), CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE();")
        
        if success and result:
            if isinstance(result, list) and len(result) > 0:
                info = result[0]
                print(Colors.green("✅ Connected to Snowflake successfully"))
                print(f"   Account: {Colors.cyan(info.get('CURRENT_ACCOUNT()', 'Unknown'))}")
                print(f"   User: {Colors.cyan(info.get('CURRENT_USER()', 'Unknown'))}")
                print(f"   Role: {Colors.cyan(info.get('CURRENT_ROLE()', 'Unknown'))}")
                print(f"   Version: {Colors.cyan(info.get('CURRENT_VERSION()', 'Unknown'))}")
                self.connection_working = True
                return True
            else:
                print(Colors.green("✅ Connection successful"))
                self.connection_working = True
                return True
        else:
            print(Colors.red("❌ Connection failed"))
            print(Colors.red(f"   Error: {result}"))
            return False
    
    def check_spcs_prerequisites(self) -> Dict[str, any]:
        """Check SPCS prerequisites and permissions"""
        print(Colors.blue("🏗️ Checking SPCS prerequisites..."))
        
        results = {
            "compute_pools": [],
            "image_repositories": [],
            "permissions": {},
            "issues": []
        }
        
        if not self.connection_working:
            results["issues"].append("No active Snowflake connection")
            return results
        
        # Check compute pools
        success, pools = self.run_sql("SHOW COMPUTE POOLS;")
        if success and pools:
            results["compute_pools"] = pools if isinstance(pools, list) else []
            print(Colors.green(f"✅ Found {len(results['compute_pools'])} compute pools"))
            
            for pool in results["compute_pools"]:
                name = pool.get("name", "Unknown")
                state = pool.get("state", "Unknown")
                if state.upper() not in ["IDLE", "ACTIVE"]:
                    results["issues"].append(f"Compute pool {name} in state: {state}")
        else:
            print(Colors.yellow("⚠️ Could not retrieve compute pools"))
            results["issues"].append("Cannot access compute pools")
        
        # Check image repositories
        success, repos = self.run_sql("SHOW IMAGE REPOSITORIES;")
        if success and repos:
            results["image_repositories"] = repos if isinstance(repos, list) else []
            print(Colors.green(f"✅ Found {len(results['image_repositories'])} image repositories"))
        else:
            print(Colors.yellow("⚠️ Could not retrieve image repositories"))
            results["issues"].append("Cannot access image repositories")
        
        # Check specific permissions
        permission_checks = [
            ("CREATE COMPUTE POOL", "SHOW GRANTS ON ACCOUNT;"),
            ("CREATE SERVICE", "SHOW GRANTS ON COMPUTE POOL APP_POOL;"),
            ("USAGE on IMAGE REPOSITORY", "SHOW GRANTS ON IMAGE REPOSITORY APPS_DB.AI_APPS.APP_IMAGES;")
        ]
        
        for permission, query in permission_checks:
            success, grants = self.run_sql(query)
            results["permissions"][permission] = success and bool(grants)
        
        return results
    
    def diagnose_app_deployment(self, app_name: str) -> Dict[str, any]:
        """Diagnose specific app deployment issues"""
        print(Colors.blue(f"🔍 Diagnosing deployment for {app_name}..."))
        
        results = {
            "app_name": app_name,
            "services": [],
            "user_exists": False,
            "stage_exists": False,
            "tables": [],
            "recent_errors": [],
            "service_logs": {},
            "recommendations": []
        }
        
        if not self.connection_working:
            results["recommendations"].append("Establish Snowflake connection first")
            return results
        
        # Check services
        success, services = self.run_sql(f"SHOW SERVICES LIKE '{app_name}%';")
        if success and services:
            results["services"] = services if isinstance(services, list) else []
            print(Colors.green(f"✅ Found {len(results['services'])} services for {app_name}"))
            
            for service in results["services"]:
                service_name = service.get("name", "")
                status = service.get("status", "Unknown")
                print(f"   Service: {Colors.cyan(service_name)} - Status: {Colors.cyan(status)}")
                
                if status.upper() in ["FAILED", "ERROR"]:
                    # Get service logs
                    log_success, logs = self.run_sql(f"SELECT SYSTEM$GET_SERVICE_LOGS('{service_name}', 0, '{app_name}-container');")
                    if log_success and logs:
                        results["service_logs"][service_name] = logs
                        results["recommendations"].append(f"Check logs for service {service_name}")
        else:
            print(Colors.yellow(f"⚠️ No services found for {app_name}"))
            results["recommendations"].append("Deploy the application first")
        
        # Check app user
        success, users = self.run_sql(f"SHOW USERS LIKE '{app_name.upper()}_USER';")
        if success and users:
            results["user_exists"] = len(users) > 0 if isinstance(users, list) else bool(users)
            if results["user_exists"]:
                print(Colors.green(f"✅ App user {app_name.upper()}_USER exists"))
            else:
                print(Colors.yellow(f"⚠️ App user {app_name.upper()}_USER not found"))
                results["recommendations"].append("Run app setup script to create user")
        
        # Check app stage
        success, stages = self.run_sql(f"SHOW STAGES LIKE '{app_name.upper()}_STAGE';")
        if success and stages:
            results["stage_exists"] = len(stages) > 0 if isinstance(stages, list) else bool(stages)
            if results["stage_exists"]:
                print(Colors.green(f"✅ App stage {app_name.upper()}_STAGE exists"))
            else:
                print(Colors.yellow(f"⚠️ App stage {app_name.upper()}_STAGE not found"))
                results["recommendations"].append("Run app setup script to create stage")
        
        # Check app tables
        success, tables = self.run_sql(f"SHOW TABLES LIKE '{app_name.upper()}%';")
        if success and tables:
            results["tables"] = tables if isinstance(tables, list) else []
            print(Colors.green(f"✅ Found {len(results['tables'])} tables for {app_name}"))
        else:
            print(Colors.yellow(f"⚠️ No tables found for {app_name}"))
            results["recommendations"].append("Run app setup script to create tables")
        
        # Check for recent errors in logs
        if f"{app_name.upper()}_LOGS" in [t.get("name", "") for t in results["tables"]]:
            error_query = f"""
            SELECT LOG_LEVEL, LOG_MESSAGE, CREATED_AT 
            FROM {app_name.upper()}_LOGS 
            WHERE LOG_LEVEL = 'ERROR' 
            AND CREATED_AT >= DATEADD('hour', -24, CURRENT_TIMESTAMP())
            ORDER BY CREATED_AT DESC 
            LIMIT 10;
            """
            success, errors = self.run_sql(error_query)
            if success and errors:
                results["recent_errors"] = errors if isinstance(errors, list) else []
                if results["recent_errors"]:
                    print(Colors.red(f"❌ Found {len(results['recent_errors'])} recent errors"))
                    results["recommendations"].append("Review recent error logs")
        
        return results
    
    def check_github_actions_setup(self) -> Dict[str, any]:
        """Check GitHub Actions deployment setup"""
        print(Colors.blue("🔧 Checking GitHub Actions setup..."))
        
        results = {
            "secrets_documented": True,
            "workflow_exists": False,
            "dockerfile_exists": False,
            "requirements_exist": False,
            "recommendations": []
        }
        
        # Check for workflow file
        workflow_paths = [
            ".github/workflows/deploy.yml",
            ".github/workflows/deploy-spcs.yml",
            f"apps/{self.app_name}/.github/workflows/deploy.yml" if self.app_name else None
        ]
        
        for path in workflow_paths:
            if path and os.path.exists(path):
                results["workflow_exists"] = True
                print(Colors.green(f"✅ Found workflow file: {path}"))
                break
        
        if not results["workflow_exists"]:
            print(Colors.yellow("⚠️ No deployment workflow found"))
            results["recommendations"].append("Create GitHub Actions workflow from template")
        
        # Check for Dockerfile
        dockerfile_paths = [
            "Dockerfile",
            f"apps/{self.app_name}/Dockerfile" if self.app_name else None
        ]
        
        for path in dockerfile_paths:
            if path and os.path.exists(path):
                results["dockerfile_exists"] = True
                print(Colors.green(f"✅ Found Dockerfile: {path}"))
                break
        
        if not results["dockerfile_exists"]:
            print(Colors.yellow("⚠️ No Dockerfile found"))
            results["recommendations"].append("Create Dockerfile from template")
        
        # Check for requirements.txt
        req_paths = [
            "requirements.txt",
            f"apps/{self.app_name}/requirements.txt" if self.app_name else None
        ]
        
        for path in req_paths:
            if path and os.path.exists(path):
                results["requirements_exist"] = True
                print(Colors.green(f"✅ Found requirements.txt: {path}"))
                break
        
        if not results["requirements_exist"]:
            print(Colors.yellow("⚠️ No requirements.txt found"))
            results["recommendations"].append("Create requirements.txt with dependencies")
        
        return results
    
    def run_comprehensive_diagnosis(self) -> Dict[str, any]:
        """Run complete diagnosis of the system"""
        print(Colors.bold("🏥 Running Comprehensive SPCS Deployment Diagnosis"))
        print("=" * 60)
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "cli_working": False,
            "connection_working": False,
            "spcs_ready": False,
            "app_specific": {},
            "github_actions": {},
            "overall_health": "Unknown",
            "priority_issues": [],
            "next_steps": []
        }
        
        # Check CLI
        diagnosis["cli_working"] = self.check_snowflake_cli()
        if not diagnosis["cli_working"]:
            diagnosis["priority_issues"].append("Install Snowflake CLI")
            diagnosis["next_steps"].append("Visit https://docs.snowflake.com/en/developer-guide/snowflake-cli-v2/installation/installation")
            return diagnosis
        
        # Check connection
        diagnosis["connection_working"] = self.test_connection()
        if not diagnosis["connection_working"]:
            diagnosis["priority_issues"].append("Fix Snowflake authentication")
            diagnosis["next_steps"].append("Check private key format and user permissions")
            return diagnosis
        
        # Check SPCS prerequisites
        spcs_results = self.check_spcs_prerequisites()
        diagnosis["spcs_ready"] = len(spcs_results["issues"]) == 0
        
        if not diagnosis["spcs_ready"]:
            diagnosis["priority_issues"].extend(spcs_results["issues"])
            diagnosis["next_steps"].append("Run framework/helpers/snowflake/spcs-setup.sh")
        
        # App-specific diagnosis
        if self.app_name:
            diagnosis["app_specific"] = self.diagnose_app_deployment(self.app_name)
            
            if diagnosis["app_specific"]["recommendations"]:
                diagnosis["next_steps"].extend(diagnosis["app_specific"]["recommendations"])
        
        # GitHub Actions check
        diagnosis["github_actions"] = self.check_github_actions_setup()
        if diagnosis["github_actions"]["recommendations"]:
            diagnosis["next_steps"].extend(diagnosis["github_actions"]["recommendations"])
        
        # Determine overall health
        if diagnosis["cli_working"] and diagnosis["connection_working"] and diagnosis["spcs_ready"]:
            if self.app_name and len(diagnosis["app_specific"]["services"]) > 0:
                diagnosis["overall_health"] = "Healthy"
            else:
                diagnosis["overall_health"] = "Ready for Deployment"
        elif diagnosis["connection_working"]:
            diagnosis["overall_health"] = "Needs Setup"
        else:
            diagnosis["overall_health"] = "Connection Issues"
        
        return diagnosis
    
    def print_summary_report(self, diagnosis: Dict[str, any]):
        """Print a formatted summary report"""
        print("\n" + Colors.bold("📊 DIAGNOSIS SUMMARY REPORT"))
        print("=" * 60)
        
        # Overall health
        health = diagnosis["overall_health"]
        if health == "Healthy":
            health_color = Colors.green
        elif health == "Ready for Deployment":
            health_color = Colors.blue
        elif health == "Needs Setup":
            health_color = Colors.yellow
        else:
            health_color = Colors.red
        
        print(f"Overall Health: {health_color(health)}")
        print(f"Timestamp: {Colors.cyan(diagnosis['timestamp'])}")
        
        if self.app_name:
            print(f"App Name: {Colors.cyan(self.app_name)}")
        
        print("\n" + Colors.bold("🔧 System Status:"))
        print(f"  Snowflake CLI: {'✅' if diagnosis['cli_working'] else '❌'}")
        print(f"  Connection: {'✅' if diagnosis['connection_working'] else '❌'}")
        print(f"  SPCS Ready: {'✅' if diagnosis['spcs_ready'] else '❌'}")
        
        if self.app_name and diagnosis["app_specific"]:
            print(f"\n" + Colors.bold(f"📱 App Status ({self.app_name}):"))
            app = diagnosis["app_specific"]
            print(f"  Services: {Colors.cyan(str(len(app['services'])))}")
            print(f"  User Exists: {'✅' if app['user_exists'] else '❌'}")
            print(f"  Stage Exists: {'✅' if app['stage_exists'] else '❌'}")
            print(f"  Tables: {Colors.cyan(str(len(app['tables'])))}")
            print(f"  Recent Errors: {Colors.red(str(len(app['recent_errors']))) if app['recent_errors'] else '✅ None'}")
        
        # Priority issues
        if diagnosis["priority_issues"]:
            print(f"\n" + Colors.bold("🚨 Priority Issues:"))
            for i, issue in enumerate(diagnosis["priority_issues"], 1):
                print(f"  {i}. {Colors.red(issue)}")
        
        # Next steps
        if diagnosis["next_steps"]:
            print(f"\n" + Colors.bold("📋 Next Steps:"))
            for i, step in enumerate(diagnosis["next_steps"], 1):
                print(f"  {i}. {Colors.blue(step)}")
        else:
            print(f"\n{Colors.green('🎉 System appears healthy! No immediate action required.')}")

def main():
    """Main function to run the troubleshooting tool"""
    parser = argparse.ArgumentParser(description="Snowflake SPCS Deployment Troubleshooting Tool")
    parser.add_argument("--app", help="Specific app name to diagnose")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--quick", action="store_true", help="Run quick health check only")
    
    args = parser.parse_args()
    
    troubleshooter = SnowflakeTroubleshooter(app_name=args.app)
    
    try:
        if args.quick:
            # Quick check
            cli_ok = troubleshooter.check_snowflake_cli()
            conn_ok = troubleshooter.test_connection() if cli_ok else False
            
            if args.json:
                result = {"cli_working": cli_ok, "connection_working": conn_ok}
                print(json.dumps(result, indent=2))
            else:
                status = "✅ Ready" if cli_ok and conn_ok else "❌ Issues Found"
                print(f"Quick Status: {status}")
        else:
            # Comprehensive diagnosis
            diagnosis = troubleshooter.run_comprehensive_diagnosis()
            
            if args.json:
                print(json.dumps(diagnosis, indent=2))
            else:
                troubleshooter.print_summary_report(diagnosis)
    
    except KeyboardInterrupt:
        print(Colors.yellow("\n⚠️ Operation cancelled by user"))
        sys.exit(1)
    except Exception as e:
        print(Colors.red(f"\n❌ Unexpected error: {e}"))
        sys.exit(1)

if __name__ == "__main__":
    main()