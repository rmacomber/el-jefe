# 📅 El Jefe Workflow Scheduler Guide

The workflow scheduler enables you to automate recurring tasks and schedule workflows to run at specific times or intervals. This powerful feature turns El Jefe into a complete automation platform.

## ✨ **Key Features**

### **🔄 Flexible Scheduling**
- **One-time execution** - Run at specific date/time
- **Daily schedules** - Run every day at specified time
- **Weekly schedules** - Run on specific days
- **Interval-based** - Run every N minutes/hours/days
- **Custom patterns** - Advanced scheduling configurations

### **📊 Workflow Management**
- **Persisted storage** - Workflows survive system restarts
- **Status tracking** - Monitor pending, running, completed, failed workflows
- **Run history** - Track execution counts and timing
- **Error handling** - Automatic retry and failure reporting

### **⚙️ Advanced Features**
- **Workspace templates** - Custom naming for scheduled workspaces
- **Agent selection** - Specify which agents to use
- **Notifications** - Email and desktop alerts (configurable)
- **Metadata support** - Custom tags and organization

## 🚀 **Quick Start**

### **Basic Scheduling**

```bash
# Schedule a daily report at 9 AM
el-jefe --schedule-add "Daily Report" "Generate daily analytics report" "Create comprehensive analytics report" "daily"

# Schedule a weekly backup every Sunday at 2 AM
el-jefe --schedule-add "Weekly Backup" "Backup all project files" "Create automated backup of workspace" "weekly"

# Schedule an hourly health check
el-jefe --schedule-add "Health Check" "System health monitoring" "Check system status and alert on issues" "interval"
```

### **Managing Workflows**

```bash
# List all scheduled workflows
el-jefe --schedule-list

# Start the scheduler daemon (runs all scheduled workflows)
el-jefe --schedule-daemon

# Check workflow status from scheduler CLI
python3 scripts/scheduler_cli.py list

# View upcoming runs in next 24 hours
python3 scripts/scheduler_cli.py upcoming --hours 24
```

## 📋 **Scheduling Options**

### **Daily Scheduling**
```bash
el-jefe --schedule-add "Daily Task" "Description" "Goal" "daily"
```
- **Default**: Runs at 9:00 AM daily
- **Configuration**: Automatically configured for optimal timing

### **Weekly Scheduling**
```bash
el-jefe --schedule-add "Weekly Task" "Description" "Goal" "weekly"
```
- **Default**: Runs every Monday at 9:00 AM
- **Days**: 0=Monday, 1=Tuesday, ..., 6=Sunday

### **Interval Scheduling**
```bash
el-jefe --schedule-add "Hourly Task" "Description" "Goal" "interval"
```
- **Default**: Runs every 1 hour
- **Configuration**: Flexible interval settings

### **One-time Scheduling**
```bash
# Using scheduler CLI for more control
python3 scripts/scheduler_cli.py schedule "One-time Task" "Description" "Goal" once --run-at "2025-12-01T14:30:00"
```

## 🔧 **Advanced Usage**

### **Scheduler CLI Tool**

The comprehensive scheduler CLI provides full workflow management:

```bash
# Launch scheduler CLI
python3 scripts/scheduler_cli.py

# Available commands:
#   list                    - List all workflows
#   show <workflow-id>      - Show detailed workflow info
#   schedule <options>      - Create new workflow
#   pause <workflow-id>     - Pause a workflow
#   resume <workflow-id>    - Resume paused workflow
#   cancel <workflow-id>    - Cancel a workflow
#   delete <workflow-id>    - Delete workflow
#   upcoming [--hours=N]    - Show upcoming runs
#   start-daemon           - Start scheduler daemon
```

### **Creating Complex Schedules**

