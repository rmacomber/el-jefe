"""
Enhanced Agent Template System for El Jefe

Provides structured agent creation with built-in validation, documentation,
and pre-built templates for common agent types. Integrates seamlessly with
the existing AgentManager and StreamingAgentManager architecture.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import aiofiles
from enum import Enum

from agent_manager import AgentType, AgentConfig
from enhanced_agent_manager import StreamingAgentManager, StreamingAgentOptions


class AgentDomain(Enum):
    """Standardized agent domains for template categorization."""
    SECURITY = "security"
    DEVELOPMENT = "development"
    DATA_SCIENCE = "data_science"
    RESEARCH = "research"
    DESIGN = "design"
    TESTING = "testing"
    PERFORMANCE = "performance"
    DEVOPS = "devops"
    ANALYSIS = "analysis"
    WRITING = "writing"


@dataclass
class AgentTemplate:
    """Structured template for creating specialized agents."""
    name: str
    domain: AgentDomain
    description: str
    system_prompt: str
    allowed_tools: List[str]
    max_turns: int
    expertise_areas: List[str]
    use_cases: List[str]
    code_examples: Dict[str, str] = field(default_factory=dict)
    best_practices: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTemplate':
        """Create template from dictionary."""
        data['domain'] = AgentDomain(data['domain'])
        return cls(**data)


@dataclass
class TemplateValidation:
    """Results of template validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class TemplateRegistry:
    """Registry for managing agent templates."""

    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or Path("templates/agents")
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, AgentTemplate] = {}
        self._load_builtin_templates()
        self._load_custom_templates()

    def _load_builtin_templates(self):
        """Load built-in agent templates."""
        self.register_template(self._create_security_analyst_template())
        self.register_template(self._create_data_scientist_template())
        self.register_template(self._create_api_developer_template())

    def _load_custom_templates(self):
        """Load custom templates from file system."""
        for template_file in self.template_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)
                    template = AgentTemplate.from_dict(data)
                    self.templates[template.name] = template
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

    def register_template(self, template: AgentTemplate):
        """Register a new agent template."""
        self.templates[template.name] = template

    def get_template(self, name: str) -> Optional[AgentTemplate]:
        """Get a template by name."""
        return self.templates.get(name)

    def list_templates(self, domain: Optional[AgentDomain] = None) -> List[str]:
        """List available templates, optionally filtered by domain."""
        if domain:
            return [name for name, template in self.templates.items()
                   if template.domain == domain]
        return list(self.templates.keys())

    def validate_template(self, template: AgentTemplate) -> TemplateValidation:
        """Validate an agent template."""
        validation = TemplateValidation(is_valid=True)

        # Check required fields
        if not template.name:
            validation.errors.append("Template name is required")
            validation.is_valid = False

        if not template.system_prompt:
            validation.errors.append("System prompt is required")
            validation.is_valid = False

        if not template.allowed_tools:
            validation.warnings.append("No tools specified - agent may be limited")

        if template.max_turns <= 0:
            validation.errors.append("Max turns must be positive")
            validation.is_valid = False

        # Check prompt quality
        if len(template.system_prompt) < 100:
            validation.warnings.append("System prompt seems short - consider more detail")

        # Check for common tools
        common_tools = {"search_web", "write_md", "read_files", "analyze_code"}
        if not any(tool in template.allowed_tools for tool in common_tools):
            validation.suggestions.append("Consider adding common tools like 'search_web' or 'write_md'")

        return validation

    def _create_security_analyst_template(self) -> AgentTemplate:
        """Create security analyst agent template."""
        return AgentTemplate(
            name="security_analyst",
            domain=AgentDomain.SECURITY,
            description="Specialized agent for security analysis, vulnerability assessment, and security best practices implementation",
            system_prompt="""You are a Security Analyst specializing in application security, vulnerability assessment, and security best practices.

Your core expertise areas:
- **Threat Assessment**: Identifying potential security vulnerabilities and attack vectors
- **Security Implementation**: Applying security best practices and defensive measures
- **Compliance Standards**: Ensuring adherence to security standards (OWASP, NIST, industry-specific)
- **Security Testing**: Performing security reviews and penetration testing guidance

## Security Analysis Process
1. **Scope Definition**: Identify assets, threats, and security requirements
2. **Vulnerability Assessment**: Analyze code/systems for security weaknesses
3. **Risk Evaluation**: Assess impact and likelihood of identified vulnerabilities
4. **Remediation Planning**: Provide actionable security improvement recommendations
5. **Implementation Guidance**: Offer specific code examples and configuration changes

## Security Best Practices to Apply
- Input validation and sanitization
- Authentication and authorization mechanisms
- Data encryption and protection
- Secure error handling and logging
- Security headers and HTTPS implementation
- Regular security updates and patching

## Deliverables
- Security vulnerability reports with severity ratings
- Remediation recommendations with code examples
- Security configuration guidelines
- Compliance check results
- Security best practices documentation

Always provide specific, actionable security recommendations with code examples when possible. Focus on practical implementation rather than theoretical concepts.""",
            allowed_tools=["read_files", "write_md", "scan_vulnerabilities", "analyze_code", "search_web"],
            max_turns=8,
            expertise_areas=[
                "Application Security (Web, Mobile, API)",
                "Vulnerability Assessment and Penetration Testing",
                "Security Standards Compliance (OWASP, NIST, GDPR)",
                "Threat Modeling and Risk Assessment",
                "Security Code Review and Best Practices"
            ],
            use_cases=[
                "Security vulnerability analysis and assessment",
                "Security best practices implementation guidance",
                "Compliance audit preparation and review",
                "Security architecture review and recommendations",
                "Threat modeling and risk assessment"
            ],
            best_practices=[
                "Always validate and sanitize user inputs",
                "Implement principle of least privilege",
                "Use HTTPS and secure communication protocols",
                "Keep security dependencies updated",
                "Implement proper authentication and authorization",
                "Log security events but avoid sensitive data in logs",
                "Regular security testing and code reviews",
                "Follow defense-in-depth principles"
            ],
            limitations=[
                "Cannot perform actual penetration testing on live systems",
                "Limited to code analysis and recommendations",
                "Cannot guarantee security of third-party dependencies",
                "Security assessments are based on provided code and context"
            ]
        )

    def _create_data_scientist_template(self) -> AgentTemplate:
        """Create data scientist agent template."""
        return AgentTemplate(
            name="data_scientist",
            domain=AgentDomain.DATA_SCIENCE,
            description="Specialized agent for data analysis, machine learning, and statistical modeling tasks",
            system_prompt="""You are a Data Scientist specializing in data analysis, machine learning, and statistical modeling.

Your core expertise areas:
- **Data Analysis**: Exploratory data analysis, statistical testing, data visualization
- **Machine Learning**: Model development, training, evaluation, and optimization
- **Statistical Modeling**: Hypothesis testing, regression analysis, predictive modeling
- **Data Engineering**: Data cleaning, preprocessing, feature engineering

## Data Science Workflow
1. **Data Understanding**: Explore and understand the dataset structure and quality
2. **Data Preparation**: Clean, preprocess, and engineer features
3. **Exploratory Analysis**: Perform statistical analysis and visualization
4. **Model Development**: Build and train appropriate ML models
5. **Evaluation**: Assess model performance and validate results
6. **Implementation**: Provide deployment-ready code and documentation

## Technical Capabilities
- Python data science libraries (pandas, numpy, scikit-learn, matplotlib)
- Statistical analysis and hypothesis testing
- Machine learning model development and evaluation
- Data visualization and reporting
- Feature engineering and selection

## Deliverables
- Comprehensive data analysis reports
- Machine learning model implementations
- Statistical analysis results and interpretations
- Data visualizations and dashboards
- Recommendations based on data insights

Always provide code examples and explain statistical concepts clearly. Focus on practical data science applications.""",
            allowed_tools=["read_files", "write_md", "analyze_data", "visualize_data", "search_web"],
            max_turns=10,
            expertise_areas=[
                "Statistical Analysis and Hypothesis Testing",
                "Machine Learning Model Development",
                "Data Visualization and Communication",
                "Feature Engineering and Selection",
                "Predictive Modeling and Forecasting"
            ],
            use_cases=[
                "Exploratory data analysis and insights generation",
                "Machine learning model development and evaluation",
                "Statistical analysis and hypothesis testing",
                "Data visualization and reporting",
                "Predictive modeling and forecasting"
            ],
            best_practices=[
                "Always perform exploratory data analysis first",
                "Validate assumptions with statistical tests",
                "Use appropriate train/test splits and cross-validation",
                "Document data preprocessing steps clearly",
                "Consider model interpretability alongside accuracy",
                "Validate model performance on unseen data",
                "Handle missing values and outliers appropriately"
            ],
            limitations=[
                "Cannot access external databases or APIs directly",
                "Limited to provided datasets for analysis",
                "Cannot perform real-time model training on large datasets",
                "Statistical analysis limited to provided data context"
            ]
        )

    def _create_api_developer_template(self) -> AgentTemplate:
        """Create API developer agent template."""
        return AgentTemplate(
            name="api_developer",
            domain=AgentDomain.DEVELOPMENT,
            description="Specialized agent for API development, REST services, and backend integration",
            system_prompt="""You are an API Developer specializing in RESTful API design, development, and integration.

Your core expertise areas:
- **API Design**: RESTful principles, OpenAPI specification, versioning strategies
- **Backend Development**: Server-side implementation, database integration, authentication
- **API Documentation**: Comprehensive API docs, interactive documentation, testing tools
- **Performance Optimization**: Caching strategies, rate limiting, load balancing

## API Development Process
1. **Requirements Analysis**: Understand API requirements and use cases
2. **Design Architecture**: Define endpoints, data models, and authentication
3. **Implementation**: Develop server-side API with proper error handling
4. **Documentation**: Create comprehensive API documentation
5. **Testing**: Unit tests, integration tests, and API validation
6. **Deployment**: Production deployment with monitoring and scaling

## Technical Expertise
- REST API design principles and best practices
- OpenAPI/Swagger specification and documentation
- Authentication and authorization (OAuth, JWT, API Keys)
- Database design and integration
- Error handling and response formatting
- API testing and validation

## Deliverables
- REST API implementation with proper documentation
- API specification files (OpenAPI/Swagger)
- Database schemas and migration scripts
- Testing suites and validation scripts
- Deployment and monitoring configurations

Always focus on creating scalable, maintainable, and well-documented APIs. Follow industry standards and best practices.""",
            allowed_tools=["read_files", "write_md", "create_api", "test_api", "search_web"],
            max_turns=8,
            expertise_areas=[
                "RESTful API Design and Development",
                "OpenAPI Specification and Documentation",
                "Authentication and Authorization Systems",
                "Database Integration and Schema Design",
                "API Testing and Validation"
            ],
            use_cases=[
                "REST API development and implementation",
                "API documentation and specification creation",
                "Authentication and authorization system design",
                "Database integration and schema design",
                "API testing and validation framework setup"
            ],
            best_practices=[
                "Use proper HTTP status codes and response formats",
                "Implement comprehensive error handling and logging",
                "Always validate input data and sanitize user inputs",
                "Use authentication and authorization for protected endpoints",
                "Implement rate limiting and caching for performance",
                "Create comprehensive API documentation",
                "Write tests for all endpoints and error cases",
                "Use versioning for API evolution"
            ],
            limitations=[
                "Cannot deploy to actual cloud environments",
                "Limited to local development and testing",
                "Cannot test with real external services",
                "Database operations limited to provided datasets"
            ]
        )


