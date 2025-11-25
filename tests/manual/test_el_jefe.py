#!/usr/bin/env python3
"""
Test El Jefe orchestrator import and initialization
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, "src")

def test_orchestrator():
    """Test orchestrator import and basic functionality."""
    print("🧪 Testing El Jefe Orchestrator...")

    try:
        from src.orchestrator import Orchestrator
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
        from src.chat_interface import ChatInterface
        print("✅ ChatInterface import successful")
    except ImportError as e:
        print(f"❌ ChatInterface import failed: {e}")
        return False

    try:
        # Test if orchestrator is available in chat interface
        chat = ChatInterface()
        if chat.orchestrator is not None:
            print("✅ ChatInterface orchestrator available")
            return True
        else:
            print("❌ ChatInterface orchestrator is None")
            return False
    except Exception as e:
        print(f"❌ ChatInterface test failed: {e}")
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