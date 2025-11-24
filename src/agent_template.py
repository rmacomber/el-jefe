"""
Agent Template System for el-jefe

Provides a structured way to create new specialized agents with
built-in documentation, examples, and quality assurance.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import json
from datetime import datetime


class ExpertiseLevel(Enum):
    """Agent expertise levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class AgentCapabilities:
    """Defines what an agent can do."""
    primary_tasks: List[str]
    secondary_tasks: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)


@dataclass
class AgentExample:
    """Example usage for an agent."""
    title: str
    description: str
    input_example: str
    expected_output: str
    context_files: List[str] = field(default_factory=list)


@dataclass
class AgentTemplate:
    """Template for creating new specialized agents."""

    # Core Identity
    name: str
    agent_type: str  # Must match AgentType enum
    description: str
    category: str  # "analysis", "creation", "validation", "coordination"
    expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE

    # System Configuration
    system_prompt: str
    allowed_tools: List[str]
    max_turns: int = 6
    timeout_seconds: int = 300

    # Capabilities and Boundaries
    capabilities: AgentCapabilities
    domain_expertise: List[str] = field(default_factory=list)
    out_of_scope: List[str] = field(default_factory=list)

    # Documentation and Examples
    examples: List[AgentExample] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    common_pitfalls: List[str] = field(default_factory=list)

    # Quality Assurance
    validation_checks: List[str] = field(default_factory=list)
    testing_scenarios: List[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)


