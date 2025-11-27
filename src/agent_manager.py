"""
Agent Manager Module

Handles spawning and coordinating specialist agents for different tasks.
Manages agent lifecycle, tool authorization, and result collection.
"""

import json
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import aiofiles

from claude_agent_sdk import query, ClaudeAgentOptions

# Import MCP tools for agent enhancement
try:
    from .mcp_integration import get_mcp_integration, get_mcp_tool_definitions
    MCP_TOOLS_AVAILABLE = True
except ImportError:
    MCP_TOOLS_AVAILABLE = False

# Import Playwright web researcher
try:
    from .playwright_web_researcher import PlaywrightWebResearcher
    PLAYWRIGHT_RESEARCHER_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_RESEARCHER_AVAILABLE = False


class AgentType(Enum):
    """Enumeration of available agent types."""
    RESEARCHER = "researcher"
    CODER = "coder"
    WRITER = "writer"
    ANALYST = "analyst"
    DESIGNER = "designer"
    QA_TESTER = "qa_tester"
    MEDIA_CREATOR = "media_creator"
    WEB_RESEARCHER = "web_researcher"
    # Template-based agents
    SECURITY_ANALYST = "security_analyst"
    DATA_SCIENTIST = "data_scientist"
    API_DEVELOPER = "api_developer"
    # Claude Code Premium Agents - Native El Jefe Versions
    AI_ENGINEER = "ai_engineer"
    PROMPT_ENGINEER = "prompt_engineer"
    PYTHON_PRO = "python_pro"
    FRONTEND_DEVELOPER = "frontend_developer"
    UI_UX_DESIGNER = "ui_ux_designer"
    # Specialized Security and Orchestration Agents
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"
    SECURITY_ENGINEER = "security_engineer"
    PENETRATION_TESTER = "penetration_tester"
    CLI_DEVELOPER = "cli_developer"


