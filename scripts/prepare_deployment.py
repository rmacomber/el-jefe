#!/usr/bin/env python3
"""
Deployment Preparation Script for El Jefe Monitoring Dashboard

Prepares the dashboard for production deployment:
- Environment validation
- Security hardening
- Configuration validation
- Health checks
- Documentation generation
"""

import os
import sys
import json
import shutil
import subprocess
import hashlib
import secrets
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from monitoring_dashboard import MonitoringDashboard
except ImportError as e:
    print(f"⚠️  Could not import monitoring_dashboard: {e}")
    MonitoringDashboard = None


class DeploymentPreparer:
    """Prepares dashboard for production deployment"""

    def __init__(self):
        self.deployment_config = {}
        self.health_checks = []
        self.security_audit = {}

    def validate_environment(self):
        """Validate deployment environment"""
        print("🌍 Validating Deployment Environment")
        print("-" * 40)

        # Check Python version
        python_version = sys.version_info
        print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

        if python_version < (3, 8):
            print("❌ Python 3.8+ required for production")
            return False

        # Check required packages
        required_packages = [
            'aiohttp',
            'aiofiles',
            'websockets',
            'aiohttp_cors'
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("   Install with: pip install " + " ".join(missing_packages))
            return False

        print("✅ All required packages available")

        # Check file permissions
        static_dir = Path("static")
        if static_dir.exists():
            file_count = len(list(static_dir.rglob("*")))
            print(f"Static files found: {file_count}")

            # Check write permissions
            if os.access(static_dir, os.W_OK):
                print("✅ Static directory writeable")
            else:
                print("⚠️  Static directory not writeable")

        # Check networking capabilities
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('localhost', 0))
            port = s.getsockname()[1]
            s.close()
            print(f"✅ Network capabilities confirmed (can use port {port})")
        except Exception as e:
            print(f"❌ Network check failed: {e}")
            return False

        return True

    def setup_production_config(self):
        """Setup production configuration"""
        print("\n⚙️ Setting Up Production Configuration")
        print("-" * 40)

        # Generate secure password
        if not os.getenv("DASHBOARD_PASSWORD"):
            password = secrets.token_urlsafe(16)
            print(f"Generated secure password: {password}")
            print("   Add to environment: export DASHBOARD_PASSWORD=" + password)
        else:
            password = os.getenv("DASHBOARD_PASSWORD")
            print("✅ Using existing password from environment")

        # Create production config file
        config = {
            "production": {
                "host": "0.0.0.0",
                "port": 8080,
                "password": hashlib.sha256(password.encode()).hexdigest(),
                "enable_auth": True,
                "session_timeout": 3600,
                "max_connections": 100,
                "enable_logging": True,
                "log_level": "INFO",
                "enable_metrics": True,
                "enable_websocket_auth": True
            },
            "security": {
                "enable_cors": True,
                "allowed_origins": ["http://localhost:8080", "https://localhost:8080"],
                "max_request_size": 10485760,  # 10MB
                "enable_rate_limiting": True,
                "rate_limit_requests": 100,
                "rate_limit_window": 60,
                "enable_input_validation": True
            },
            "monitoring": {
                "enable_health_checks": True,
                "health_check_interval": 30,
                "enable_metrics_collection": True,
                "metrics_retention_days": 30,
                "enable_alerts": True
            },
            "performance": {
                "enable_compression": True,
                "compression_level": 6,
                "enable_caching": True,
                "cache_ttl": 300,
                "max_concurrent_connections": 50
            }
        }

        # Get local IP for network access
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            config["production"]["local_ip"] = local_ip
            print(f"Local IP detected: {local_ip}")
        except Exception as e:
            print(f"⚠️  Could not detect local IP: {e}")
            config["production"]["local_ip"] = "127.0.0.1"

        # Save configuration
        config_file = Path("config/production.json")
        config_file.parent.mkdir(exist_ok=True)

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Production config saved to {config_file}")
        self.deployment_config = config

        return config

    def perform_security_audit(self):
        """Perform security audit"""
        print("\n🛡️ Performing Security Audit")
        print("-" * 40)

        security_issues = []

        # Check for hardcoded secrets
        sensitive_patterns = [
            'password', 'secret', 'key', 'token', 'auth'
        ]

        print("Scanning for hardcoded secrets...")
        security_violations = []

        for file_path in Path('.').rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    line_number = 0

                    for line in content.split('\n'):
                        line_number += 1
                        line_lower = line.lower()

                        for pattern in sensitive_patterns:
                            if pattern in line_lower and ('=' in line or ':' in line):
                                # Check if it's not a comment or variable name
                                stripped = line.strip()
                                if (not stripped.startswith('#') and
                                    not stripped.startswith('//') and
                                    not stripped.startswith('"""') and
                                    not stripped.startswith("'''")):
                                    security_violations.append({
                                        'file': str(file_path),
                                        'line': line_number,
                                        'content': stripped[:50] + "..." if len(stripped) > 50 else stripped
                                    })

            except Exception as e:
                print(f"⚠️  Could not scan {file_path}: {e}")

        if security_violations:
            print(f"❌ Found {len(security_violations)} potential security issues:")
            for violation in security_violations[:5]:  # Show first 5
                print(f"   • {violation['file']}:{violation['line']} - {violation['content']}")
            if len(security_violations) > 5:
                print(f"   ... and {len(security_violations) - 5} more")
        else:
            print("✅ No hardcoded secrets found")

        self.security_audit = {
            'scan_timestamp': time.time(),
            'violations_found': len(security_violations),
            'violations': security_violations[:10]  # Limit storage
        }

        # Check file permissions
        print("\nChecking file permissions...")
        permission_issues = []

        sensitive_files = [
            "config/production.json",
            "monitoring_state.json",
            ".env"
        ]

        for file_path in sensitive_files:
            path = Path(file_path)
            if path.exists():
                mode = path.stat().st_mode
                if mode & 0o077:  # Check if others have write permission
                    permission_issues.append(f"{file_path} has overly permissive permissions")
                    try:
                        # Restrict permissions (owner read/write only)
                        path.chmod(0o600)
                        print(f"✅ Fixed permissions for {file_path}")
                    except Exception as e:
                        print(f"⚠️  Could not fix permissions for {file_path}: {e}")

        if permission_issues:
            print(f"⚠️  Permission issues found: {len(permission_issues)}")
            for issue in permission_issues:
                print(f"   • {issue}")

        return len(security_violations) == 0

    def run_health_checks(self):
        """Run comprehensive health checks"""
        print("\n🏥 Running Health Checks")
        print("-" * 40)

        health_results = {}

        # Check dashboard startup
        if MonitoringDashboard:
            try:
                print("Testing dashboard startup...")
                test_dashboard = MonitoringDashboard(port=8083)
                start_time = time.time()
                runner = await test_dashboard.start()
                startup_time = (time.time() - start_time) * 1000

                # Quick test of API endpoints
                import aiohttp
                test_url = "http://localhost:8083/api/status"

                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(test_url) as response:
                            if response.status == 200:
                                health_results['dashboard_startup'] = "PASS"
                                health_results['startup_time_ms'] = startup_time
                                health_results['api_responsive'] = "PASS"
                            else:
                                health_results['dashboard_startup'] = "FAIL"
                except Exception as e:
                    health_results['dashboard_startup'] = f"ERROR: {e}"

                await runner.cleanup()
                await test_dashboard.stop()

            except Exception as e:
                health_results['dashboard_startup'] = f"ERROR: {e}"

            if 'startup_time_ms' in health_results:
                print(f"✅ Dashboard startup: {health_results['startup_time_ms']:.2f}ms")
                if health_results['startup_time_ms'] > 5000:
                    print("⚠️  Slow startup detected")
                else:
                    print("✅ Startup time acceptable")

        # Check disk space
        disk_usage = shutil.disk_usage('.')
        total_gb = disk_usage.total / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        used_gb = total_gb - free_gb
        usage_percent = (used_gb / total_gb) * 100

        print(f"✅ Disk space: {used_gb:.1f}/{total_gb:.1f}GB ({usage_percent:.1f}%)")

        if free_gb < 1:  # Less than 1GB free
            print("⚠️  Low disk space warning")

        health_results['disk_space_gb'] = {
            'total': total_gb,
            'used': used_gb,
            'free': free_gb,
            'usage_percent': usage_percent
        }

        # Check memory availability (approximate)
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            total_mem_gb = memory.total / (1024**3)

            print(f"✅ Available memory: {available_gb:.1f}/{total_mem_gb:.1f}GB")

            if available_gb < 1:  # Less than 1GB available
                print("⚠️  Low memory warning")

            health_results['memory_gb'] = {
                'available': available_gb,
                'total': total_mem_gb
            }
        except ImportError:
            print("⚠️  psutil not available for memory check")
            health_results['memory_check'] = "SKIP"

        # Check network connectivity
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            result = s.connect_ex(('google.com', 80))
            s.close()

            if result == 0:
                health_results['network'] = "PASS"
                print("✅ Network connectivity confirmed")
            else:
                health_results['network'] = "FAIL"
                print("⚠️  Network connectivity issues detected")

        except Exception as e:
            health_results['network'] = f"ERROR: {e}"
            print(f"⚠️  Network check failed: {e}")

        self.health_checks = health_results
        return health_results

    def generate_deployment_documentation(self):
        """Generate deployment documentation"""
        print("\n📚 Generating Deployment Documentation")
        print("-" * 40)

        # Create deployment guide
        deployment_guide = f"""# El Jefe Monitoring Dashboard - Deployment Guide

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

The El Jefe Monitoring Dashboard provides real-time monitoring and analytics for AI agent orchestration. This guide covers production deployment.

## Prerequisites

- Python 3.8+
- Required packages: aiohttp, aiofiles, websockets, aiohttp_cors
- Network access for multi-user support (optional)

## Security Configuration

The dashboard includes multiple security features:

### Authentication
- Password protection using SHA-256 hashing
- Configurable session timeout
- WebSocket authentication

### Network Security
- CORS configuration for cross-origin requests
- Input validation and sanitization
- Rate limiting capabilities

### File Security
- Restricted file permissions on sensitive files
- No hardcoded credentials in code
- Environment variable configuration

## Deployment Steps

### 1. Environment Setup

```bash
# Clone or download the project
git clone <repository-url>
cd orchestrator-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DASHBOARD_PASSWORD="your-secure-password"
export DASHBOARD_HOST="0.0.0.0"  # For network access
export DASHBOARD_PORT="8080"
```

### 2. Configuration

The dashboard automatically generates a production configuration in `config/production.json`.

Key configuration options:
- `host`: Network interface to bind (0.0.0.0 for all interfaces)
- `port`: Port number (default: 8080)
- `password`: Authentication password
- `enable_auth`: Enable password protection
- `max_connections`: Maximum concurrent connections
- `enable_rate_limiting`: Enable request rate limiting

### 3. Service Deployment

#### Option A: Direct Python

```bash
# Start the dashboard
python3 monitoring_dashboard.py

# The dashboard will be available at:
# Local: http://localhost:8080
# Network: http://YOUR_IP:8080
```

#### Option B: Systemd Service

Create `/etc/systemd/system/el-jefe-dashboard.service`:

```ini
[Unit]
Description=El Jefe Monitoring Dashboard
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/orchestrator-agent
Environment=DASHBOARD_PASSWORD=your-secure-password
ExecStart=/usr/bin/python3 monitoring_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable el-jefe-dashboard
sudo systemctl start el-jefe-dashboard
```

#### Option C: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python3", "monitoring_dashboard.py"]
```

Build and run:
```bash
docker build -t el-jefe-dashboard .
docker run -p 8080:8080 -e DASHBOARD_PASSWORD=your-secure-password el-jefe-dashboard
```

### 4. Firewall Configuration

If using firewall, allow dashboard port:
```bash
# ufw
sudo ufw allow 8080

# iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### 5. SSL/TLS (Optional)

For HTTPS, use a reverse proxy like Nginx:

```nginx
server {{
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {{
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
```

## Health Checks

The dashboard includes health endpoints:

- `/api/status` - System status
- `/api/health` - Health check endpoint
- WebSocket connection testing

## Monitoring

### Log Monitoring

- Application logs to console
- Consider file logging for production
- Monitor resource usage

### Metrics

- Performance metrics collection
- User activity tracking
- Error rate monitoring

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   Error: [Errno 98] Address already in use
   ```
   Solution: Change port number or stop conflicting services

2. **Permission Denied**
   ```
   Error: Permission denied
   ```
   Solution: Check file permissions and user privileges

3. **WebSocket Connection Failed**
   ```
   WebSocket connection failed
   ```
   Solution: Check firewall and network configuration

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check Scripts

Use the provided test scripts:
```bash
# Integration tests
python3 tests/test_dashboard_integration.py

# Performance optimization
python3 scripts/optimize_dashboard.py
```

## Security Best Practices

1. **Regular Updates**
   - Keep Python and packages updated
   - Monitor security advisories

2. **Access Control**
   - Use strong passwords
   - Limit network access if possible
   - Monitor access logs

3. **Data Protection**
   - Regular backups
   - Encrypt sensitive configuration
   - Monitor data retention

4. **Monitoring**
   - Monitor system resources
   - Set up alerting for failures
   - Log all access attempts

## API Documentation

### Authentication
```http
POST /login
Content-Type: application/json
{{"password": "your-password"}}
```

### WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.send(JSON.stringify({{"type": "auth", "token": "your-token"}}));
```

### REST API Endpoints

- `GET /api/status` - System status
- `GET /api/agents` - Agent information
- `GET /api/workflows` - Workflow data
- `GET /api/metrics` - System metrics
- `GET /api/analytics/*` - Advanced analytics

## Support

For issues or questions:
- Check the health check reports
- Review the troubleshooting section
- Contact development team with logs and configuration details

---

**Production Deployment Checklist:**

- [ ] Python 3.8+ installed
- [ ] Required packages installed
- [ ] Environment variables configured
- [ ] Security measures implemented
- [ ] Firewall rules configured
- [ ] Health checks passing
- [ ] SSL/TLS configured (if required)
- [ ] Monitoring system set up
- [ ] Backup procedures in place
"""

        # Save deployment guide
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)

        guide_file = docs_dir / "DEPLOYMENT.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(deployment_guide)

        print(f"✅ Deployment guide saved to {guide_file}")

        # Create README for this deployment
        readme_content = f"""# El Jefe Dashboard Deployment

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Quick Start

```bash
# Start the dashboard
python3 monitoring_dashboard.py

# Access at:
# Local: http://localhost:8080
# Network: http://{self.deployment_config.get('production', {}).get('local_ip', '127.0.0.1')}:8080
```

## Security Features

- ✅ Password protection enabled
- ✅ Input validation active
- ✅ Rate limiting configured
- ✅ CORS properly set up

## Performance Metrics

{self.get_performance_summary()}

## Health Check Status

{self.get_health_summary()}

For detailed documentation, see `docs/DEPLOYMENT.md`.
"""

        readme_file = Path("DEPLOYMENT-README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"✅ Deployment README saved to {readme_file}")

    def get_performance_summary(self):
        """Get performance summary for documentation"""
        if self.health_checks:
            return {
                'startup': self.health_checks.get('dashboard_startup', 'N/A'),
                'disk_space': self.health_checks.get('disk_space_gb', {}),
                'memory': self.health_checks.get('memory_gb', {})
            }
        return {}

    def get_health_summary(self):
        """Get health check summary for documentation"""
        if self.health_checks:
            summary = {}
            for key, value in self.health_checks.items():
                if isinstance(value, str):
                    summary[key] = value
                elif isinstance(value, dict):
                    if 'status' in value:
                        summary[key] = value['status']
                    else:
                        summary[key] = "OK"
                else:
                    summary[key] = str(value)
            return summary
        return {}

    def prepare_deployment_package(self):
        """Create deployment package"""
        print("\n📦 Creating Deployment Package")
        print("-" * 40)

        # Create deployment directory
        deploy_dir = Path("deployment")
        deploy_dir.mkdir(exist_ok=True)

        # Copy essential files
        essential_files = [
            "monitoring_dashboard.py",
            "requirements.txt",
            "static/",
            "config/",
            "tests/",
            "scripts/"
        ]

        for file_pattern in essential_files:
            src_path = Path(file_pattern)
            dest_path = deploy_dir / file_pattern

            if src_path.exists():
                if src_path.is_file():
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    print(f"✅ Copied {file_pattern}")
                elif src_path.is_dir():
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(src_path, dest_path)
                    print(f"✅ Copied {file_pattern}/ directory")

        # Create deployment scripts
        deploy_scripts = deploy_dir / "scripts"
        deploy_scripts.mkdir(exist_ok=True)

        # Create deployment script
        deploy_script = deploy_scripts / "deploy.sh"
        with open(deploy_script, 'w') as f:
            f.write("""#!/bin/bash
# El Jefe Dashboard Deployment Script

set -e

echo "🚀 Starting El Jefe Dashboard Deployment..."

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$python_version" != "3.9" ] && [ "$python_version" != "3.10" ] && [ "$python_version" != "3.11" ]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Set environment variables
if [ -z "$DASHBOARD_PASSWORD" ]; then
    echo "🔐 Setting environment variables..."
    export DASHBOARD_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
    echo "Generated password: $DASHBOARD_PASSWORD"
fi

# Create config directory
mkdir -p config

# Start dashboard
echo "🚀 Starting dashboard..."
python3 monitoring_dashboard.py
""")

        deploy_script.chmod(0o755)
        print(f"✅ Deployment script created: {deploy_script}")

        # Create systemd service file
        service_file = deploy_dir / "el-jefe-dashboard.service"
        with open(service_file, 'w') as f:
            f.write("""[Unit]
Description=El Jefe Monitoring Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=DASHBOARD_PASSWORD=$DASHBOARD_PASSWORD
ExecStart=/usr/bin/python3 $(pwd)/monitoring_dashboard.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
""")

        print(f"✅ Systemd service file created: {service_file}")

        # Create Docker configuration
        dockerfile = deploy_dir / "Dockerfile"
        with open(dockerfile, 'w') as f:
            f.write("""FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u dashboard

# Set ownership
RUN chown -R dashboard:dashboard /app

# Switch to non-root user
USER dashboard

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/api/status || exit 1

# Start application
CMD ["python3", "monitoring_dashboard.py"]
""")

        dockerignore_file = deploy_dir / ".dockerignore"
        with open(dockerignore_file, 'w') as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.pyo
*.pyd
.Python
build/
dist/
*.egg-info/

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
""")

        print(f"✅ Docker configuration created")

        # Create deployment package info
        package_info = {
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'includes': [
                'monitoring_dashboard.py',
                'requirements.txt',
                'static/',
                'config/',
                'tests/',
                'scripts/'
            ],
            'deployment_options': [
                'Direct Python execution',
                'Systemd service',
                'Docker container',
                'Reverse proxy (Nginx/Apache)'
            ]
        }

        package_file = deploy_dir / "package.json"
        with open(package_file, 'w') as f:
            json.dump(package_info, f, indent=2)

        print(f"✅ Deployment package created in {deploy_dir}")

        # Calculate package size
        total_size = sum(f.stat().st_size for f in deploy_dir.rglob("*") if f.is_file())
        print(f"📦 Package size: {total_size:,} bytes ({total_size/(1024*1024):.2f} MB)")

        return deploy_dir

    def run_deployment_preparation(self):
        """Run complete deployment preparation"""
        print("🚀 Starting Deployment Preparation")
        print("=" * 60)

        success = True

        # Run all preparation steps
        steps = [
            ("Environment Validation", self.validate_environment),
            ("Configuration Setup", self.setup_production_config),
            ("Security Audit", self.perform_security_audit),
            ("Health Checks", self.run_health_checks),
            ("Documentation Generation", self.generate_deployment_documentation),
            ("Deployment Package", self.prepare_deployment_package)
        ]

        for step_name, step_func in steps:
            try:
                print(f"\n📋 {step_name}")
                result = step_func()
                if result is False:
                    success = False
                    print(f"❌ {step_name} failed")
                elif result is True:
                    print(f"✅ {step_name} completed")
                else:
                    print(f"✅ {step_name} completed")
            except Exception as e:
                print(f"❌ {step_name} failed: {e}")
                success = False

        print("\n" + "=" * 60)
        if success:
            print("🎉 Deployment preparation completed successfully!")
            print("The dashboard is ready for production deployment.")
            print("\nNext steps:")
            print("1. Choose a deployment method:")
            print("   • Direct Python execution (development/testing)")
            print("   • Systemd service (production)")
            print("   • Docker container (containerized deployment)")
            print("   • Reverse proxy (load balanced)")
            print("\n2. Run the deployment:")
            print("   python3 monitoring_dashboard.py")
            print("   # Or use the provided deployment scripts")
            print("   deployment/scripts/deploy.sh")
            print("\n3. Access the dashboard:")
            local_ip = self.deployment_config.get('production', {}).get('local_ip', '127.0.0.1')
            print(f"   Local: http://localhost:8080")
            print(f"   Network: http://{local_ip}:8080")
            return 0
        else:
            print("❌ Deployment preparation failed!")
            print("Please address the issues above before deploying.")
            return 1


def main():
    """Main deployment preparation script"""
    preparer = DeploymentPreparer()
    exit_code = preparer.run_deployment_preparation()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()