# Pre-defined templates for existing agents
AGENT_TEMPLATES = {
    "security_analyst": AgentTemplate(
        name="Security Analyst",
        agent_type="security_analyst",
        description="Specializes in security assessment, vulnerability analysis, and threat detection",
        category="validation",
        expertise_level=ExpertiseLevel.EXPERT,
        system_prompt="""You are a security analyst with expertise in identifying vulnerabilities, assessing risks, and implementing security best practices.

Your responsibilities:
- Analyze code and systems for security vulnerabilities
- Recommend security improvements
- Ensure compliance with security standards
- Identify potential attack vectors
- Provide actionable security recommendations

Always provide:
1. Risk level (Critical/High/Medium/Low)
2. Detailed explanation of vulnerabilities
3. Specific remediation steps
4. Prevention recommendations""",
        allowed_tools=["read_files", "write_md", "search_web", "analyze_code", "validate_security"],
        max_turns=8,
        capabilities=AgentCapabilities(
            primary_tasks=[
                "Security vulnerability assessment",
                "Threat modeling",
                "Security code review",
                "Compliance checking"
            ],
            secondary_tasks=[
                "Security documentation",
                "Risk assessment reports",
                "Security architecture review"
            ],
            tools_used=["static analysis", "dynamic analysis", "security scanners"],
            limitations=[
                "Cannot execute code for testing",
                "Relies on provided code and documentation",
                "Cannot access external security databases in real-time"
            ]
        ),
        domain_expertise=[
            "OWASP Top 10",
            "CVE vulnerabilities",
            "Security frameworks (NIST, ISO 27001)",
            "Encryption and authentication",
            "Network security",
            "Application security"
        ],
        out_of_scope=[
            "Penetration testing (requires execution)",
            "Live system monitoring",
            "Incident response (real-time)",
            "Forensic analysis"
        ],
        examples=[
            AgentExample(
                title="Web Application Security Review",
                description="Review a web application for security vulnerabilities",
                input_example="Analyze this Flask application for security issues",
                expected_output="Detailed security report with vulnerabilities and remediation steps",
                context_files=["app.py", "requirements.txt", "config.py"]
            ),
            AgentExample(
                title="Infrastructure Security Assessment",
                description="Assess cloud infrastructure configuration",
                input_example="Review these AWS CloudFormation templates for security misconfigurations",
                expected_output="Security findings report with specific recommendations"
            )
        ],
        best_practices=[
            "Always prioritize vulnerabilities by risk level",
            "Provide specific, actionable remediation steps",
            "Consider the principle of least privilege",
            "Reference industry standards (OWASP, NIST)",
            "Suggest automated testing where possible"
        ],
        validation_checks=[
            "Verify all findings have clear risk ratings",
            "Ensure remediation steps are specific and actionable",
            "Check that all high-risk issues are highlighted",
            "Validate that recommendations follow security best practices"
        ],
        testing_scenarios=[
            "Input validation testing",
            "Authentication and authorization testing",
            "Error handling and information disclosure",
            "Cryptographic storage validation",
            "Configuration security review"
        ],
        tags=["security", "vulnerability", "compliance", "risk-assessment"]
    ),

    "data_scientist": AgentTemplate(
        name="Data Scientist",
        agent_type="data_scientist",
        description="Specializes in data analysis, machine learning, and statistical modeling",
        category="analysis",
        expertise_level=ExpertiseLevel.EXPERT,
        system_prompt="""You are a data scientist with expertise in statistical analysis, machine learning, and data visualization.

Your responsibilities:
- Analyze datasets and extract insights
- Build and evaluate machine learning models
- Create visualizations and reports
- Provide statistical interpretations
- Recommend data-driven decisions

Always provide:
1. Clear methodology explanations
2. Statistical significance testing where appropriate
3. Limitations and assumptions
4. Actionable insights and recommendations""",
        allowed_tools=["read_files", "write_md", "analyze_data", "create_visualizations", "write_file"],
        max_turns=10,
        capabilities=AgentCapabilities(
            primary_tasks=[
                "Exploratory data analysis",
                "Statistical modeling",
                "Machine learning pipeline development",
                "Data visualization"
            ],
            secondary_tasks=[
                "Feature engineering",
                "Model evaluation and validation",
                "A/B testing design",
                "Predictive analytics"
            ],
            tools_used=["pandas", "numpy", "scikit-learn", "matplotlib", "seaborn"],
            limitations=[
                "Cannot execute code directly",
                "Limited by provided dataset size",
                "Cannot access external data sources"
            ]
        ),
        domain_expertise=[
            "Statistical analysis",
            "Machine learning algorithms",
            "Data visualization",
            "Experimental design",
            "Feature engineering",
            "Model validation"
        ],
        examples=[
            AgentExample(
                title="Customer Churn Prediction",
                description="Build a model to predict customer churn",
                input_example="Analyze this customer dataset and build a churn prediction model",
                expected_output="Complete analysis with model code, evaluation metrics, and insights"
            ),
            AgentExample(
                title="Sales Trend Analysis",
                description="Analyze sales data to identify trends and patterns",
                input_example="Perform exploratory analysis on quarterly sales data",
                expected_output="Comprehensive report with visualizations and statistical insights"
            )
        ],
        best_practices=[
            "Always validate assumptions about data",
            "Use appropriate statistical tests",
            "Visualize data before modeling",
            "Document all data preprocessing steps",
            "Consider model interpretability"
        ],
        validation_checks=[
            "Verify statistical test appropriateness",
            "Check for data leakage",
            "Ensure proper train/test splits",
            "Validate model assumptions"
        ],
        tags=["data-science", "machine-learning", "statistics", "analytics"]
    ),

    "api_developer": AgentTemplate(
        name="API Developer",
        agent_type="api_developer",
        description="Specializes in designing, building, and documenting RESTful APIs",
        category="creation",
        expertise_level=ExpertiseLevel.ADVANCED,
        system_prompt="""You are an API developer specializing in RESTful API design, implementation, and documentation.

Your responsibilities:
- Design clean, intuitive API endpoints
- Implement proper HTTP methods and status codes
- Create comprehensive API documentation
- Ensure API security and performance
- Follow RESTful best practices

Always provide:
1. Clear API specifications
2. Proper error handling
3. Authentication and authorization
4. Rate limiting considerations
5. Comprehensive documentation""",
        allowed_tools=["read_files", "write_file", "write_md", "test_code", "validate_schema"],
        max_turns=8,
        capabilities=AgentCapabilities(
            primary_tasks=[
                "RESTful API design",
                "Endpoint implementation",
                "API documentation",
                "Authentication integration"
            ],
            secondary_tasks=[
                "API testing",
                "Performance optimization",
                "Versioning strategy",
                "SDK generation"
            ],
            tools_used=["FastAPI", "Flask", "Django REST", "OpenAPI", "Postman"],
            limitations=[
                "Cannot deploy APIs",
                "Cannot perform load testing",
                "Limited to provided specifications"
            ]
        ),
        domain_expertise=[
            "RESTful principles",
            "OpenAPI specification",
            "JWT authentication",
            "OAuth 2.0",
            "GraphQL",
            "API gateway patterns"
        ],
        examples=[
            AgentExample(
                title="E-commerce API Design",
                description="Design a RESTful API for an e-commerce platform",
                input_example="Create API endpoints for products, orders, and users",
                expected_output="Complete API specification with OpenAPI documentation"
            ),
            AgentExample(
                title="Authentication Service",
                description="Implement secure authentication endpoints",
                input_example="Build login, register, and token refresh endpoints",
                expected_output="Secure implementation with JWT tokens"
            )
        ],
        best_practices=[
            "Use appropriate HTTP methods",
            "Implement proper status codes",
            "Version your APIs",
            "Document all endpoints",
            "Implement rate limiting"
        ],
        validation_checks=[
            "Verify RESTful principles compliance",
            "Check authentication implementation",
            "Validate error handling",
            "Review documentation completeness"
        ],
        tags=["api", "rest", "backend", "authentication"]
    )
}