class TemplatedAgentManager:
    """Enhanced agent manager with template support."""

    def __init__(self, workspace_path: Path, template_registry: Optional[TemplateRegistry] = None):
        self.workspace_path = workspace_path
        self.template_registry = template_registry or TemplateRegistry()
        self.streaming_manager = StreamingAgentManager(workspace_path)

        # Track created agents
        self.created_agents: Dict[str, Dict[str, Any]] = {}

    async def create_agent_from_template(
        self,
        template_name: str,
        customizations: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a specialized agent from a template."""
        template = self.template_registry.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Validate template
        validation = self.template_registry.validate_template(template)
        if not validation.is_valid:
            raise ValueError(f"Template validation failed: {validation.errors}")

        # Apply customizations
        if customizations:
            agent_config = self._apply_customizations(template, customizations)
        else:
            agent_config = self._template_to_config(template)

        # Generate unique agent ID
        if not agent_id:
            agent_id = f"{template.name}_{datetime.now().strftime('%H%M%S')}"

        # Store agent info
        self.created_agents[agent_id] = {
            "template_name": template_name,
            "config": agent_config,
            "created_at": datetime.now().isoformat(),
            "customizations": customizations or {}
        }

        # Generate documentation
        await self._generate_agent_documentation(agent_id, template, customizations)

        return {
            "agent_id": agent_id,
            "template_name": template_name,
            "config": agent_config,
            "validation": validation,
            "documentation_file": f"agent_docs/{agent_id}.md"
        }

    def _apply_customizations(self, template: AgentTemplate, customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply customizations to a template."""
        config = self._template_to_config(template)

        # Apply allowed customizations
        if "max_turns" in customizations:
            config["max_turns"] = customizations["max_turns"]

        if "allowed_tools" in customizations:
            config["allowed_tools"] = list(set(config["allowed_tools"] + customizations["allowed_tools"]))

        if "system_prompt_suffix" in customizations:
            config["system_prompt"] += "\n\n" + customizations["system_prompt_suffix"]

        if "system_prompt_prefix" in customizations:
            config["system_prompt"] = customizations["system_prompt_prefix"] + "\n\n" + config["system_prompt"]

        return config

    def _template_to_config(self, template: AgentTemplate) -> Dict[str, Any]:
        """Convert a template to agent configuration."""
        return {
            "system_prompt": template.system_prompt,
            "allowed_tools": template.allowed_tools,
            "max_turns": template.max_turns,
            "domain": template.domain.value,
            "expertise_areas": template.expertise_areas,
            "use_cases": template.use_cases
        }

    async def _generate_agent_documentation(
        self,
        agent_id: str,
        template: AgentTemplate,
        customizations: Optional[Dict[str, Any]] = None
    ):
        """Generate documentation for a created agent."""
        docs_dir = self.workspace_path / "agent_docs"
        docs_dir.mkdir(exist_ok=True)

        doc_content = f"""# {template.name.replace('_', ' ').title()} Agent

**Template**: {template.name}
**Domain**: {template.domain.value}
**Created**: {datetime.now().isoformat()}
**Agent ID**: {agent_id}

## Description

{template.description}

## Expertise Areas

"""

        for area in template.expertise_areas:
            doc_content += f"- **{area}**\n"

        doc_content += f"""
## Use Cases

"""

        for use_case in template.use_cases:
            doc_content += f"- {use_case}\n"

        if template.best_practices:
            doc_content += f"""
## Best Practices

"""
            for practice in template.best_practices:
                doc_content += f"- {practice}\n"

        if template.limitations:
            doc_content += f"""
## Limitations

"""
            for limitation in template.limitations:
                doc_content += f"- {limitation}\n"

        if customizations:
            doc_content += f"""
## Applied Customizations

```json
{json.dumps(customizations, indent=2)}
```
"""

        doc_content += f"""
## Configuration

- **Max Turns**: {template.max_turns}
- **Allowed Tools**: {', '.join(template.allowed_tools)}

---

*Generated by El Jefe Agent Template System*
"""

        # Write documentation
        doc_file = docs_dir / f"{agent_id}.md"
        async with aiofiles.open(doc_file, 'w') as f:
            await f.write(doc_content)

    def list_available_templates(self, domain: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """List available templates with details."""
        domain_filter = AgentDomain(domain) if domain else None
        template_names = self.template_registry.list_templates(domain_filter)

        return {
            name: {
                "name": template.name,
                "domain": template.domain.value,
                "description": template.description,
                "expertise_areas": template.expertise_areas[:3],  # Show first 3
                "use_cases": template.use_cases[:2]  # Show first 2
            }
            for name, template in self.template_registry.templates.items()
            if name in template_names
        }

    async def cleanup(self):
        """Cleanup resources."""
        await self.streaming_manager.cleanup()
