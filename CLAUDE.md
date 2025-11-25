# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

El Jefe is a comprehensive AI Agent Monitoring Dashboard and orchestration system that provides real-time monitoring, management, and coordination of multiple AI agents. The system has evolved from a simple orchestrator SDK into a production-ready dashboard platform with web-based monitoring, comprehensive testing suites, and modern frontend capabilities.

### Core Features
- **Real-time Monitoring Dashboard**: WebSocket-based live monitoring of agent jobs and workflows
- **Multi-Agent Coordination**: Orchestrates specialized AI agents for various tasks
- **Comprehensive Testing Suite**: Full testing framework with unit, E2E, performance, and security tests
- **Modern Frontend**: React/TypeScript starter kit with Material-UI components
- **Production Ready**: Docker deployment, SSL support, and security hardening
- **Claude Code Integration**: Slash commands for easy testing and validation

## Core Architecture

### Main Components

1. **Monitoring Dashboard** (`monitoring_dashboard.py`) - Main aiohttp-based web server
   - Real-time WebSocket monitoring and updates
   - RESTful API for agent and workflow management
   - Authentication and security middleware
   - File upload and chat interface capabilities
   - Mobile-responsive design

2. **Agent System** - Specialized AI agents for different domains
   - Research Agent: Web research and information gathering
   - Writer Agent: Content creation and script writing
   - Coder Agent: Code generation and development tasks
   - Additional agents can be added following the established pattern

3. **Frontend Implementations** - Multiple dashboard versions available
   - `static/index.html` - Main HTML/CSS/JS dashboard (v1)
   - `static/v2.html` - Enhanced dashboard with advanced features
   - `static/charts.html` - Analytics and data visualization dashboard
   - `frontend-starter/` - Modern React/TypeScript implementation

4. **Testing Framework** - Comprehensive test suite
   - Unit tests for API endpoints
   - End-to-end browser automation with Playwright
   - Performance and load testing with Locust
   - Security validation and cross-browser testing

## Development Commands

### Starting the Dashboard

```bash
# Start the main monitoring dashboard (default port 8080)
python monitoring_dashboard.py

# Start with custom configuration
python monitoring_dashboard.py --host 0.0.0.0 --port 8080 --password your_password

# Start with SSL/HTTPS
python monitoring_dashboard.py --ssl --cert-path /path/to/cert.pem --key-path /path/to/key.pem
```

### Environment Setup

```bash
# Install required dependencies
pip install -r requirements.txt

# Install testing dependencies
pip install pytest playwright locust

# Install Playwright browsers (required for E2E tests)
playwright install

# Install frontend dependencies (if using React starter)
cd frontend-starter && npm install
```

### Claude Code Testing Commands

The project includes specialized Claude Code slash commands for easy testing:

```bash
# Quick validation of testing setup
/test-validation

# Run all tests
/test-all

# Run specific test types
/test-unit
/test-e2e
/test-performance
/test-security
/test-cross-browser

# Generate test report
/test-report
```

### Manual Testing

```bash
# Run basic setup validation
pytest tests/test_basic.py -v

# Run full test suite (requires dashboard running on localhost:8080)
python3 tests/run_tests.py --test-type all

# Individual test types
python3 tests/run_tests.py --test-type unit      # Unit tests only
python3 tests/run_tests.py --test-type e2e       # End-to-end browser tests
python3 tests/run_tests.py --test-type performance  # Performance/load testing
python3 tests/run_tests.py --test-type security   # Security validation
```

### Load Testing

```bash
# Performance testing with Locust
locust -f tests/locustfile.py --headless --users 20 --run-time 60s --host http://localhost:8080

# Interactive web interface for load testing
locust -f tests/locustfile.py --host http://localhost:8080
# Visit http://localhost:8089 for web interface
```

### Frontend Development

```bash
# Start React frontend development server
cd frontend-starter
npm run dev

# Build for production
npm run build

# Run frontend tests
npm test
```

## Project Structure