```bash
# Schedule with specific time
python3 scripts/scheduler_cli.py schedule "Morning Report" "Daily analytics" "Generate report" daily --hour 8 --minute 30

# Schedule for specific day
python3 scripts/scheduler_cli.py schedule "Sunday Cleanup" "Weekly maintenance" "Clean up old files" weekly --day-of-week 6 --hour 2

# Schedule every 6 hours
python3 scripts/scheduler_cli.py schedule "Frequent Check" "System monitoring" "Check system health" interval --interval-value 6 --interval-unit hours

# One-time execution
python3 scripts/scheduler_cli.py schedule "Yearly Report" "Annual summary" "Generate yearly report" once --run-at "2025-12-31T23:59:00"
```

### **Workflow Configuration**

```bash
# Schedule with custom workspace template
python3 scripts/scheduler_cli.py schedule "Custom Task" "Description" "Goal" daily \
  --workspace-template "scheduled-{name}-{timestamp}"

# Schedule with specific agents
python3 scripts/scheduler_cli.py schedule "Security Scan" "Weekly security" "Run security analysis" weekly \
  --agent-types "security_analyst,coder"

# Schedule with maximum runs
python3 scripts/scheduler_cli.py schedule "Limited Task" "Description" "Goal" daily \
  --max-runs 30
```

## 🏗️ **Architecture**

### **Component Overview**

```
┌─────────────────────┐    ┌─────────────────────┐
│   Main CLI          │    │  Scheduler CLI      │
│   (el-jefe)         │    │  (scheduler_cli.py) │
│                     │    │                     │
│ --schedule-list     │    │ list                │
│ --schedule-add      │    │ schedule            │
│ --schedule-daemon   │    │ pause/resume        │
└─────────────────────┘    └─────────────────────┘
          │                         │
          └─────────────┬───────────┘
                        │
                ┌───────▼───────┐
                │  Workflow      │
                │  Scheduler     │
                │  (Core Module) │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │   Orchestrator │
                │   (Execution)  │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │   Workspace    │
                │   Management   │
                └───────────────┘
```

### **Data Storage**

```
workspaces/scheduler/
├── scheduled_workflows.json     # Workflow definitions
├── scheduler.log                # Execution logs
└── workspaces/                  # Individual execution results
    ├── scheduled-daily-report-20251124-090000/
    ├── scheduled-backup-20251124-020000/
    └── ...
```

### **Workflow Lifecycle**

1. **Creation** → Define workflow with schedule and configuration
2. **Scheduling** → Calculate next run time based on schedule type
3. **Queuing** → Workflow waits in pending status
4. **Execution** → Scheduler runs workflow via orchestrator
5. **Completion** → Update status and calculate next run (if recurring)
6. **Persistence** → Save state to survive restarts

## 📝 **Practical Examples**

### **DevOps Automation**

```bash
# Daily code quality checks
el-jefe --schedule-add "Code Quality" "Run code analysis" "Analyze all repositories for code quality issues" "daily"

# Weekly security scans
el-jefe --schedule-add "Security Scan" "Security vulnerability assessment" "Scan all applications for security issues" "weekly"

# Monthly dependency updates
el-jefe --schedule-add "Update Dependencies" "Update project dependencies" "Check and update all project dependencies" "monthly"
```

### **Content Creation**

```bash
# Daily blog research
el-jefe --schedule-add "Blog Research" "Research trending topics" "Find trending topics for technical blog posts" "daily"

# Weekly newsletter
el-jefe --schedule-add "Newsletter" "Create weekly newsletter" "Generate and send weekly technical newsletter" "weekly"

# Monthly reports
el-jefe --schedule-add "Monthly Report" "Generate monthly analytics" "Create comprehensive monthly analytics report" "monthly"
```

### **System Maintenance**

```bash
# Hourly health checks
el-jefe --schedule-add "Health Monitor" "System health monitoring" "Check all system components and report status" "interval"

# Daily log cleanup
el-jefe --schedule-add "Log Cleanup" "Clean up old log files" "Archive and remove log files older than 30 days" "daily"

# Weekly performance analysis
el-jefe --schedule-add "Performance Review" "System performance analysis" "Analyze system performance metrics and identify bottlenecks" "weekly"
```

## 🔍 **Monitoring and Troubleshooting**

### **Checking Status**

