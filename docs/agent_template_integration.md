# Agent Template System Integration Guide

This guide explains how to use the agent template system to create and manage specialized agents for the el-jefe AI Orchestrator.

## Overview

The agent template system provides a structured approach to creating new agents with:
- Standardized configuration format
- Built-in documentation generation
- Quality assurance checks
- Example-driven development
- Validation and testing scenarios

## Quick Start

### 1. Using Existing Templates

```python
from src.templated_agent_manager import TemplatedAgentManager
from pathlib import Path

# Initialize templated manager
manager = TemplatedAgentManager(Path("your_workspace"))

# List available templates
templates = manager.list_available_templates()
print(templates)

# Get template recommendations for a task
recommendations = manager.get_template_recommendations("Analyze sales data for trends")
for rec in recommendations:
    print(f"{rec['template']}: {rec['score']} - {rec['match_reasons']}")

# Spawn agent from template
result = await manager.spawn_templated_agent(
    template_name="data_scientist",
    task_description="Analyze quarterly sales data",
    context_files=["sales_data.csv"],
    output_file="sales_analysis.md"
)
```

### 2. Creating a Custom Agent

#### Option A: Interactive Wizard

```bash
# Run the interactive agent creation wizard
python scripts/create_agent.py

# List existing templates
python scripts/create_agent.py list
```

#### Option B: Programmatic Creation

```python
from src.agent_template import AgentTemplate, AgentCapabilities, ExpertiseLevel

# Create a custom agent template
template = AgentTemplate(
    name="Marketing Strategist",
    agent_type="marketing_strategist",
    description="Specializes in creating marketing strategies and campaigns",
    category="creation",
    expertise_level=ExpertiseLevel.ADVANCED,
    system_prompt="""You are a marketing strategist with expertise in digital marketing,
brand positioning, and campaign development...""",
    allowed_tools=["read_files", "write_md", "search_web", "analyze_data"],
    max_turns=8,
    capabilities=AgentCapabilities(
        primary_tasks=[
            "Marketing strategy development",
            "Campaign planning",
            "Brand analysis"
        ],
        secondary_tasks=[
            "Content strategy",
            "Market research",
            "Performance tracking"
        ]
    ),
    domain_expertise=[
        "Digital marketing",
        "Social media marketing",
        "SEO/SEM",
        "Content marketing",
        "Brand strategy"
    ]
)

# Register the agent
manager.register_custom_agent(template)

# Or save to file
from src.agent_template import save_template
save_template(template, "custom_agents/marketing_strategist.json")
```

### 3. Using Templates with Streaming Orchestrator

```python
from src.streaming_orchestrator import StreamingOrchestrator
from src.templated_agent_manager import TemplatedAgentManager

# Initialize both systems
orchestrator = StreamingOrchestrator(enable_streaming=True)
manager = TemplatedAgentManager(Path("workspace"))

# Use template to configure agent
agent_config = manager.create_agent_from_template(
    "security_analyst",
    customizations={
        "max_turns": 10,
        "allowed_tools": ["read_files", "write_md", "scan_vulnerabilities"]
    }
)

# Execute with streaming
async for update in orchestrator.execute_goal_streaming(
    "Perform security audit on the application",
    enable_parallel=True
):
    print(f"Update: {update['type']} - {update.get('content', '')}")
```

## Advanced Features

### 1. Template Validation

```python
from src.agent_template import validate_agent_template

# Validate template before registration
issues = validate_agent_template(template)
if issues:
    print("Validation issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Template is valid!")
```

### 2. Custom Tool Integration

```python
# Define custom tools for your agent
custom_tools = [
    "analyze_sentiment",
    "generate_chart",
    "export_to_powerbi"
]

# Create template with custom tools
template = AgentTemplate(
    name="Data Visualizer",
    agent_type="data_visualizer",
    allowed_tools=["read_files", "write_md"] + custom_tools,
    # ... other configuration
)
```

### 3. Template Inheritance

```python
# Create a base template
base_analyst_template = AgentTemplate(
    name="Base Analyst",
    agent_type="base_analyst",
    category="analysis",
    # ... base configuration
)

# Create specialized templates by extending base
security_analyst_template = AgentTemplate(
    **base_analyst_template.__dict__,
    name="Security Analyst",
    agent_type="security_analyst",
    domain_expertise=base_analyst_template.domain_expertise + [
        "Penetration testing",
        "Vulnerability assessment",
        "Security compliance"
    ]
)
```

## Best Practices

### 1. Template Design

- **Clear Scope**: Define specific, focused capabilities
- **Good Prompts**: Provide detailed system prompts with examples
- **Proper Tools**: Only include tools the agent actually needs
- **Validation**: Always include validation checks
- **Documentation**: Provide comprehensive examples

### 2. Agent Configuration