```
el-jefe-dashboard/
├── monitoring_dashboard.py          # Main dashboard server (aiohttp)
├── requirements.txt                 # Python dependencies
├── config/                         # Configuration files
│   ├── nginx.conf                  # Nginx configuration
│   └── ssl/                        # SSL certificates
├── static/                         # Static web assets
│   ├── index.html                  # Main dashboard (v1)
│   ├── v2.html                     # Enhanced dashboard
│   ├── charts.html                 # Analytics dashboard
│   ├── advanced.html               # Advanced features
│   ├── logs.html                   # Logs viewer
│   ├── css/                        # Stylesheets
│   └── js/                         # JavaScript files
├── tests/                          # Comprehensive test suite
│   ├── test_basic.py               # Basic validation tests
│   ├── test_dashboard_functionality.py  # Unit tests
│   ├── test_end_to_end.py          # E2E browser tests
│   ├── test_performance.py         # Performance tests
│   ├── test_security.py            # Security tests
│   ├── locustfile.py               # Load testing
│   └── run_tests.py                # Test runner script
├── frontend-starter/               # React/TypeScript frontend
│   ├── src/                        # React source code
│   ├── package.json                # NPM dependencies
│   └── vite.config.ts              # Vite configuration
├── scripts/                        # Utility scripts
├── .claude/commands/               # Claude Code slash commands
│   ├── test-validation.md          # Quick validation command
│   ├── test-all.md                 # Run all tests
│   ├── test-unit.md                # Unit tests
│   ├── test-e2e.md                 # E2E tests
│   ├── test-performance.md         # Performance tests
│   └── test-security.md            # Security tests
└── agents/                         # AI agent implementations
    ├── researcher_agent.py         # Research specialization
    ├── writer_agent.py             # Content creation
    └── coder_agent.py              # Code generation
```

## Agent Configuration

### Research Agent
- **Purpose**: Web research, information gathering, and data synthesis
- **Tools**: Web search, data extraction, note organization
- **Max Turns**: 8 (configurable)
- **Output**: Structured research notes with citations

### Writer Agent
- **Purpose**: Content creation, script writing, documentation
- **Tools**: Text generation, formatting, style adaptation
- **Max Turns**: 6 (configurable)
- **Input**: Research notes from researcher agent
- **Output**: Polished content in various formats

### Coder Agent
- **Purpose**: Code generation, development tasks, utilities
- **Tools**: Code generation, documentation, testing
- **Max Turns**: 5 (configurable)
- **Input**: Content specifications and requirements
- **Output**: Production-ready code with documentation

## API Endpoints

### Authentication
- `POST /api/login` - Authenticate with dashboard
- `POST /api/logout` - End current session

### Agent Management
- `GET /api/agents` - List all available agents
- `GET /api/agents/{id}/status` - Get agent status
- `POST /api/agents/{id}/execute` - Execute agent task

### Workflow Management
- `GET /api/workflows` - List all workflows
- `POST /api/workflows` - Create new workflow
- `GET /api/workflows/{id}/status` - Get workflow status
- `POST /api/workflows/{id}/pause` - Pause workflow execution
- `POST /api/workflows/{id}/resume` - Resume paused workflow

### Monitoring
- `GET /api/jobs` - List all agent jobs
- `WebSocket /ws` - Real-time updates and notifications

### Chat Interface
- `POST /api/chat` - Send message to El Jefe
- `POST /api/upload` - Upload files for processing

## Testing Framework

### Test Coverage Areas
- **API Testing**: All REST endpoints with validation
- **Authentication**: Login, logout, session management
- **Workflow Execution**: End-to-end workflow testing
- **Real-time Updates**: WebSocket functionality
- **Cross-browser**: Chrome, Firefox, Safari, Edge
- **Mobile**: Responsive design on various devices
- **Performance**: Load testing up to 100 concurrent users
- **Security**: XSS, CSRF, SQL injection prevention
- **Accessibility**: WCAG 2.1 AA compliance