```bash
# List all workflows with status
el-jefe --schedule-list

# Detailed workflow information
python3 scripts/scheduler_cli.py show <workflow-id>

# Check for upcoming runs
python3 scripts/scheduler_cli.py upcoming --hours 48
```

### **Common Issues**

**Workflow not running:**
```bash
# Check if scheduler daemon is running
ps aux | grep "main.py.*schedule-daemon"

# Check workflow status
python3 scripts/scheduler_cli.py show <workflow-id>

# Verify schedule configuration
python3 scripts/scheduler_cli.py show <workflow-id>
```

**Workspace permissions:**
```bash
# Check workspace directory permissions
ls -la workspaces/scheduler/

# Ensure write permissions
chmod 755 workspaces/scheduler/
```

**Logging issues:**
```bash
# Check scheduler logs
tail -f workspaces/scheduler/scheduler.log

# Check individual workflow logs
find workspaces/ -name "*.log" -mtime -1
```

## ⚡ **Performance Considerations**

### **Resource Management**
- Scheduler daemon runs in background with minimal overhead
- Each workflow gets isolated workspace to prevent conflicts
- Automatic cleanup of old workspaces preserves disk space
- Concurrent execution limits prevent system overload

### **Optimization Tips**
```bash
# Clean up old scheduled workspaces
python3 main.py --cleanup 7

# Use specific agent types to optimize resource usage
python3 scripts/scheduler_cli.py schedule "Optimized Task" "Description" "Goal" daily \
  --agent-types "researcher"

# Set reasonable maximum run limits
python3 scripts/scheduler_cli.py schedule "Limited Task" "Description" "Goal" daily \
  --max-runs 100
```

## 🔄 **Integration Examples**

### **CI/CD Pipeline Integration**

```bash
# Schedule pre-deployment checks
el-jefe --schedule-add "Pre-deployment Checks" "Run pre-deployment validation" "Validate code quality and security before deployment" "daily"

# Schedule post-deployment monitoring
el-jefe --schedule-add "Post-deployment Monitor" "Monitor deployment health" "Check system health after deployments" "interval"
```

### **Monitoring Integration**

```bash
# Schedule external API monitoring
el-jefe --schedule-add "API Monitor" "External API health check" "Check external API endpoints and report status" "interval"

# Schedule database maintenance
el-jefe --schedule-add "DB Maintenance" "Database optimization" "Optimize database performance and clean up old data" "weekly"
```

## 🎯 **Best Practices**

### **Scheduling Guidelines**
1. **Start simple** - Begin with basic daily/weekly schedules
2. **Avoid overlap** - Ensure workflows don't conflict with each other
3. **Monitor resources** - Track system resource usage for frequent tasks
4. **Test thoroughly** - Validate workflows before scheduling
5. **Document clearly** - Use descriptive names and goals

### **Workflow Design**
1. **Specific goals** - Clear, actionable objectives for each workflow
2. **Idempotent** - Workflows should handle repeated execution safely
3. **Error handling** - Design workflows to gracefully handle failures
4. **Appropriate agents** - Choose the right specialized agents for tasks
5. **Output organization** - Structure results for easy review

### **Maintenance**
1. **Regular reviews** - Periodically review and update scheduled workflows
2. **Cleanup** - Remove old or completed workflows
3. **Monitoring** - Track execution success rates and performance
4. **Updates** - Update workflows as requirements change
5. **Backup** - Backup scheduler configuration regularly

## 🎉 **Summary**

The El Jefe workflow scheduler transforms manual tasks into automated, reliable processes. With flexible scheduling options, comprehensive management tools, and seamless integration with the orchestrator, you can create sophisticated automation workflows that save time and improve consistency.

**Key Benefits:**
- ✅ **Automation** - Eliminate manual repetitive tasks
- ✅ **Reliability** - Consistent execution with error handling
- ✅ **Flexibility** - Multiple scheduling options and configurations
- ✅ **Monitoring** - Complete visibility into workflow status
- ✅ **Integration** - Works seamlessly with existing El Jefe features

Start automating your workflows today and let El Jefe handle the repetitive work while you focus on what matters most! 🚀