```python
# Good: Specific system prompt
system_prompt = """You are a financial analyst specializing in startup valuation.

Your responsibilities:
1. Analyze financial statements
2. Calculate valuation multiples
3. Compare with industry benchmarks
4. Provide actionable insights

Always provide:
- Clear numerical calculations
- Industry comparisons
- Risk factors
- Investment recommendations"""

# Bad: Vague system prompt
system_prompt = "You are an analyst. Analyze things."
```

### 3. Error Handling

```python
try:
    result = await manager.spawn_templated_agent(
        template_name="custom_agent",
        task_description="Execute task",
        output_file="result.md"
    )

    # Validate execution
    validation = await manager.validate_agent_execution(
        result["agent_id"],
        validation_type="comprehensive"
    )

    if validation["issues_found"]:
        print("⚠️ Issues found during execution:")
        for issue in validation["issues_found"]:
            print(f"  - {issue}")

except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Execution error: {e}")
```

## Migration Guide

### From AgentManager to TemplatedAgentManager

```python
# Old approach
from src.agent_manager import AgentManager, AgentType

manager = AgentManager(workspace_path)
result = await manager.spawn_agent(
    agent_type=AgentType.RESEARCHER,
    task_description="Research topic",
    output_file="research.md"
)

# New approach
from src.templated_agent_manager import TemplatedAgentManager

manager = TemplatedAgentManager(workspace_path)

# Use built-in template
result = await manager.spawn_templated_agent(
    template_name="researcher",
    task_description="Research topic",
    output_file="research.md"
)

# Or create custom agent
template = AgentTemplate(...)
manager.register_custom_agent(template)
result = await manager.spawn_templated_agent(
    template_name="custom_agent",
    task_description="Execute task"
)
```

## Example: Complete Workflow

Here's a complete example of creating and using a custom agent:

```python
import asyncio
from pathlib import Path

async def custom_agent_workflow():
    """Complete workflow with custom agent creation and usage."""

    # 1. Initialize manager
    manager = TemplatedAgentManager(Path("workspace"))

    # 2. Create custom agent template
    template = AgentTemplate(
        name="DevOps Engineer",
        agent_type="devops_engineer",
        description="Specializes in CI/CD pipeline setup and infrastructure automation",
        category="creation",
        expertise_level=ExpertiseLevel.ADVANCED,
        system_prompt="""You are a DevOps engineer with expertise in:
- CI/CD pipeline design and implementation
- Infrastructure as Code (IaC)
- Container orchestration
- Monitoring and logging
- Cloud platform automation

Always provide:
1. Clear implementation steps
2. Configuration examples
3. Security considerations
4. Best practices""",
        allowed_tools=["read_files", "write_md", "write_file", "analyze_config"],
        max_turns=8,
        capabilities=AgentCapabilities(
            primary_tasks=[
                "CI/CD pipeline setup",
                "Infrastructure automation",
                "Deployment strategies"
            ],
            tools_used=["Docker", "Kubernetes", "Terraform", "Jenkins", "GitHub Actions"]
        ),
        domain_expertise=[
            "DevOps principles",
            "Microservices architecture",
            "Cloud platforms (AWS, GCP, Azure)",
            "Container orchestration",
            "Infrastructure as Code"
        ],
        examples=[
            AgentExample(
                title="Setup CI/CD for Node.js App",
                description="Create GitHub Actions workflow for Node.js deployment",
                input_example="Setup automated testing and deployment for my Node.js API",
                expected_output="Complete GitHub Actions workflow with testing, building, and deployment steps"
            )
        ]
    )

    # 3. Register the agent
    manager.register_custom_agent(template)

    # 4. Get recommendations
    recommendations = manager.get_template_recommendations(
        "Setup CI/CD pipeline for Python web application"
    )
    print("Recommended agents:", recommendations)

    # 5. Execute task with custom agent
    result = await manager.spawn_templated_agent(
        template_name="devops_engineer",
        task_description="Create a complete CI/CD pipeline for a Django application with Docker deployment",
        context_files=["requirements.txt", "Dockerfile"],
        output_file="cicd_setup.md"
    )

    # 6. Validate execution
    validation = await manager.validate_agent_execution(result["agent_id"])
    print("Validation result:", validation)

    # 7. Generate documentation
    docs = manager.generate_agent_docs("devops_engineer")
    with open("devops_engineer_docs.md", "w") as f:
        f.write(docs)

    return result

# Run the workflow
result = asyncio.run(custom_agent_workflow())
```

## Troubleshooting

### Common Issues

1. **Template not found**: Ensure template is registered or JSON file exists
2. **Validation errors**: Check all required fields are present and valid
3. **Tool not available**: Verify tools are implemented in your environment
4. **Execution timeout**: Adjust max_turns or timeout settings

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug information
manager = TemplatedAgentManager(workspace_path)
templates = manager.list_available_templates()
print("Available templates:", templates)
```

## Contributing

To contribute new templates:

1. Create template following the established patterns
2. Include comprehensive examples and validation
3. Test thoroughly with various scenarios
4. Submit documentation and examples
5. Follow code style guidelines

For more information, see the [Developer Guide](developer-guide.md).