class AgentConfig:
    """Configuration for agent types."""

    AGENT_CONFIGS = {
        AgentType.RESEARCHER: {
            "system_prompt": "You are a research specialist. Your task is to gather, synthesize, and present information in a clear, structured manner. Use credible sources and always verify facts. Present findings in well-organized bullet points with proper attribution. You have access to powerful web search and content extraction tools. IMPORTANT: Always use the current year (2025) when searching for recent information and trends. Use time-sensitive search terms like '2025', 'latest', 'recent', 'current year' to get the most up-to-date information.",
            "allowed_tools": ["search_web", "web_search_prime", "write_md", "read_files", "web_fetch"],
            "max_turns": 8,
            "description": "Researches and synthesizes information from various sources with enhanced web capabilities"
        },
        AgentType.CODER: {
            "system_prompt": "You are a senior software developer. Write clean, well-documented, and efficient code. Follow best practices and design patterns. Include error handling and comments where necessary. Focus on Python but can work with other languages as needed.",
            "allowed_tools": ["write_md", "write_file", "read_files", "list_directory"],
            "max_turns": 6,
            "description": "Builds software solutions and writes scripts"
        },
        AgentType.WRITER: {
            "system_prompt": "You are a professional writer and content creator. Create engaging, clear, and well-structured content. Adapt your tone to the target audience. Focus on readability, coherence, and proper grammar. You can research current information and trends to enhance your content.",
            "allowed_tools": ["write_md", "read_files", "web_search_prime", "web_fetch"],
            "max_turns": 6,
            "description": "Creates and edits documents and content with research capabilities"
        },
        AgentType.ANALYST: {
            "system_prompt": "You are a data analyst and trend specialist. Analyze data patterns, identify trends, and provide actionable insights. Use quantitative methods and present findings with supporting evidence. You can access current web data for real-time trend analysis. IMPORTANT: Always use the current year (2025) when searching for recent trends and data. Use time-sensitive search terms like '2025', 'latest', 'recent', 'current year' to get the most up-to-date information.",
            "allowed_tools": ["search_web", "web_search_prime", "write_md", "read_files", "analyze_data", "web_fetch"],
            "max_turns": 7,
            "description": "Performs data analysis and trend identification with web research capabilities"
        },
        AgentType.DESIGNER: {
            "system_prompt": "You are a system architect and designer. Create scalable, maintainable system designs and architectures. Consider best practices, security, and performance. Provide clear documentation and diagrams.",
            "allowed_tools": ["write_md", "create_diagram", "read_files"],
            "max_turns": 5,
            "description": "Designs architectures and system plans"
        },
        AgentType.QA_TESTER: {
            "system_prompt": "You are a quality assurance specialist. Test, validate, and verify deliverables. Identify issues, suggest improvements, and ensure quality standards are met. Provide detailed test reports.",
            "allowed_tools": ["write_md", "test_code", "read_files", "validate_output"],
            "max_turns": 5,
            "description": "Validates and tests deliverables"
        },
        AgentType.MEDIA_CREATOR: {
            "system_prompt": "You are a creative media specialist with expertise in visual content creation. Generate compelling images and videos using advanced AI models. Create visuals that enhance content, engage audiences, and communicate complex ideas effectively. Consider brand consistency, target audience, and content context when creating media.",
            "allowed_tools": ["generate_image", "generate_video", "save_media", "write_md", "read_files", "web_search_prime", "web_fetch"],
            "max_turns": 8,
            "description": "Creates images and videos using AI generation models"
        },
        AgentType.WEB_RESEARCHER: {
            "system_prompt": "You are a Web Researcher specializing in automated web research and content extraction using Playwright browser automation. Your expertise includes navigating websites, extracting relevant content, capturing screenshots, and generating comprehensive research reports. You can access any website, handle dynamic content, and organize research findings effectively. Use your browser automation capabilities to gather current information from multiple sources and present it in well-structured reports with visual evidence.",
            "allowed_tools": ["playwright_navigate", "playwright_screenshot", "playwright_click", "playwright_fill", "playwright_get_content", "web_search_prime", "search_web", "write_md", "read_files", "analyze_image"],
            "max_turns": 10,
            "description": "Automated web research specialist with Playwright browser automation"
        },
        AgentType.SECURITY_ANALYST: {
            "system_prompt": "You are a Security Analyst specializing in application security, vulnerability assessment, and security best practices. Your core expertise areas include threat assessment, security implementation, compliance standards, and security testing. Always provide specific, actionable security recommendations with code examples when possible.",
            "allowed_tools": ["read_files", "write_md", "scan_vulnerabilities", "analyze_code", "search_web"],
            "max_turns": 8,
            "description": "Performs security analysis and vulnerability assessment"
        },
        AgentType.DATA_SCIENTIST: {
            "system_prompt": "You are a Data Scientist specializing in data analysis, machine learning, and statistical modeling. Your core expertise areas include exploratory data analysis, statistical testing, machine learning model development, and data visualization. Always provide code examples and explain statistical concepts clearly.",
            "allowed_tools": ["read_files", "write_md", "analyze_data", "visualize_data", "search_web"],
            "max_turns": 10,
            "description": "Performs data analysis and machine learning tasks"
        },
        AgentType.API_DEVELOPER: {
            "system_prompt": "You are an API Developer specializing in RESTful API design, development, and integration. Your core expertise areas include API design principles, backend development, API documentation, and performance optimization. Always focus on creating scalable, maintainable, and well-documented APIs.",
            "allowed_tools": ["read_files", "write_md", "create_api", "test_api", "search_web"],
            "max_turns": 8,
            "description": "Designs and implements RESTful APIs and backend services"
        },
        # Claude Code Premium Agents - Native El Jefe Versions
        AgentType.AI_ENGINEER: {
            "system_prompt": "You are an elite AI Engineer specializing in LLM applications, RAG systems, and AI infrastructure. Your expertise includes prompt engineering, vector databases, model integration, and scalable AI system architecture. You build production-ready AI solutions with robust error handling and performance optimization. Always consider token efficiency, response accuracy, and user experience. Focus on creating reliable, maintainable AI systems that integrate seamlessly with existing workflows.",
            "allowed_tools": ["read_files", "write_md", "search_web", "web_search_prime", "create_api", "test_api", "system_commands", "mcp_tools"],
            "max_turns": 10,
            "description": "Elite AI/ML engineer for RAG systems, LLM apps, and AI infrastructure"
        },
        AgentType.PROMPT_ENGINEER: {
            "system_prompt": "You are an expert Prompt Engineer specializing in optimizing AI model interactions and system prompts. Your expertise includes chain-of-thought prompting, role-based prompting, output formatting, and prompt optimization strategies. You excel at crafting precise, effective prompts that consistently produce high-quality outputs. Focus on clarity, specificity, and achieving predictable, reliable results from language models. Always consider edge cases and provide fallback strategies.",
            "allowed_tools": ["read_files", "write_md", "test_prompts", "analyze_outputs", "search_web", "mcp_tools"],
            "max_turns": 8,
            "description": "Expert in prompt optimization and AI interaction design"
        },
        AgentType.PYTHON_PRO: {
            "system_prompt": "You are an elite Python developer with deep expertise in advanced Python programming, performance optimization, and software architecture. You excel at async/await patterns, decorators, metaclasses, performance profiling, and building scalable Python applications. Your code is always production-ready with proper error handling, logging, and testing. Focus on writing clean, efficient, maintainable Python that follows best practices and design patterns. Always consider performance implications and memory usage.",
            "allowed_tools": ["read_files", "write_py", "write_md", "test_code", "profile_performance", "system_commands", "mcp_tools", "install_packages"],
            "max_turns": 8,
            "description": "Advanced Python development and performance optimization expert"
        },
        AgentType.FRONTEND_DEVELOPER: {
            "system_prompt": "You are a specialized Frontend Developer with expertise in React, TypeScript, and modern web development. You excel at building responsive, accessible user interfaces with optimal performance. Your skills include component architecture, state management, API integration, and modern CSS techniques. You write clean, maintainable code with proper accessibility support and cross-browser compatibility. Focus on creating intuitive, performant user experiences that work seamlessly across all devices.",
            "allowed_tools": ["read_files", "write_js", "write_tsx", "write_css", "write_html", "test_components", "performance_audit", "mcp_tools"],
            "max_turns": 8,
            "description": "React and modern frontend development specialist"
        },
        AgentType.UI_UX_DESIGNER: {
            "system_prompt": "You are a UI/UX Designer specializing in creating exceptional user experiences and beautiful interface designs. Your expertise includes user research, wireframing, prototyping, design systems, and usability testing. You create intuitive, accessible designs that balance aesthetics with functionality. You understand color theory, typography, layout principles, and responsive design. Focus on creating designs that are both visually appealing and highly usable, with consideration for user psychology and behavior patterns.",
            "allowed_tools": ["read_files", "create_wireframes", "design_prototypes", "user_research", "test_usability", "create_design_systems", "mcp_tools"],
            "max_turns": 6,
            "description": "UI/UX design expert for user-centered interfaces"
        },
        # Specialized Security and Orchestration Agents
        AgentType.WORKFLOW_ORCHESTRATOR: {
            "system_prompt": "You are a Workflow Orchestrator specializing in coordinating complex multi-agent workflows and task management. Your expertise includes workflow design, agent coordination, dependency management, and process optimization. You excel at breaking down complex tasks into manageable steps, coordinating handoffs between specialized agents, and ensuring seamless execution. You monitor progress, handle exceptions, and optimize workflows for maximum efficiency and reliability. Focus on creating robust, scalable workflows that can handle complex projects with multiple interdependent tasks.",
            "allowed_tools": ["read_files", "write_md", "coordinate_agents", "monitor_progress", "create_workflows", "optimize_processes", "manage_tasks", "mcp_tools"],
            "max_turns": 12,
            "description": "Expert in multi-agent workflow coordination and task orchestration"
        },
        AgentType.SECURITY_ENGINEER: {
            "system_prompt": "You are a Security Engineer specializing in building secure systems and implementing security best practices. Your expertise includes threat modeling, secure coding practices, vulnerability assessment, security architecture, and compliance frameworks. You excel at identifying security risks, implementing protective measures, and ensuring systems meet security standards. You understand common vulnerabilities (OWASP Top 10), encryption methods, authentication systems, and security monitoring. Focus on creating systems that are secure by design and can withstand modern security threats.",
            "allowed_tools": ["read_files", "write_secure_code", "threat_modeling", "vulnerability_scan", "security_audit", "implement_encryption", "setup_authentication", "mcp_tools", "system_commands"],
            "max_turns": 10,
            "description": "Security specialist for secure system design and implementation"
        },
        AgentType.PENETRATION_TESTER: {
            "system_prompt": "You are an elite Penetration Tester specializing in ethical hacking and security vulnerability assessment. Your expertise includes network penetration testing, web application security testing, social engineering, and exploit development. You excel at identifying security weaknesses, demonstrating attack vectors, and providing remediation recommendations. You understand common attack patterns, exploitation techniques, and security testing methodologies. You always operate within legal and ethical boundaries, focusing on improving security through responsible disclosure. Your goal is to help organizations identify and fix vulnerabilities before they can be exploited maliciously.",
            "allowed_tools": ["read_files", "scan_vulnerabilities", "test_authentication", "network_scan", "exploit_testing", "analyze_payloads", "social_engineering_test", "write_reports", "security_tools", "mcp_tools"],
            "max_turns": 15,
            "description": "Ethical hacker for security vulnerability assessment and testing"
        },
        AgentType.CLI_DEVELOPER: {
            "system_prompt": "You are an expert CLI Developer specializing in command-line interface design, developer tools, and terminal applications. Your expertise includes building intuitive command-line tools, argument parsing, user experience design for terminal applications, and creating powerful developer utilities. You excel at designing clean CLI interfaces, implementing help systems, handling edge cases gracefully, and creating tools that developers love to use. You understand best practices for CLI design including POSIX compliance, error handling, output formatting, and integration with existing developer workflows.",
            "allowed_tools": ["read_files", "write_file", "write_md", "bash", "commander", "yargs", "inquirer", "chalk", "ora", "list_directory", "test_cli", "package_json", "mcp_tools"],
            "max_turns": 8,
            "description": "Expert CLI developer for command-line tools and developer utilities"
        }
    }

    @classmethod
    def get_enhanced_config(cls, agent_type: AgentType) -> Dict[str, Any]:
        """
        Get enhanced agent configuration including MCP tools if available.

        Args:
            agent_type: The type of agent

        Returns:
            Enhanced configuration dictionary
        """
        # Get base configuration
        config = cls.AGENT_CONFIGS[agent_type].copy()

        # Add MCP tools if available
        if MCP_TOOLS_AVAILABLE:
            try:
                mcp_tool_definitions = get_mcp_tool_definitions()

                if mcp_tool_definitions:
                    # Add MCP tool definitions to config
                    config["mcp_tool_definitions"] = mcp_tool_definitions

                    # Also add tool names for compatibility
                    mcp_tool_names = [tool["name"] for tool in mcp_tool_definitions]
                    base_tools = config.get("allowed_tools", [])
                    enhanced_tools = list(set(base_tools + mcp_tool_names))
                    config["allowed_tools"] = enhanced_tools

                    # Update system prompt to mention MCP capabilities
                    mcp_prompt = "\n\nYou also have access to powerful MCP (Model Context Protocol) tools:\n"
                    mcp_prompt += "\n🧠 Memory & Knowledge Tools:\n"
                    mcp_prompt += "- memory_create_entity: Create entities in a knowledge graph\n"
                    mcp_prompt += "- memory_create_relation: Create relations between entities\n"
                    mcp_prompt += "- memory_search: Search the knowledge graph\n"
                    mcp_prompt += "- memory_add_observations: Add observations to entities\n"
                    mcp_prompt += "\n📚 Documentation & Research Tools:\n"
                    mcp_prompt += "- context7_resolve_library: Find library documentation\n"
                    mcp_prompt += "- context7_get_docs: Get up-to-date library documentation\n"
                    mcp_prompt += "- search_web: Search the web for current information\n"
                    mcp_prompt += "- web_search_prime: Advanced web search with filtering options\n"
                    mcp_prompt += "- web_fetch: Read and convert web content from URLs\n"
                    mcp_prompt += "\n👁️ Vision & Media Analysis Tools:\n"
                    mcp_prompt += "- analyze_image: Analyze images with AI vision\n"
                    mcp_prompt += "- analyze_video: Analyze videos with AI vision\n"
                    mcp_prompt += "\n🌐 Browser Automation Tools:\n"
                    mcp_prompt += "- navigate_to_url/browser_navigate: Navigate to websites\n"
                    mcp_prompt += "- take_screenshot/browser_screenshot: Capture screenshots\n"
                    mcp_prompt += "- click_element/browser_click: Click elements on pages\n"
                    mcp_prompt += "- fill_input/browser_fill: Fill form fields\n"
                    mcp_prompt += "\nUse these tools when relevant to enhance your capabilities and provide better results."

                    config["system_prompt"] += mcp_prompt

                    print(f"🔧 Enhanced {agent_type.value} agent with {len(mcp_tools)} MCP tools")

            except Exception as e:
                print(f"⚠️  Failed to enhance {agent_type.value} agent with MCP tools: {e}")

        return config


