#!/bin/bash
# Local installation script for el-jefe (no sudo required)

set -e

INSTALL_DIR="/Users/ryanmacomber/Documents/Orchestrator-Agent"

echo "🚀 Installing el-jefe CLI tool..."

# Check if ~/.local/bin exists, create if not
mkdir -p ~/.local/bin

# Create symlink in ~/.local/bin (user-level, no sudo required)
ln -sf "$INSTALL_DIR/el-jefe" ~/.local/bin/el-jefe

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "🔧 Adding ~/.local/bin to your PATH..."

    # Determine shell profile
    SHELL_PROFILE=""
    if [ -f ~/.zshrc ]; then
        SHELL_PROFILE=~/.zshrc
    elif [ -f ~/.bash_profile ]; then
        SHELL_PROFILE=~/.bash_profile
    elif [ -f ~/.bashrc ]; then
        SHELL_PROFILE=~/.bashrc
    fi

    if [ ! -z "$SHELL_PROFILE" ]; then
        if ! grep -q "\.local/bin" "$SHELL_PROFILE"; then
            echo "" >> "$SHELL_PROFILE"
            echo "# el-jefe CLI tool" >> "$SHELL_PROFILE"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_PROFILE"
            echo "✅ Added to $SHELL_PROFILE"
        else
            echo "ℹ️  ~/.local/bin already in $SHELL_PROFILE"
        fi
    fi
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Command: el-jefe"
echo ""
echo "🔄 Restart your terminal or run: source ~/.zshrc (or ~/.bash_profile)"
echo ""
echo "💡 Try it out:"
echo "   el-jefe --help"
echo "   el-jefe \"Research AI trends\""
echo "   el-jefe \"Build a Python script\""
echo ""
echo "🏠 Workspaces will be stored in: $INSTALL_DIR/workspaces"
echo ""
echo "🔧 Alternative: You can also run it directly:"
echo "   $INSTALL_DIR/el-jefe \"your task\""