def create_agent_from_template(template: AgentTemplate) -> Dict[str, Any]:
    """Convert template to agent configuration format."""
    return {
        "system_prompt": template.system_prompt,
        "allowed_tools": template.allowed_tools,
        "max_turns": template.max_turns,
        "description": template.description,
        "category": template.category,
        "capabilities": {
            "primary": template.capabilities.primary_tasks,
            "secondary": template.capabilities.secondary_tasks,
            "tools": template.capabilities.tools_used,
            "limitations": template.capabilities.limitations
        },
        "domain_expertise": template.domain_expertise,
        "out_of_scope": template.out_of_scope,
        "examples": [
            {
                "title": ex.title,
                "description": ex.description,
                "input": ex.input_example,
                "output": ex.expected_output,
                "context": ex.context_files
            }
            for ex in template.examples
        ]
    }


def validate_agent_template(template: AgentTemplate) -> List[str]:
    """Validate agent template and return list of issues."""
    issues = []

    # Check required fields
    if not template.name:
        issues.append("Name is required")
    if not template.agent_type:
        issues.append("Agent type is required")
    if not template.system_prompt:
        issues.append("System prompt is required")
    if not template.allowed_tools:
        issues.append("At least one tool must be specified")

    # Check system prompt quality
    if len(template.system_prompt) < 100:
        issues.append("System prompt should be more detailed")

    # Check for examples
    if not template.examples:
        issues.append("Add at least one example for better usability")

    # Check validation checks
    if not template.validation_checks:
        issues.append("Add validation checks for quality assurance")

    return issues


def generate_agent_documentation(template: AgentTemplate) -> str:
    """Generate comprehensive documentation for an agent."""
    doc = f"""# {template.name} Agent

## Overview
{template.description}

**Category:** {template.category}
**Expertise Level:** {template.expertise_level.value}
**Version:** {template.version}

## Capabilities

### Primary Tasks
{chr(10).join(f"- {task}" for task in template.capabilities.primary_tasks)}

### Secondary Tasks
{chr(10).join(f"- {task}" for task in template.capabilities.secondary_tasks)}

### Tools Used
{chr(10).join(f"- {tool}" for tool in template.capabilities.tools_used)}

### Limitations
{chr(10).join(f"- {limitation}" for limitation in template.capabilities.limitations)}

## Domain Expertise
{chr(10).join(f"- {domain}" for domain in template.domain_expertise)}

## Out of Scope
{chr(10).join(f"- {scope}" for scope in template.out_of_scope)}

## Configuration
- **Max Turns:** {template.max_turns}
- **Timeout:** {template.timeout_seconds} seconds
- **Allowed Tools:** {', '.join(template.allowed_tools)}

## Examples

"""

    for i, example in enumerate(template.examples, 1):
        doc += f"""### Example {i}: {example.title}

{example.description}

**Input:**
```python
{example.input_example}
```

**Expected Output:**
{example.expected_output}

"""
        if example.context_files:
            doc += f"**Context Files:** {', '.join(example.context_files)}\n\n"

    if template.best_practices:
        doc += """## Best Practices
"""
        doc += chr(10).join(f"- {practice}" for practice in template.best_practices)
        doc += "\n\n"

    if template.common_pitfalls:
        doc += """## Common Pitfalls to Avoid
"""
        doc += chr(10).join(f"- {pitfall}" for pitfall in template.common_pitfalls)
        doc += "\n\n"

    if template.validation_checks:
        doc += """## Quality Assurance Checklist
"""
        doc += chr(10).join(f"- [ ] {check}" for check in template.validation_checks)
        doc += "\n\n"

    if template.testing_scenarios:
        doc += """## Recommended Testing Scenarios
"""
        doc += chr(10).join(f"- {scenario}" for scenario in template.testing_scenarios)
        doc += "\n\n"

    if template.tags:
        doc += f"""## Tags
{', '.join(f'`{tag}`' for tag in template.tags)}
"""

    return doc


def save_template(template: AgentTemplate, filepath: str):
    """Save agent template as JSON file."""
    with open(filepath, 'w') as f:
        json.dump(template.__dict__, f, indent=2, default=str)


def load_template(filepath: str) -> AgentTemplate:
    """Load agent template from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Convert back to dataclass
    return AgentTemplate(**data)