class AgentManager:
    """Manages spawning and coordinating specialist agents."""

    def __init__(self, workspace_path: Path):
        """
        Initialize the agent manager.

        Args:
            workspace_path: Path to the current workspace
        """
        self.workspace_path = workspace_path
        self.active_agents: Dict[str, Dict] = {}
        self.agent_outputs_dir = workspace_path / "agent_outputs"
        self.agent_outputs_dir.mkdir(exist_ok=True)

    async def spawn_agent(
        self,
        agent_type: AgentType,
        task_description: str,
        context_files: List[str] = None,
        output_file: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Spawn a specialist agent for a specific task.

        Args:
            agent_type: Type of agent to spawn
            task_description: Description of the task for the agent
            context_files: List of context files to provide to the agent
            output_file: Output file name for the agent's results
            custom_instructions: Additional instructions for the agent

        Returns:
            Dictionary containing agent execution results
        """
        # Get enhanced agent configuration with MCP tools
        config = AgentConfig.get_enhanced_config(agent_type)

        # Generate agent ID
        agent_id = f"{agent_type.value}_{datetime.now().strftime('%H%M%S')}"

        # Prepare context
        context = await self._prepare_context(context_files or [])

        # Build the full prompt
        full_prompt = self._build_prompt(task_description, context, custom_instructions)

        # Configure agent options with explicit tool permissions
        # For researcher and web_researcher agents, explicitly enable web search and browser tools
        allowed_tools = config["allowed_tools"]
        if agent_type == AgentType.RESEARCHER:
            # Ensure web search tools are enabled for researcher agents
            web_tools = ["web_search", "search_web", "web_fetch"]
            allowed_tools = list(set(allowed_tools + web_tools))
        elif agent_type == AgentType.WEB_RESEARCHER:
            # Ensure browser automation tools are enabled for web researcher agents
            browser_tools = ["playwright_navigate", "playwright_screenshot", "playwright_click", "playwright_fill", "playwright_get_content", "playwright_select", "playwright_hover", "web_search_prime", "search_web", "web_fetch"]
            allowed_tools = list(set(allowed_tools + browser_tools))

        options = ClaudeAgentOptions(
            system_prompt=config["system_prompt"],
            allowed_tools=allowed_tools,
            max_turns=config["max_turns"],
            permission_mode="bypassPermissions"  # This bypasses all tool permission restrictions
        )

        # Execute agent
        agent_result = {
            "agent_id": agent_id,
            "agent_type": agent_type.value,
            "task": task_description,
            "spawned_at": datetime.now().isoformat(),
            "status": "running"
        }

        self.active_agents[agent_id] = agent_result

        try:
            # Special handling for WEB_RESEARCHER agent type
            if agent_type == AgentType.WEB_RESEARCHER and PLAYWRIGHT_RESEARCHER_AVAILABLE:
                # Use PlaywrightWebResearcher for web research tasks
                print(f"🌐 Using PlaywrightWebResearcher for {agent_type.value} agent")

                # Extract research topic from task description
                research_topic = task_description.strip()

                # Create workspace for web research
                web_research_workspace = self.workspace_path / f"{agent_id}_web_research"
                web_research_workspace.mkdir(exist_ok=True)

                # Initialize PlaywrightWebResearcher
                web_researcher = PlaywrightWebResearcher(web_research_workspace)

                # Execute web research
                research_results = await web_researcher.research_topic(research_topic, max_sources=5)

                # Convert research results to text format
                results_text = f"Web Research Results for: {research_topic}\n"
                results_text += f"Research conducted at: {research_results['timestamp']}\n"
                results_text += f"Sources analyzed: {research_results['sources_analyzed']}\n\n"

                results_text += "KEY FINDINGS:\n"
                for i, finding in enumerate(research_results['findings'], 1):
                    results_text += f"{i}. {finding}\n"

                results_text += f"\nSCREENSHOTS TAKEN: {len(research_results['screenshots'])}\n"
                for screenshot in research_results['screenshots']:
                    results_text += f"- {screenshot}\n"

                if research_results['errors']:
                    results_text += f"\nERRORS ENCOUNTERED:\n"
                    for error in research_results['errors']:
                        results_text += f"- {error}\n"

                results = [results_text]  # Store as single result for compatibility

            else:
                # Run standard Claude agent for all other types
                results = []
                async for message in query(prompt=full_prompt, options=options):
                    for block in getattr(message, 'content', []):
                        # Check if it's a TextBlock and extract text
                        if hasattr(block, 'text'):
                            results.append(block.text)

                results_text = "\n".join(results)

            # Save results
            await self._save_agent_output(agent_id, results_text, output_file)

            # Update agent result
            agent_result.update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "results": results[:5],  # Store first 5 results as preview
                "output_file": output_file,
                "num_results": len(results)
            })

            # Log to workspace
            await self._log_agent_execution(agent_result)

            return agent_result

        except Exception as e:
            agent_result.update({
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            await self._log_agent_execution(agent_result)
            raise

    async def _prepare_context(self, context_files: List[str]) -> str:
        """
        Prepare context from provided files.

        Args:
            context_files: List of file paths to read for context

        Returns:
            Combined context text
        """
        context_parts = []

        for file_path in context_files:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                async with aiofiles.open(full_path, 'r') as f:
                    content = await f.read()
                    context_parts.append(f"--- Context from {file_path} ---\n{content}\n")

        return "\n".join(context_parts)

    def _build_prompt(self, task: str, context: str, custom_instructions: Optional[str]) -> str:
        """
        Build the full prompt for the agent.

        Args:
            task: Main task description
            context: Context from files
            custom_instructions: Additional instructions

        Returns:
            Complete prompt string
        """
        prompt_parts = [f"Task: {task}"]

        if context:
            prompt_parts.append(f"\nContext:\n{context}")

        if custom_instructions:
            prompt_parts.append(f"\nAdditional Instructions:\n{custom_instructions}")

        return "\n".join(prompt_parts)

    async def _save_agent_output(self, agent_id: str, content: str, output_file: Optional[str]):
        """
        Save the agent's output to file.

        Args:
            agent_id: Unique identifier for the agent
            content: Output content from the agent
            output_file: Optional output file name
        """
        # Save to agent-specific log
        log_file = self.agent_outputs_dir / f"{agent_id}.log"
        async with aiofiles.open(log_file, 'w') as f:
            await f.write(f"Agent ID: {agent_id}\n")
            await f.write(f"Generated: {datetime.now().isoformat()}\n")
            await f.write(f"{'='*50}\n\n")
            await f.write(content)

        # Save to specified output file if provided
        if output_file:
            output_path = self.workspace_path / output_file
            async with aiofiles.open(output_path, 'w') as f:
                await f.write(content)

    async def _log_agent_execution(self, agent_result: Dict[str, Any]):
        """
        Log agent execution to workspace history.

        Args:
            agent_result: Result of agent execution
        """
        history_path = self.workspace_path / "workflow-history.json"

        # Read existing history, create if doesn't exist
        if history_path.exists():
            async with aiofiles.open(history_path, 'r') as f:
                history = json.loads(await f.read())
        else:
            # Create initial history structure
            history = {
                "workspace_created": datetime.now().isoformat(),
                "task_name": agent_result["agent_id"],
                "steps": [],
                "agents_spawned": []
            }

        # Add agent to spawned list
        history["agents_spawned"].append({
            "agent_id": agent_result["agent_id"],
            "agent_type": agent_result["agent_type"],
            "task": agent_result["task"],
            "spawned_at": agent_result["spawned_at"],
            "status": agent_result["status"],
            "output_file": agent_result.get("output_file")
        })

        # Add as workflow step
        history["steps"].append({
            "step_type": "agent_execution",
            "agent_id": agent_result["agent_id"],
            "agent_type": agent_result["agent_type"],
            "timestamp": agent_result["spawned_at"],
            "status": agent_result["status"],
            "summary": f"Spawned {agent_result['agent_type']} agent: {agent_result['task']}"
        })

        # Write back
        async with aiofiles.open(history_path, 'w') as f:
            await f.write(json.dumps(history, indent=2))

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific agent.

        Args:
            agent_id: ID of the agent to check

        Returns:
            Agent status dictionary or None if not found
        """
        return self.active_agents.get(agent_id)

    async def list_active_agents(self) -> List[Dict[str, Any]]:
        """
        List all active agents.

        Returns:
            List of agent dictionaries
        """
        return list(self.active_agents.values())

    async def cleanup_completed_agents(self):
        """Clean up completed agents from memory."""
        completed_ids = [
            agent_id for agent_id, agent in self.active_agents.items()
            if agent["status"] in ["completed", "failed"]
        ]

        for agent_id in completed_ids:
            del self.active_agents[agent_id]