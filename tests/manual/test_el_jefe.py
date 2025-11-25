#!/usr/bin/env python3
"""
Test El Jefe orchestrator import and initialization
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports (absolute path)
# File is in tests/manual/, project root is two levels up
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

def test_orchestrator():
    """Test orchestrator import and basic functionality."""
    print("🧪 Testing El Jefe Orchestrator...")

    try:
        from main import Orchestrator
        print("✅ Orchestrator import successful")
    except ImportError as e:
        print(f"❌ Orchestrator import failed: {e}")
        return False

    try:
        # Test basic initialization
        orchestrator = Orchestrator(base_dir="workspaces", interactive=False)
        print("✅ Orchestrator initialization successful")
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return False

    try:
        # Test list workspaces
        import asyncio
        async def test_list():
            workspaces = await orchestrator.list_workspaces(limit=5)
            print(f"✅ List workspaces successful: {len(workspaces)} found")
            return True

        return asyncio.run(test_list())
    except Exception as e:
        print(f"❌ List workspaces failed: {e}")
        return False

def test_chat_interface():
    """Test chat interface import."""
    print("\n🧪 Testing Chat Interface...")

    try:
        # Check if chat functionality exists in monitoring_dashboard
        from monitoring_dashboard import ChatMessage
        print("✅ ChatMessage import successful")

        # Test creating a chat message
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        msg = ChatMessage("test", "user", "Test message", timestamp)
        print("✅ ChatMessage creation successful")
        return True
    except ImportError as e:
        print(f"❌ Chat interface import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Chat interface test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 El Jefe Import Test Suite")
    print("=" * 40)

    # Test current working directory
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📁 Python path: {sys.path[:3]}")  # Show first 3 entries

    # Run tests
    orch_test = test_orchestrator()
    chat_test = test_chat_interface()

    print("\n" + "=" * 40)
    print("📊 Results:")
    print(f"Orchestrator: {'✅ PASS' if orch_test else '❌ FAIL'}")
    print(f"Chat Interface: {'✅ PASS' if chat_test else '❌ FAIL'}")

    if orch_test and chat_test:
        print("\n🎉 All tests passed! El Jefe should work correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)