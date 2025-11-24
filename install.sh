#!/bin/bash
# Installation script for AI Orchestrator CLI tools

set -e

INSTALL_DIR="/Users/ryanmacomber/Documents/Orchestrator-Agent"

echo "🚀 Installing AI Orchestrator CLI tools..."

# Create symbolic links in /usr/local/bin (requires sudo)
echo "📦 Creating system-wide symlinks..."

# Ask for sudo password upfront
echo "Please enter your password to create system-wide symlinks:"

# Create symlink for el-jefe
ln -sf "$INSTALL_DIR/el-jefe" "/usr/local/bin/el-jefe"

# Or add to shell profile
echo "🔧 Adding to PATH in shell profile..."

SHELL_PROFILE=""
if [ -f ~/.zshrc ]; then
    SHELL_PROFILE=~/.zshrc
elif [ -f ~/.bash_profile ]; then
    SHELL_PROFILE=~/.bash_profile
elif [ -f ~/.bashrc ]; then
    SHELL_PROFILE=~/.bashrc
fi

if [ ! -z "$SHELL_PROFILE" ]; then
    if ! grep -q "Orchestrator-Agent" "$SHELL_PROFILE"; then
        echo "" >> "$SHELL_PROFILE"
        echo "# AI Orchestrator CLI tools" >> "$SHELL_PROFILE"
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_PROFILE"
        echo "✅ Added to $SHELL_PROFILE"
    else
        echo "ℹ️  Already in $SHELL_PROFILE"
    fi
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Available command:"
echo "   el-jefe    - AI Orchestrator CLI"
echo ""
echo "🔄 Restart your terminal or run: source $SHELL_PROFILE"
echo ""
echo "💡 Try it out:"
echo "   el-jefe --help"
echo "   el-jefe \"Research AI trends\""
echo "   el-jefe \"Build a Python script\""
echo ""
echo "🏠 Workspaces will be stored in: $INSTALL_DIR/workspaces"