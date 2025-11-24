#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced streaming capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.streaming_orchestrator import StreamingOrchestrator

async def test_streaming_workflow():
    """Test the streaming orchestrator with a simple goal."""

    print("🚀 Testing Enhanced Streaming Orchestrator")
    print("=" * 50)

    # Initialize streaming orchestrator
    orchestrator = StreamingOrchestrator(
        base_dir="test_workspaces",
        enable_monitoring=True,
        enable_streaming=True
    )

    # Test goal
    goal = "Write a brief summary of artificial intelligence for a beginner"

    print(f"📋 Goal: {goal}")
    print(f"🎯 Starting streaming workflow...\n")

    try:
        # Execute with streaming
        update_count = 0
        async for update in orchestrator.execute_goal_streaming(
            goal,
            session_id="test_session",
            enable_parallel=False  # Keep it simple for testing
        ):
            update_count += 1
            timestamp = update["timestamp"][-8:]  # Last 8 chars for time

            if update["type"] == "workflow_started":
                print(f"[{timestamp}] 📂 Workflow Started")
                print(f"  Session: {update['session_id']}")
                print(f"  Workspace: {update['workspace']}")

            elif update["type"] == "workflow_planned":
                print(f"\n[{timestamp}] 📋 Planned {update['total_steps']} steps")
                for step in update["steps"]:
                    print(f"  Step {step['step']}: {step['description']} ({step['agent_type']})")

            elif update["type"] == "step_started":
                print(f"\n[{timestamp}] ⚡ Step {update['step']}/{update['total_steps']}")
                print(f"  Agent: {update['agent_type']}")
                print(f"  Task: {update['description']}")

            elif update["type"] == "text_chunk":
                # Show brief preview of real-time output
                text = update["content"][:100].replace('\n', ' ')
                if len(update["content"]) > 100:
                    text += "..."
                print(f"  📝 {text}")

            elif update["type"] == "tool_use":
                print(f"  🔧 Tool: {update['tool']}")

            elif update["type"] == "agent_completed":
                print(f"\n[{timestamp}] ✅ Agent Completed")
                print(f"  Words: {update['total_words']}")
                print(f"  Tokens: {update.get('total_tokens', 0)}")
                if update['tools_used']:
                    print(f"  Tools: {', '.join(update['tools_used'])}")

            elif update["type"] == "step_completed":
                print(f"✅ Step {update['step']} completed")

            elif update["type"] == "workflow_completed":
                print(f"\n[{timestamp}] 🎉 Workflow Completed!")
                print(f"  Session: {update['session_id']}")
                print(f"  Workspace: {update['workspace']}")

                # Display metrics
                metrics = update.get("metrics", {})
                if metrics:
                    print(f"\n📊 Performance Metrics:")
                    print(f"  Total Tokens: {metrics.get('total_tokens', 0):,}")
                    print(f"  Total Words: {metrics.get('total_words', 0):,}")
                    print(f"  API Calls: {metrics.get('total_api_calls', 0)}")
                    print(f"  Tool Calls: {metrics.get('total_tool_calls', 0)}")
                    if metrics.get('average_response_time', 0) > 0:
                        print(f"  Avg Response Time: {metrics.get('average_response_time', 0):.2f}s")
                break

            elif update["type"] == "workflow_error":
                print(f"\n❌ Workflow Error: {update['error']}")
                break

        print(f"\n✅ Test completed! Received {update_count} streaming updates.")

    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        await orchestrator.cleanup()
        print("\n🧹 Cleanup completed.")

if __name__ == "__main__":
    asyncio.run(test_streaming_workflow())