### Test Requirements
- Dashboard running on http://localhost:8080
- Default credentials: eljefe_admin (auto-configured)
- Testing dependencies: pytest, playwright, locust
- Browsers installed via `playwright install`

## Deployment

### Development
```bash
# Start development server
python monitoring_dashboard.py --dev

# Enable debug logging
export LOG_LEVEL=DEBUG
python monitoring_dashboard.py
```

### Production with Docker
```bash
# Build Docker image
docker build -t el-jefe-dashboard .

# Run with Docker Compose
docker-compose up -d

# Or run standalone
docker run -p 8080:8080 el-jefe-dashboard
```

### Production with SSL
```bash
# Generate SSL certificates (Let's Encrypt recommended)
certbot certonly --webroot -w /var/www/html -d your-domain.com

# Start with SSL
python monitoring_dashboard.py --ssl \
  --cert-path /etc/letsencrypt/live/your-domain.com/fullchain.pem \
  --key-path /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### Using Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/el-jefe
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Security Features

- **Authentication**: Password-based with session management
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Request throttling to prevent abuse
- **HTTPS Support**: SSL/TLS encryption for production
- **Security Headers**: OWASP recommended headers
- **File Upload Security**: Type and size validation

## Adding New Agents

New agents should follow the established pattern:

```python
async def run_<agent>_agent(task: str, context: Dict, output_path: str):
    """
    Execute agent-specific task with provided context.

    Args:
        task: Task description for the agent
        context: Additional context and configuration
        output_path: Path to save agent output

    Returns:
        Dict containing agent results and metadata
    """
    # 1. Parse and validate input
    # 2. Initialize agent with appropriate tools
    # 3. Execute the task with error handling
    # 4. Save results to output_path
    # 5. Return execution summary

    pass
```

### Agent Registration
```python
# Register new agent in monitoring_dashboard.py
AVAILABLE_AGENTS = {
    "researcher": run_researcher_agent,
    "writer": run_writer_agent,
    "coder": run_coder_agent,
    "new_agent": run_new_agent,  # Add your agent here
}
```

## Monitoring and Logging

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General information about system operation
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures

### Monitoring Metrics
- Active agent jobs and status
- Workflow execution times
- System resource usage
- API request/response times
- WebSocket connection status
- Error rates and types

## Troubleshooting

### Common Issues

1. **Dashboard won't start**
   - Check if port 8080 is available
   - Verify all dependencies are installed
   - Check Python version (3.8+ required)

2. **Tests failing**
   - Ensure dashboard is running on localhost:8080
   - Install Playwright browsers: `playwright install`
   - Check test configuration in tests/conftest.py

3. **WebSocket connection issues**
   - Check firewall settings
   - Verify CORS configuration
   - Ensure WebSocket upgrade headers are properly forwarded

4. **Performance issues**
   - Monitor memory usage with large workloads
   - Consider increasing WebSocket connection limits
   - Use Redis for session storage in production

### Debug Mode
```bash
# Enable comprehensive debug logging
export EL_JEFE_DEBUG=1
export LOG_LEVEL=DEBUG
python monitoring_dashboard.py --dev
```

## Contributing

### Code Style
- Python: Follow PEP 8, use Black for formatting
- JavaScript/TypeScript: Use ESLint and Prettier
- All code should have appropriate tests

### Testing
- Write unit tests for new functionality
- Add E2E tests for UI changes
- Verify cross-browser compatibility
- Update documentation

### Security
- Follow secure coding practices
- Validate all inputs
- Use parameterized queries
- Keep dependencies updated

## Integration with Claude Code

This project is optimized for Claude Code with specialized commands:

- `/test-validation` - Quick test setup validation
- `/test-all` - Run comprehensive test suite
- `/test-unit` - Unit tests only
- `/test-e2e` - End-to-end browser tests
- `/test-performance` - Load and performance testing
- `/test-security` - Security validation tests
- `/test-cross-browser` - Multi-browser compatibility
- `/test-report` - Generate comprehensive test report

These commands provide instant access to testing capabilities and streamline the development workflow when using Claude Code.