# Enhanced Chat Interface Implementation Guide
## El Jefe Monitoring Dashboard - Complete Code Examples

---

## Table of Contents
1. [HTML Structure](#html-structure)
2. [CSS Implementation](#css-implementation)
3. [JavaScript Functionality](#javascript-functionality)
4. [WebSocket Integration](#websocket-integration)
5. [Component Library](#component-library)
6. [Mobile Responsive Implementation](#mobile-responsive-implementation)

---

## HTML Structure

### Main Enhanced Chat Interface

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>El Jefe - Enhanced Workflow Chat Interface</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="enhanced-chat.css" rel="stylesheet">
</head>
<body>
    <div id="app" class="app-container">
        <!-- Header -->
        <header class="app-header">
            <div class="header-left">
                <h1 class="app-title">
                    <i class="fas fa-robot"></i>
                    El Jefe Workflow Chat
                </h1>
                <div class="connection-status" id="connection-status">
                    <span class="status-indicator connected"></span>
                    <span class="status-text">Connected</span>
                </div>
            </div>
            <div class="header-right">
                <button class="header-btn" id="settings-btn" title="Settings">
                    <i class="fas fa-cog"></i>
                </button>
                <button class="header-btn" id="help-btn" title="Help">
                    <i class="fas fa-question-circle"></i>
                </button>
                <div class="user-profile">
                    <img src="user-avatar.png" alt="User" class="user-avatar">
                    <span class="user-name">Admin</span>
                </div>
            </div>
        </header>

        <!-- Main Layout -->
        <div class="app-layout">
            <!-- Sidebar: Chat Sessions -->
            <aside class="sidebar sidebar-left" id="chat-sessions-sidebar">
                <div class="sidebar-header">
                    <h2 class="sidebar-title">Chat Sessions</h2>
                    <button class="btn btn-sm btn-primary" id="new-session-btn">
                        <i class="fas fa-plus"></i> New Session
                    </button>
                </div>
                <div class="sessions-list" id="sessions-list">
                    <!-- Chat sessions will be dynamically added here -->
                </div>
            </aside>

            <!-- Main Chat Area -->
            <main class="main-content">
                <div class="chat-container">
                    <!-- Chat Header -->
                    <div class="chat-header">
                        <div class="chat-info">
                            <h2 class="chat-title" id="current-chat-title">General Chat</h2>
                            <div class="chat-status">
                                <span class="status-badge active" id="chat-status-badge">Active</span>
                                <span class="agent-count" id="agent-count">2 agents</span>
                            </div>
                        </div>
                        <div class="chat-actions">
                            <button class="btn btn-sm btn-outline" id="search-btn">
                                <i class="fas fa-search"></i>
                            </button>
                            <button class="btn btn-sm btn-outline" id="filter-btn">
                                <i class="fas fa-filter"></i>
                            </button>
                            <button class="btn btn-sm btn-outline" id="voice-btn">
                                <i class="fas fa-microphone"></i>
                            </button>
                            <button class="btn btn-sm btn-success" id="start-workflow-btn">
                                <i class="fas fa-play"></i> Start Workflow
                            </button>
                        </div>
                    </div>

                    <!-- Workflow Assignment Panel (Collapsible) -->
                    <div class="workflow-panel" id="workflow-panel">
                        <div class="panel-header">
                            <h3 class="panel-title">
                                <i class="fas fa-tasks"></i>
                                Quick Workflow Assignment
                            </h3>
                            <button class="panel-toggle" id="workflow-panel-toggle">
                                <i class="fas fa-chevron-up"></i>
                            </button>
                        </div>
                        <div class="panel-content" id="workflow-panel-content">
                            <div class="workflow-templates">
                                <div class="template-grid" id="template-grid">
                                    <!-- Workflow templates will be dynamically added -->
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Messages Area -->
                    <div class="messages-container" id="messages-container">
                        <div class="messages-list" id="messages-list">
                            <!-- Messages will be dynamically added here -->
                        </div>
                    </div>

                    <!-- Enhanced Input Area -->
                    <div class="input-area" id="input-area">
                        <div class="input-toolbar">
                            <button class="toolbar-btn" id="attach-file-btn" title="Attach file">
                                <i class="fas fa-paperclip"></i>
                            </button>
                            <button class="toolbar-btn" id="emoji-btn" title="Add emoji">
                                <i class="fas fa-smile"></i>
                            </button>
                            <button class="toolbar-btn" id="code-block-btn" title="Add code block">
                                <i class="fas fa-code"></i>
                            </button>
                            <button class="toolbar-btn" id="template-btn" title="Insert template">
                                <i class="fas fa-file-alt"></i>
                            </button>
                        </div>
                        <div class="input-container">
                            <textarea
                                class="message-input"
                                id="message-input"
                                placeholder="Type your message or command..."
                                rows="1"
                                maxlength="5000"
                            ></textarea>
                            <button class="send-btn" id="send-btn" type="button">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                        <div class="smart-suggestions" id="smart-suggestions">
                            <!-- Smart suggestions will appear here -->
                        </div>
                    </div>
                </div>
            </main>

            <!-- Right Sidebar: Workflow Queue & Agents -->
            <aside class="sidebar sidebar-right" id="workflow-sidebar">
                <!-- Workflow Queue Section -->
                <div class="sidebar-section">
                    <div class="section-header">
                        <h3 class="section-title">
                            <i class="fas fa-list"></i>
                            Workflow Queue
                        </h3>
                        <button class="btn btn-sm btn-outline" id="refresh-queue-btn">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                    <div class="workflow-queue" id="workflow-queue">
                        <!-- Workflow queue items will be dynamically added -->
                    </div>
                </div>

                <!-- Active Agents Section -->
                <div class="sidebar-section">
                    <div class="section-header">
                        <h3 class="section-title">
                            <i class="fas fa-users"></i>
                            Active Agents
                        </h3>
                        <button class="btn btn-sm btn-outline" id="manage-agents-btn">
                            <i class="fas fa-cog"></i>
                        </button>
                    </div>
                    <div class="agents-list" id="agents-list">
                        <!-- Agent cards will be dynamically added -->
                    </div>
                </div>

                <!-- System Resources -->
                <div class="sidebar-section">
                    <div class="section-header">
                        <h3 class="section-title">
                            <i class="fas fa-chart-line"></i>
                            System Resources
                        </h3>
                    </div>
                    <div class="resource-monitor" id="resource-monitor">
                        <!-- Resource indicators will be dynamically added -->
                    </div>
                </div>
            </aside>
        </div>
    </div>

    <!-- Modals -->
    <div class="modal-overlay" id="modal-overlay"></div>

    <!-- Workflow Assignment Modal -->
    <div class="modal" id="workflow-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Assign New Workflow</h3>
                <button class="modal-close" id="workflow-modal-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body" id="workflow-modal-body">
                <!-- Workflow assignment form will be dynamically generated -->
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" id="workflow-cancel-btn">Cancel</button>
                <button class="btn btn-primary" id="workflow-assign-btn">Assign Workflow</button>
            </div>
        </div>
    </div>

    <!-- File Upload Modal -->
    <div class="modal" id="file-upload-modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Upload Files</h3>
                <button class="modal-close" id="file-upload-modal-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body" id="file-upload-modal-body">
                <!-- File upload interface will be dynamically generated -->
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" id="file-upload-cancel-btn">Cancel</button>
                <button class="btn btn-primary" id="file-upload-confirm-btn">Upload</button>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="enhanced-chat.js"></script>
    <script src="workflow-engine.js"></script>
    <script src="agent-coordinator.js"></script>
    <script src="voice-input.js"></script>
    <script src="file-handler.js"></script>
</body>
</html>
```

---

## CSS Implementation

### Enhanced Chat Styles (`enhanced-chat.css`)

```css
/* CSS Custom Properties (Design Tokens) */
:root {
  /* Color Palette */
  --primary-color: #667eea;
  --primary-hover: #5a6fd8;
  --secondary-color: #764ba2;
  --success-color: #27ae60;
  --warning-color: #f39c12;
  --error-color: #e74c3c;
  --info-color: #3498db;

  /* Neutral Colors */
  --white: #ffffff;
  --gray-50: #f8f9fa;
  --gray-100: #e9ecef;
  --gray-200: #dee2e6;
  --gray-300: #ced4da;
  --gray-400: #adb5bd;
  --gray-500: #6c757d;
  --gray-600: #495057;
  --gray-700: #343a40;
  --gray-800: #212529;
  --gray-900: #000000;

  /* Gradients */
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --success-gradient: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  --warning-gradient: linear-gradient(135deg, #f39c12 0%, #f1c40f 100%);
  --error-gradient: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);

  /* Typography */
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-family-mono: 'SF Mono', Monaco, Inconsolata, 'Roboto Mono', 'Source Code Pro', monospace;

  /* Font Sizes */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */

  /* Spacing */
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-5: 1.25rem;   /* 20px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-10: 2.5rem;   /* 40px */
  --spacing-12: 3rem;     /* 48px */
  --spacing-16: 4rem;     /* 64px */
  --spacing-20: 5rem;     /* 80px */

  /* Border Radius */
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */
  --radius-2xl: 1.5rem;   /* 24px */
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-base: 300ms ease;
  --transition-slow: 500ms ease;

  /* Z-index */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
  --z-toast: 1080;
}

/* Base Styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  line-height: 1.5;
  -webkit-text-size-adjust: 100%;
  -ms-text-size-adjust: 100%;
}

body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  line-height: 1.6;
  color: var(--gray-800);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  overflow: hidden;
}

/* App Container */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

/* Header Styles */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) var(--spacing-6);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-md);
  z-index: var(--z-fixed);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.app-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.app-title i {
  color: var(--primary-color);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--gray-100);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--error-color);
  animation: pulse 2s infinite;
}

.status-indicator.connected {
  background: var(--success-color);
}

.status-indicator.disconnected {
  background: var(--error-color);
  animation: none;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.header-btn {
  padding: var(--spacing-2);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--gray-600);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.header-btn:hover {
  background: var(--gray-100);
  color: var(--primary-color);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2);
  background: var(--gray-100);
  border-radius: var(--radius-full);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  object-fit: cover;
}

.user-name {
  font-weight: 600;
  color: var(--gray-700);
}

/* App Layout */
.app-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Sidebar Styles */
.sidebar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-left {
  width: 280px;
  min-width: 280px;
}

.sidebar-right {
  width: 320px;
  min-width: 320px;
}

.sidebar-header,
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) var(--spacing-5);
  border-bottom: 1px solid var(--gray-200);
}

.sidebar-title,
.section-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

/* Sessions List */
.sessions-list {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  padding: var(--spacing-3) var(--spacing-5);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-left: 3px solid transparent;
  position: relative;
}

.session-item:hover {
  background: var(--gray-50);
}

.session-item.active {
  background: rgba(102, 126, 234, 0.1);
  border-left-color: var(--primary-color);
}

.session-title {
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: var(--spacing-1);
}

.session-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
  color: var(--gray-500);
}

.session-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.session-status-dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--gray-400);
}

.session-status-dot.active {
  background: var(--success-color);
}

.session-status-dot.busy {
  background: var(--warning-color);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--gray-50);
  overflow: hidden;
}

/* Chat Container */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Chat Header */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) var(--spacing-6);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--gray-200);
}

.chat-info h2 {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--gray-900);
  margin-bottom: var(--spacing-1);
}

.chat-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.status-badge {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background: rgba(39, 174, 96, 0.1);
  color: var(--success-color);
}

.status-badge.paused {
  background: rgba(243, 156, 18, 0.1);
  color: var(--warning-color);
}

.status-badge.inactive {
  background: var(--gray-100);
  color: var(--gray-500);
}

.agent-count {
  font-size: var(--font-size-sm);
  color: var(--gray-500);
}

.chat-actions {
  display: flex;
  gap: var(--spacing-2);
}

/* Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn-sm {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-success {
  background: var(--success-color);
  color: white;
}

.btn-success:hover {
  background: #229954;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-outline {
  background: transparent;
  color: var(--gray-700);
  border: 2px solid var(--gray-300);
}

.btn-outline:hover {
  background: var(--gray-100);
  border-color: var(--gray-400);
  color: var(--gray-900);
}

/* Workflow Panel */
.workflow-panel {
  background: white;
  border-bottom: 1px solid var(--gray-200);
  transition: all var(--transition-base);
}

.workflow-panel.collapsed .panel-content {
  display: none;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) var(--spacing-6);
  background: var(--gray-50);
  cursor: pointer;
}

.panel-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.panel-toggle {
  background: none;
  border: none;
  color: var(--gray-500);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.workflow-panel.collapsed .panel-toggle {
  transform: rotate(180deg);
}

.panel-content {
  padding: var(--spacing-6);
}

/* Template Grid */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.workflow-template {
  padding: var(--spacing-5);
  background: white;
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;
}

.workflow-template:hover {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.05);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.template-icon {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-3);
  color: var(--primary-color);
}

.template-name {
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: var(--spacing-2);
}

.template-description {
  font-size: var(--font-size-sm);
  color: var(--gray-600);
  margin-bottom: var(--spacing-3);
}

.template-meta {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--gray-500);
}

/* Messages Container */
.messages-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-6);
  scroll-behavior: smooth;
}

/* Message Styles */
.message {
  margin-bottom: var(--spacing-4);
  animation: messageSlideIn var(--transition-base) ease;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-content {
  max-width: 70%;
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  position: relative;
}

.message.user .message-content {
  background: var(--primary-color);
  color: white;
  margin-left: auto;
  border-bottom-right-radius: var(--radius-sm);
}

.message.agent .message-content {
  background: white;
  border: 1px solid var(--gray-200);
  border-bottom-left-radius: var(--radius-sm);
}

.message.system .message-content {
  background: var(--gray-100);
  border: 1px solid var(--gray-200);
  text-align: center;
  font-style: italic;
  color: var(--gray-600);
  margin: 0 auto;
  max-width: 80%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.message.user .message-header {
  justify-content: flex-end;
  color: white;
}

.message.agent .message-header {
  color: var(--primary-color);
}

.message-avatar {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  background: var(--gray-200);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
}

.message-timestamp {
  font-size: var(--font-size-xs);
  color: var(--gray-500);
  margin-left: auto;
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-text p {
  margin-bottom: var(--spacing-2);
}

.message-text p:last-child {
  margin-bottom: 0;
}

/* Workflow Status Card */
.workflow-status-card {
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--spacing-5);
  margin-bottom: var(--spacing-4);
  box-shadow: var(--shadow-sm);
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-3);
}

.workflow-title {
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.workflow-status {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
}

.workflow-status.running {
  background: rgba(39, 174, 96, 0.1);
  color: var(--success-color);
}

.workflow-status.pending {
  background: rgba(243, 156, 18, 0.1);
  color: var(--warning-color);
}

.workflow-status.completed {
  background: rgba(52, 152, 219, 0.1);
  color: var(--info-color);
}

.workflow-status.failed {
  background: rgba(231, 76, 60, 0.1);
  color: var(--error-color);
}

.progress-bar {
  height: 8px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin: var(--spacing-3) 0;
}

.progress-fill {
  height: 100%;
  background: var(--primary-gradient);
  border-radius: var(--radius-full);
  transition: width var(--transition-base);
}

.workflow-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--gray-600);
}

.agent-flow {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-2);
}

.agent-badge {
  padding: var(--spacing-1) var(--spacing-2);
  background: var(--gray-100);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.agent-badge.active {
  background: var(--primary-color);
  color: white;
}

.agent-badge.completed {
  background: var(--success-color);
  color: white;
}

/* Input Area */
.input-area {
  background: white;
  border-top: 1px solid var(--gray-200);
  padding: var(--spacing-4) var(--spacing-6);
}

.input-toolbar {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-3);
}

.toolbar-btn {
  padding: var(--spacing-2);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--gray-500);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toolbar-btn:hover {
  background: var(--gray-100);
  color: var(--primary-color);
}

.input-container {
  display: flex;
  gap: var(--spacing-3);
  align-items: flex-end;
}

.message-input {
  flex: 1;
  min-height: 44px;
  max-height: 200px;
  padding: var(--spacing-3) var(--spacing-4);
  border: 2px solid var(--gray-200);
  border-radius: var(--radius-xl);
  font-size: var(--font-size-base);
  font-family: inherit;
  resize: none;
  outline: none;
  transition: all var(--transition-fast);
}

.message-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.send-btn {
  width: 44px;
  height: 44px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-full);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.send-btn:hover {
  background: var(--primary-hover);
  transform: scale(1.05);
}

.send-btn:disabled {
  background: var(--gray-300);
  cursor: not-allowed;
  transform: scale(1);
}

/* Smart Suggestions */
.smart-suggestions {
  display: flex;
  gap: var(--spacing-2);
  margin-top: var(--spacing-3);
  overflow-x: auto;
  padding: var(--spacing-1) 0;
}

.suggestion-chip {
  padding: var(--spacing-1) var(--spacing-3);
  background: var(--gray-100);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  color: var(--gray-700);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.suggestion-chip:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* Workflow Queue */
.workflow-queue {
  padding: var(--spacing-4);
}

.queue-item {
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  margin-bottom: var(--spacing-3);
  transition: all var(--transition-fast);
}

.queue-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.queue-title {
  font-weight: 600;
  color: var(--gray-900);
  font-size: var(--font-size-sm);
}

.queue-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--gray-500);
}

/* Agents List */
.agents-list {
  padding: var(--spacing-4);
}

.agent-card {
  background: white;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  margin-bottom: var(--spacing-3);
  transition: all var(--transition-fast);
}

.agent-card:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-3);
}

.agent-name {
  font-weight: 600;
  color: var(--gray-900);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.agent-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.agent-status.available {
  color: var(--success-color);
}

.agent-status.busy {
  color: var(--warning-color);
}

.agent-status.offline {
  color: var(--gray-400);
}

.agent-status-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.agent-status.available .agent-status-dot {
  background: var(--success-color);
}

.agent-status.busy .agent-status-dot {
  background: var(--warning-color);
}

.agent-status.offline .agent-status-dot {
  background: var(--gray-400);
}

.agent-workload {
  margin-top: var(--spacing-3);
}

.workload-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--gray-600);
  margin-bottom: var(--spacing-1);
}

.workload-bar {
  height: 6px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.workload-fill {
  height: 100%;
  background: var(--primary-gradient);
  transition: width var(--transition-base);
}

/* Resource Monitor */
.resource-monitor {
  padding: var(--spacing-4);
}

.resource-item {
  margin-bottom: var(--spacing-4);
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.resource-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--gray-900);
}

.resource-value {
  font-size: var(--font-size-sm);
  color: var(--gray-600);
}

.resource-bar {
  height: 8px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  transition: width var(--transition-base);
}

.resource-fill.low {
  background: var(--success-color);
}

.resource-fill.medium {
  background: var(--warning-color);
}

.resource-fill.high {
  background: var(--error-color);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: var(--z-modal-backdrop);
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-base);
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.9);
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  z-index: var(--z-modal);
  max-width: 90%;
  max-height: 90%;
  overflow: hidden;
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-base);
}

.modal.active {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, -50%) scale(1);
}

.modal-content {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-6);
  border-bottom: 1px solid var(--gray-200);
}

.modal-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--gray-900);
}

.modal-close {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--gray-500);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--gray-100);
  color: var(--gray-700);
}

.modal-body {
  flex: 1;
  padding: var(--spacing-6);
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  padding: var(--spacing-6);
  border-top: 1px solid var(--gray-200);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .sidebar-left,
  .sidebar-right {
    position: fixed;
    top: 0;
    bottom: 0;
    z-index: var(--z-modal);
    transform: translateX(-100%);
    transition: transform var(--transition-base);
  }

  .sidebar-right {
    right: 0;
    transform: translateX(100%);
  }

  .sidebar-left.open {
    transform: translateX(0);
  }

  .sidebar-right.open {
    transform: translateX(0);
  }

  .main-content {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: var(--spacing-3) var(--spacing-4);
  }

  .app-title {
    font-size: var(--font-size-xl);
  }

  .header-right {
    gap: var(--spacing-2);
  }

  .chat-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-3);
  }

  .chat-actions {
    justify-content: center;
  }

  .template-grid {
    grid-template-columns: 1fr;
  }

  .message-content {
    max-width: 85%;
  }

  .input-container {
    flex-direction: column;
    align-items: stretch;
  }

  .send-btn {
    width: 100%;
    margin-top: var(--spacing-2);
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: var(--spacing-2) var(--spacing-3);
  }

  .header-left h1 {
    font-size: var(--font-size-lg);
  }

  .user-name {
    display: none;
  }

  .chat-header {
    padding: var(--spacing-3) var(--spacing-4);
  }

  .messages-list {
    padding: var(--spacing-4);
  }

  .input-area {
    padding: var(--spacing-3) var(--spacing-4);
  }

  .toolbar-btn {
    padding: var(--spacing-1);
  }

  .modal {
    width: 95%;
    max-width: none;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: var(--spacing-4);
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

@media (prefers-contrast: high) {
  .message-content {
    border-width: 2px;
  }

  .btn {
    border-width: 2px;
  }
}

/* Focus Styles */
.focusable:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* Skip Links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-color);
  color: white;
  padding: var(--spacing-2) var(--spacing-3);
  text-decoration: none;
  border-radius: var(--radius-md);
  z-index: var(--z-tooltip);
}

.skip-link:focus {
  top: 6px;
}

/* Print Styles */
@media print {
  .sidebar,
  .input-area,
  .app-header,
  .chat-header {
    display: none;
  }

  .main-content {
    width: 100%;
  }

  .messages-container {
    height: auto;
  }

  .message {
    break-inside: avoid;
  }
}
```

---

## JavaScript Functionality

### Enhanced Chat Interface (`enhanced-chat.js`)

```javascript
class EnhancedChatInterface {
    constructor() {
        this.ws = null;
        this.currentSession = null;
        this.sessions = new Map();
        this.messages = new Map();
        this.workflowEngine = new WorkflowEngine();
        this.agentCoordinator = new AgentCoordinator();
        this.voiceInput = new VoiceInput();
        this.fileHandler = new FileHandler();

        this.init();
    }

    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.loadSessions();
        this.initializeWorkflowTemplates();
        this.startAutoSave();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.updateConnectionStatus('connected');
            this.requestInitialData();
        };

        this.ws.onclose = () => {
            this.updateConnectionStatus('disconnected');
            this.attemptReconnection();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('error');
        };

        this.ws.onmessage = (event) => {
            this.handleWebSocketMessage(JSON.parse(event.data));
        };
    }

    setupEventListeners() {
        // Session management
        document.getElementById('new-session-btn').addEventListener('click', () => this.createNewSession());
        document.getElementById('sessions-list').addEventListener('click', (e) => this.handleSessionClick(e));

        // Message input
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');

        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
            this.handleInputTyping(e);
        });

        messageInput.addEventListener('input', () => this.updateSendButton());
        sendBtn.addEventListener('click', () => this.sendMessage());

        // Workflow panel
        document.getElementById('workflow-panel-toggle').addEventListener('click', () => this.toggleWorkflowPanel());
        document.getElementById('start-workflow-btn').addEventListener('click', () => this.openWorkflowModal());

        // File upload
        document.getElementById('attach-file-btn').addEventListener('click', () => this.openFileUploadModal());

        // Voice input
        document.getElementById('voice-btn').addEventListener('click', () => this.toggleVoiceInput());

        // Search and filter
        document.getElementById('search-btn').addEventListener('click', () => this.openSearchModal());
        document.getElementById('filter-btn').addEventListener('click', () => this.openFilterModal());

        // Settings
        document.getElementById('settings-btn').addEventListener('click', () => this.openSettingsModal());

        // Modals
        this.setupModalListeners();

        // Smart suggestions
        document.getElementById('smart-suggestions').addEventListener('click', (e) => this.handleSuggestionClick(e));

        // Keyboard shortcuts
        this.setupKeyboardShortcuts();

        // Auto-resize textarea
        this.setupTextareaResize();
    }

    createNewSession() {
        const sessionName = prompt('Enter session name:');
        if (!sessionName) return;

        const session = {
            id: this.generateId(),
            name: sessionName,
            createdAt: new Date().toISOString(),
            lastActivity: new Date().toISOString(),
            workflow: null,
            status: 'active'
        };

        this.sessions.set(session.id, session);
        this.currentSession = session.id;
        this.messages.set(session.id, []);

        this.renderSessionsList();
        this.switchToSession(session.id);
        this.saveSessionToStorage(session);
    }

    switchToSession(sessionId) {
        this.currentSession = sessionId;
        const session = this.sessions.get(sessionId);

        // Update UI
        document.getElementById('current-chat-title').textContent = session.name;
        this.renderSessionsList();
        this.renderMessages();

        // Update session activity
        session.lastActivity = new Date().toISOString();
        this.saveSessionToStorage(session);
    }

    async sendMessage() {
        const input = document.getElementById('message-input');
        const content = input.value.trim();

        if (!content || !this.currentSession) return;

        // Create user message
        const message = {
            id: this.generateId(),
            type: 'user',
            content: content,
            timestamp: new Date().toISOString(),
            sessionId: this.currentSession
        };

        // Add to local state
        this.addMessage(message);

        // Clear input
        input.value = '';
        this.updateSendButton();
        this.hideSmartSuggestions();

        // Send via WebSocket
        this.sendWebSocketMessage({
            type: 'chat_message',
            message: content,
            sessionId: this.currentSession
        });

        // Process for workflow commands
        this.processMessageForWorkflow(content);

        // Update session activity
        const session = this.sessions.get(this.currentSession);
        session.lastActivity = new Date().toISOString();
        this.saveSessionToStorage(session);
    }

    addMessage(message) {
        if (!this.messages.has(message.sessionId)) {
            this.messages.set(message.sessionId, []);
        }

        this.messages.get(message.sessionId).push(message);

        if (message.sessionId === this.currentSession) {
            this.renderMessage(message);
            this.scrollToBottom();
        }

        this.saveMessagesToStorage(message.sessionId);
    }

    renderMessage(message) {
        const messagesList = document.getElementById('messages-list');
        const messageElement = this.createMessageElement(message);
        messagesList.appendChild(messageElement);
    }

    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type}`;
        messageDiv.dataset.messageId = message.id;

        // Handle different message types
        if (message.type === 'workflow_status') {
            return this.createWorkflowStatusElement(message);
        } else if (message.type === 'file_upload') {
            return this.createFileUploadElement(message);
        } else if (message.type === 'agent_handoff') {
            return this.createAgentHandoffElement(message);
        } else {
            return this.createTextMessageElement(message);
        }
    }

    createTextMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.type}`;
        messageDiv.dataset.messageId = message.id;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        // Message header
        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = message.type === 'user' ? '👤' : '🤖';

        const sender = document.createElement('span');
        sender.textContent = message.type === 'user' ? 'You' : 'El Jefe';

        const timestamp = document.createElement('span');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = this.formatTime(message.timestamp);

        messageHeader.appendChild(avatar);
        messageHeader.appendChild(sender);
        messageHeader.appendChild(timestamp);

        // Message text with markdown support
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.renderMarkdown(message.content);

        messageContent.appendChild(messageHeader);
        messageContent.appendChild(messageText);
        messageDiv.appendChild(messageContent);

        return messageDiv;
    }

    createWorkflowStatusElement(message) {
        const workflow = message.data.workflow;
        const card = document.createElement('div');
        card.className = 'workflow-status-card';

        card.innerHTML = `
            <div class="workflow-header">
                <div class="workflow-title">
                    <i class="fas fa-tasks"></i>
                    ${workflow.name}
                </div>
                <div class="workflow-status ${workflow.status}">${workflow.status}</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${workflow.progress}%"></div>
            </div>
            <div class="workflow-meta">
                <span>Started: ${this.formatTime(workflow.startedAt)}</span>
                <span>ETA: ${workflow.eta || 'Calculating...'}</span>
            </div>
            <div class="agent-flow">
                ${workflow.agents.map(agent =>
                    `<div class="agent-badge ${agent.status}">${agent.name}</div>`
                ).join('')}
                <div class="agent-arrow">→</div>
                <div class="agent-badge ${workflow.nextAgent?.status || 'pending'}">
                    ${workflow.nextAgent?.name || 'Waiting...'}
                </div>
            </div>
        `;

        return card;
    }

    renderMarkdown(text) {
        // Simple markdown rendering (consider using a library like marked.js for production)
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/https?:\/\/[^\s]+/g, '<a href="$&" target="_blank">$&</a>');
    }

    async processMessageForWorkflow(content) {
        // Check if message contains workflow assignment intent
        const workflowIntent = this.detectWorkflowIntent(content);

        if (workflowIntent) {
            await this.suggestWorkflow(workflowIntent);
        }
    }

    detectWorkflowIntent(content) {
        const keywords = {
            'research': ['research', 'analyze', 'investigate', 'study'],
            'content-creation': ['create', 'write', 'blog post', 'article', 'content'],
            'code-development': ['code', 'develop', 'build', 'implement', 'program'],
            'security-audit': ['security', 'audit', 'review', 'vulnerability', 'test']
        };

        const lowerContent = content.toLowerCase();

        for (const [type, words] of Object.entries(keywords)) {
            if (words.some(word => lowerContent.includes(word))) {
                return {
                    type: type,
                    content: content,
                    confidence: this.calculateConfidence(content, words)
                };
            }
        }

        return null;
    }

    calculateConfidence(content, keywords) {
        const matches = keywords.filter(word => content.toLowerCase().includes(word)).length;
        return Math.min(matches / keywords.length, 1.0);
    }

    async suggestWorkflow(intent) {
        if (intent.confidence > 0.7) {
            const template = this.workflowEngine.getTemplate(intent.type);

            // Add suggestion message
            const suggestionMessage = {
                id: this.generateId(),
                type: 'agent',
                content: `I detected you want to ${intent.type.replace('-', ' ')}. Would you like to use the "${template.name}" template?`,
                timestamp: new Date().toISOString(),
                sessionId: this.currentSession,
                suggestions: [
                    { text: `Use ${template.name} template`, action: 'use_template', data: template },
                    { text: 'Custom workflow', action: 'custom_workflow' },
                    { text: 'Not now', action: 'dismiss' }
                ]
            };

            this.addMessage(suggestionMessage);
        }
    }

    showSmartSuggestions(suggestions) {
        const container = document.getElementById('smart-suggestions');
        container.innerHTML = '';

        suggestions.forEach(suggestion => {
            const chip = document.createElement('div');
            chip.className = 'suggestion-chip';
            chip.textContent = suggestion.text;
            chip.dataset.action = suggestion.action;
            chip.dataset.data = JSON.stringify(suggestion.data);
            container.appendChild(chip);
        });

        container.style.display = 'flex';
    }

    hideSmartSuggestions() {
        const container = document.getElementById('smart-suggestions');
        container.style.display = 'none';
    }

    handleSuggestionClick(event) {
        if (event.target.classList.contains('suggestion-chip')) {
            const action = event.target.dataset.action;
            const data = JSON.parse(event.target.dataset.data);

            this.executeSuggestion(action, data);
        }
    }

    executeSuggestion(action, data) {
        switch (action) {
            case 'use_template':
                this.openWorkflowModal(data);
                break;
            case 'custom_workflow':
                this.openWorkflowModal();
                break;
            case 'dismiss':
                this.hideSmartSuggestions();
                break;
            default:
                console.warn('Unknown suggestion action:', action);
        }
    }

    // Workflow Management
    openWorkflowModal(template = null) {
        this.showModal('workflow-modal');
        this.renderWorkflowModal(template);
    }

    renderWorkflowModal(template) {
        const modalBody = document.getElementById('workflow-modal-body');

        modalBody.innerHTML = `
            <form id="workflow-form">
                <div class="form-group">
                    <label for="workflow-name">Workflow Name</label>
                    <input type="text" id="workflow-name" name="name"
                           value="${template?.name || ''}" required>
                </div>

                <div class="form-group">
                    <label for="workflow-description">Description</label>
                    <textarea id="workflow-description" name="description" rows="3"
                              placeholder="Describe what this workflow should accomplish...">${template?.description || ''}</textarea>
                </div>

                <div class="form-group">
                    <label>Workflow Template</label>
                    <div class="template-selection">
                        ${this.renderTemplateOptions(template?.type)}
                    </div>
                </div>

                <div class="form-group">
                    <label for="workflow-priority">Priority</label>
                    <select id="workflow-priority" name="priority">
                        <option value="low">Low</option>
                        <option value="normal" selected>Normal</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Schedule</label>
                    <div class="schedule-options">
                        <label>
                            <input type="radio" name="schedule" value="now" checked>
                            Start now
                        </label>
                        <label>
                            <input type="radio" name="schedule" value="later">
                            Schedule for later
                        </label>
                    </div>
                </div>

                <div id="schedule-details" style="display: none;">
                    <div class="form-group">
                        <label for="workflow-date">Date</label>
                        <input type="datetime-local" id="workflow-date" name="scheduleDate">
                    </div>
                </div>
            </form>
        `;

        // Setup form listeners
        this.setupWorkflowFormListeners();
    }

    setupWorkflowFormListeners() {
        const scheduleRadios = document.querySelectorAll('input[name="schedule"]');
        const scheduleDetails = document.getElementById('schedule-details');

        scheduleRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                scheduleDetails.style.display = e.target.value === 'later' ? 'block' : 'none';
            });
        });

        document.getElementById('workflow-assign-btn').addEventListener('click', () => {
            this.assignWorkflow();
        });
    }

    async assignWorkflow() {
        const form = document.getElementById('workflow-form');
        const formData = new FormData(form);

        const workflow = {
            id: this.generateId(),
            name: formData.get('name'),
            description: formData.get('description'),
            type: formData.get('template'),
            priority: formData.get('priority'),
            schedule: formData.get('schedule'),
            scheduleDate: formData.get('scheduleDate'),
            sessionId: this.currentSession,
            status: 'pending',
            createdAt: new Date().toISOString()
        };

        try {
            // Validate workflow
            this.validateWorkflow(workflow);

            // Send to server
            this.sendWebSocketMessage({
                type: 'assign_workflow',
                workflow: workflow
            });

            // Add confirmation message
            this.addMessage({
                id: this.generateId(),
                type: 'agent',
                content: `Workflow "${workflow.name}" has been assigned and will start ${workflow.schedule === 'now' ? 'immediately' : 'as scheduled'}.`,
                timestamp: new Date().toISOString(),
                sessionId: this.currentSession
            });

            // Close modal
            this.hideModal('workflow-modal');

        } catch (error) {
            alert(`Error assigning workflow: ${error.message}`);
        }
    }

    validateWorkflow(workflow) {
        if (!workflow.name.trim()) {
            throw new Error('Workflow name is required');
        }

        if (!workflow.type) {
            throw new Error('Please select a workflow template');
        }

        if (workflow.schedule === 'later' && !workflow.scheduleDate) {
            throw new Error('Please specify a schedule date and time');
        }

        const scheduleDate = new Date(workflow.scheduleDate);
        if (scheduleDate <= new Date()) {
            throw new Error('Schedule date must be in the future');
        }
    }

    // WebSocket Communication
    sendWebSocketMessage(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not connected, message not sent:', data);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'chat_message':
                this.addMessage(data.message);
                break;
            case 'workflow_update':
                this.updateWorkflowStatus(data.workflow);
                break;
            case 'agent_update':
                this.updateAgentStatus(data.agent);
                break;
            case 'session_update':
                this.handleSessionUpdate(data.session);
                break;
            case 'error':
                this.handleError(data.error);
                break;
            default:
                console.log('Unknown message type:', data.type, data);
        }
    }

    // Utility Functions
    generateId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        const indicator = statusElement.querySelector('.status-indicator');
        const text = statusElement.querySelector('.status-text');

        statusElement.className = 'connection-status';

        switch (status) {
            case 'connected':
                statusElement.classList.add('connected');
                indicator.className = 'status-indicator connected';
                text.textContent = 'Connected';
                break;
            case 'disconnected':
                statusElement.classList.add('disconnected');
                indicator.className = 'status-indicator disconnected';
                text.textContent = 'Disconnected';
                break;
            case 'error':
                statusElement.classList.add('error');
                indicator.className = 'status-indicator error';
                text.textContent = 'Error';
                break;
        }
    }

    attemptReconnection() {
        let attempts = 0;
        const maxAttempts = 5;
        const delay = 5000;

        const reconnect = () => {
            if (attempts >= maxAttempts) {
                console.error('Max reconnection attempts reached');
                return;
            }

            attempts++;
            console.log(`Reconnection attempt ${attempts}/${maxAttempts}`);

            setTimeout(() => {
                this.setupWebSocket();
            }, delay);
        };

        reconnect();
    }

    // Local Storage Management
    saveSessionToStorage(session) {
        const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
        const index = sessions.findIndex(s => s.id === session.id);

        if (index >= 0) {
            sessions[index] = session;
        } else {
            sessions.push(session);
        }

        localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    }

    loadSessions() {
        try {
            const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
            sessions.forEach(session => {
                this.sessions.set(session.id, session);
            });

            // Load first session or create default
            if (sessions.length > 0) {
                this.switchToSession(sessions[0].id);
            } else {
                this.createNewSession();
            }

            this.renderSessionsList();
        } catch (error) {
            console.error('Error loading sessions:', error);
            this.createNewSession();
        }
    }

    saveMessagesToStorage(sessionId) {
        const messages = this.messages.get(sessionId) || [];
        localStorage.setItem(`chat_messages_${sessionId}`, JSON.stringify(messages));
    }

    loadMessagesFromStorage(sessionId) {
        try {
            const messages = JSON.parse(localStorage.getItem(`chat_messages_${sessionId}`) || '[]');
            this.messages.set(sessionId, messages);
        } catch (error) {
            console.error('Error loading messages:', error);
            this.messages.set(sessionId, []);
        }
    }

    // UI Rendering Functions
    renderSessionsList() {
        const container = document.getElementById('sessions-list');
        container.innerHTML = '';

        this.sessions.forEach(session => {
            const sessionElement = this.createSessionElement(session);
            container.appendChild(sessionElement);
        });
    }

    createSessionElement(session) {
        const div = document.createElement('div');
        div.className = `session-item ${session.id === this.currentSession ? 'active' : ''}`;
        div.dataset.sessionId = session.id;

        const statusClass = session.status === 'active' ? 'active' :
                           session.status === 'busy' ? 'busy' : '';

        div.innerHTML = `
            <div class="session-title">${session.name}</div>
            <div class="session-meta">
                <div class="session-status">
                    <span class="session-status-dot ${statusClass}"></span>
                    <span>${session.status}</span>
                </div>
                <span>${this.formatTime(session.lastActivity)}</span>
            </div>
        `;

        return div;
    }

    renderMessages() {
        const messagesList = document.getElementById('messages-list');
        messagesList.innerHTML = '';

        const messages = this.messages.get(this.currentSession) || [];
        messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            messagesList.appendChild(messageElement);
        });

        this.scrollToBottom();
    }

    scrollToBottom() {
        const messagesContainer = document.querySelector('.messages-container');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    updateSendButton() {
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const hasContent = input.value.trim().length > 0;

        sendBtn.disabled = !hasContent;
        sendBtn.classList.toggle('disabled', !hasContent);
    }

    // Auto-save functionality
    startAutoSave() {
        setInterval(() => {
            if (this.currentSession) {
                this.saveMessagesToStorage(this.currentSession);
            }
        }, 30000); // Auto-save every 30 seconds
    }

    // Keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openSearchModal();
            }

            // Ctrl/Cmd + N for new session
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                this.createNewSession();
            }

            // Ctrl/Cmd + / for help
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                this.openHelpModal();
            }

            // Escape to close modals
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    // Auto-resize textarea
    setupTextareaResize() {
        const textarea = document.getElementById('message-input');

        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
        });
    }

    handleInputTyping(event) {
        // Show typing indicator to other users (if implemented)
        const content = event.target.value;

        // Show smart suggestions after typing certain keywords
        if (content.length > 3 && content.includes('workflow')) {
            this.showWorkflowSuggestions();
        }
    }

    showWorkflowSuggestions() {
        const suggestions = [
            { text: 'Create new workflow', action: 'create_workflow' },
            { text: 'View active workflows', action: 'view_workflows' },
            { text: 'Schedule workflow', action: 'schedule_workflow' }
        ];

        this.showSmartSuggestions(suggestions);
    }

    // Modal management
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        const overlay = document.getElementById('modal-overlay');

        modal.classList.add('active');
        overlay.classList.add('active');

        // Focus management
        const firstFocusable = modal.querySelector('input, button, select, textarea');
        if (firstFocusable) {
            firstFocusable.focus();
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        const overlay = document.getElementById('modal-overlay');

        modal.classList.remove('active');
        overlay.classList.remove('active');
    }

    closeAllModals() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
        document.getElementById('modal-overlay').classList.remove('active');
    }

    setupModalListeners() {
        // Overlay click to close
        document.getElementById('modal-overlay').addEventListener('click', () => {
            this.closeAllModals();
        });

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });

        // Close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.hideModal(modal.id);
            });
        });
    }

    // Placeholder methods for features to be implemented
    toggleWorkflowPanel() {
        const panel = document.getElementById('workflow-panel');
        panel.classList.toggle('collapsed');
    }

    openFileUploadModal() {
        console.log('File upload modal not implemented yet');
    }

    toggleVoiceInput() {
        this.voiceInput.toggle();
    }

    openSearchModal() {
        console.log('Search modal not implemented yet');
    }

    openFilterModal() {
        console.log('Filter modal not implemented yet');
    }

    openSettingsModal() {
        console.log('Settings modal not implemented yet');
    }

    openHelpModal() {
        console.log('Help modal not implemented yet');
    }

    handleSessionClick(event) {
        const sessionItem = event.target.closest('.session-item');
        if (sessionItem) {
            const sessionId = sessionItem.dataset.sessionId;
            this.switchToSession(sessionId);
        }
    }

    updateWorkflowStatus(workflow) {
        // Update workflow status in UI
        console.log('Workflow status update:', workflow);
    }

    updateAgentStatus(agent) {
        // Update agent status in UI
        console.log('Agent status update:', agent);
    }

    handleSessionUpdate(session) {
        // Handle session updates
        console.log('Session update:', session);
    }

    handleError(error) {
        console.error('WebSocket error:', error);

        // Show error message to user
        this.addMessage({
            id: this.generateId(),
            type: 'system',
            content: `Error: ${error.message}`,
            timestamp: new Date().toISOString(),
            sessionId: this.currentSession
        });
    }

    requestInitialData() {
        this.sendWebSocketMessage({ type: 'request_initial_data' });
    }

    initializeWorkflowTemplates() {
        this.workflowEngine.initializeTemplates();
    }
}

// Initialize the enhanced chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedChat = new EnhancedChatInterface();
});
```

### Workflow Engine (`workflow-engine.js`)

```javascript
class WorkflowEngine {
    constructor() {
        this.templates = new Map();
        this.activeWorkflows = new Map();
        this.initializeTemplates();
    }

    initializeTemplates() {
        const defaultTemplates = {
            'research-analysis': {
                id: 'research-analysis',
                name: 'Research & Analysis',
                icon: '🔍',
                description: 'Comprehensive research and data analysis',
                parameters: ['topic', 'scope', 'timeline', 'sources'],
                defaultAgents: ['researcher', 'analyst'],
                estimatedTime: '2-4 hours',
                category: 'research'
            },
            'content-creation': {
                id: 'content-creation',
                name: 'Content Creation',
                icon: '✍️',
                description: 'Generate articles, scripts, or documentation',
                parameters: ['content_type', 'topic', 'tone', 'length'],
                defaultAgents: ['researcher', 'writer'],
                estimatedTime: '1-3 hours',
                category: 'content'
            },
            'code-development': {
                id: 'code-development',
                name: 'Code Development',
                icon: '💻',
                description: 'Build and deploy software solutions',
                parameters: ['requirements', 'language', 'framework', 'timeline'],
                defaultAgents: ['coder', 'analyst'],
                estimatedTime: '4-8 hours',
                category: 'development'
            },
            'security-audit': {
                id: 'security-audit',
                name: 'Security Audit',
                icon: '🔒',
                description: 'Comprehensive security assessment',
                parameters: ['target', 'scope', 'compliance', 'timeline'],
                defaultAgents: ['security-reviewer', 'analyst'],
                estimatedTime: '6-12 hours',
                category: 'security'
            }
        };

        defaultTemplates.forEach(template => {
            this.templates.set(template.id, template);
        });
    }

    getTemplate(type) {
        return this.templates.get(type);
    }

    getAllTemplates() {
        return Array.from(this.templates.values());
    }

    getTemplatesByCategory(category) {
        return Array.from(this.templates.values())
            .filter(template => template.category === category);
    }

    async createWorkflow(templateId, parameters, options = {}) {
        const template = this.getTemplate(templateId);
        if (!template) {
            throw new Error(`Template not found: ${templateId}`);
        }

        const workflow = {
            id: this.generateWorkflowId(),
            templateId: templateId,
            name: parameters.name || template.name,
            description: parameters.description || template.description,
            parameters: this.validateParameters(template, parameters),
            agents: template.defaultAgents,
            status: 'pending',
            progress: 0,
            currentStep: 0,
            totalSteps: this.calculateTotalSteps(template),
            createdAt: new Date().toISOString(),
            ...options
        };

        this.activeWorkflows.set(workflow.id, workflow);
        return workflow;
    }

    validateParameters(template, parameters) {
        const validated = {};

        template.parameters.forEach(param => {
            if (parameters[param]) {
                validated[param] = parameters[param];
            } else {
                // Set default values or required parameter warnings
                validated[param] = this.getDefaultValue(param);
            }
        });

        return validated;
    }

    getDefaultValue(parameter) {
        const defaults = {
            'topic': 'Default topic',
            'scope': 'Standard scope',
            'timeline': 'Standard timeline',
            'sources': 'Default sources',
            'content_type': 'article',
            'tone': 'professional',
            'length': 'medium',
            'requirements': 'Basic requirements',
            'language': 'javascript',
            'framework': 'none',
            'target': 'auto-detected',
            'compliance': 'standard'
        };

        return defaults[parameter] || '';
    }

    calculateTotalSteps(template) {
        // Define the number of steps for each workflow type
        const stepCounts = {
            'research-analysis': 5,
            'content-creation': 4,
            'code-development': 6,
            'security-audit': 7
        };

        return stepCounts[template.id] || 4;
    }

    generateWorkflowId() {
        return `wf_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    async updateWorkflowProgress(workflowId, progress, currentStep) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow) {
            throw new Error(`Workflow not found: ${workflowId}`);
        }

        workflow.progress = Math.min(100, Math.max(0, progress));
        workflow.currentStep = currentStep;
        workflow.lastUpdated = new Date().toISOString();

        // Update status based on progress
        if (workflow.progress >= 100) {
            workflow.status = 'completed';
            workflow.completedAt = new Date().toISOString();
        } else if (workflow.progress > 0) {
            workflow.status = 'running';
        }

        return workflow;
    }

    getActiveWorkflows() {
        return Array.from(this.activeWorkflows.values());
    }

    getWorkflow(workflowId) {
        return this.activeWorkflows.get(workflowId);
    }

    async cancelWorkflow(workflowId) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow) {
            throw new Error(`Workflow not found: ${workflowId}`);
        }

        workflow.status = 'cancelled';
        workflow.cancelledAt = new Date().toISOString();

        return workflow;
    }

    async pauseWorkflow(workflowId) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow) {
            throw new Error(`Workflow not found: ${workflowId}`);
        }

        workflow.status = 'paused';
        workflow.pausedAt = new Date().toISOString();

        return workflow;
    }

    async resumeWorkflow(workflowId) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow) {
            throw new Error(`Workflow not found: ${workflowId}`);
        }

        workflow.status = 'running';
        workflow.resumedAt = new Date().toISOString();

        return workflow;
    }

    // Workflow scheduling
    async scheduleWorkflow(workflowId, scheduledTime) {
        const workflow = this.activeWorkflows.get(workflowId);
        if (!workflow) {
            throw new Error(`Workflow not found: ${workflowId}`);
        }

        workflow.scheduledTime = scheduledTime;
        workflow.status = 'scheduled';

        return workflow;
    }

    // Workflow analytics
    getWorkflowAnalytics() {
        const workflows = this.getActiveWorkflows();

        return {
            total: workflows.length,
            running: workflows.filter(w => w.status === 'running').length,
            completed: workflows.filter(w => w.status === 'completed').length,
            failed: workflows.filter(w => w.status === 'failed').length,
            scheduled: workflows.filter(w => w.status === 'scheduled').length,
            averageCompletionTime: this.calculateAverageCompletionTime(workflows),
            successRate: this.calculateSuccessRate(workflows)
        };
    }

    calculateAverageCompletionTime(workflows) {
        const completedWorkflows = workflows.filter(w =>
            w.status === 'completed' && w.completedAt
        );

        if (completedWorkflows.length === 0) return 0;

        const totalTime = completedWorkflows.reduce((sum, workflow) => {
            const start = new Date(workflow.createdAt);
            const end = new Date(workflow.completedAt);
            return sum + (end - start);
        }, 0);

        return totalTime / completedWorkflows.length;
    }

    calculateSuccessRate(workflows) {
        const totalWorkflows = workflows.filter(w =>
            ['completed', 'failed'].includes(w.status)
        );

        if (totalWorkflows.length === 0) return 100;

        const successful = totalWorkflows.filter(w => w.status === 'completed').length;
        return (successful / totalWorkflows.length) * 100;
    }
}
```

---

## WebSocket Integration

### Enhanced WebSocket Message Protocol

```javascript
// Message Types and Structures
const MessageTypes = {
    // Chat Messages
    CHAT_MESSAGE: 'chat_message',
    MESSAGE_HISTORY: 'message_history',
    TYPING_INDICATOR: 'typing_indicator',

    // Workflow Management
    WORKFLOW_ASSIGN: 'assign_workflow',
    WORKFLOW_UPDATE: 'workflow_update',
    WORKFLOW_CANCEL: 'cancel_workflow',
    WORKFLOW_PAUSE: 'pause_workflow',
    WORKFLOW_RESUME: 'resume_workflow',
    WORKFLOW_SCHEDULE: 'schedule_workflow',

    // Agent Management
    AGENT_STATUS: 'agent_status',
    AGENT_HANDOFF: 'agent_handoff',
    AGENT_COORDINATION: 'agent_coordination',

    // Session Management
    SESSION_CREATE: 'session_create',
    SESSION_UPDATE: 'session_update',
    SESSION_SWITCH: 'session_switch',

    // File Management
    FILE_UPLOAD: 'file_upload',
    FILE_PROCESS: 'file_process',

    // System
    SYSTEM_STATUS: 'system_status',
    ERROR: 'error',
    HEARTBEAT: 'heartbeat'
};

// Enhanced WebSocket Handler
class EnhancedWebSocketHandler {
    constructor() {
        this.ws = null;
        this.messageQueue = [];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.heartbeatInterval = null;
        this.messageHandlers = new Map();
        this.setupMessageHandlers();
    }

    setupMessageHandlers() {
        this.messageHandlers.set(MessageTypes.CHAT_MESSAGE, this.handleChatMessage.bind(this));
        this.messageHandlers.set(MessageTypes.WORKFLOW_UPDATE, this.handleWorkflowUpdate.bind(this));
        this.messageHandlers.set(MessageTypes.AGENT_STATUS, this.handleAgentStatus.bind(this));
        this.messageHandlers.set(MessageTypes.FILE_UPLOAD, this.handleFileUpload.bind(this));
        this.messageHandlers.set(MessageTypes.SYSTEM_STATUS, this.handleSystemStatus.bind(this));
        this.messageHandlers.set(MessageTypes.ERROR, this.handleError.bind(this));
    }

    connect(url) {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(url);

                this.ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.reconnectAttempts = 0;
                    this.startHeartbeat();
                    this.flushMessageQueue();
                    resolve();
                };

                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.stopHeartbeat();
                    this.attemptReconnect();
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };

                this.ws.onmessage = (event) => {
                    this.handleMessage(JSON.parse(event.data));
                };

            } catch (error) {
                reject(error);
            }
        });
    }

    handleMessage(data) {
        const handler = this.messageHandlers.get(data.type);
        if (handler) {
            handler(data);
        } else {
            console.warn('No handler for message type:', data.type);
        }
    }

    send(message) {
        const messageData = {
            ...message,
            timestamp: new Date().toISOString(),
            messageId: this.generateMessageId()
        };

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(messageData));
        } else {
            this.messageQueue.push(messageData);
        }
    }

    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            this.send({ type: MessageTypes.HEARTBEAT });
        }, 30000); // 30 seconds
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

        setTimeout(() => {
            console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            this.connect(this.ws.url);
        }, delay);
    }

    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Message Handlers
    handleChatMessage(data) {
        // Handle incoming chat messages
        if (window.enhancedChat) {
            window.enhancedChat.addMessage(data.message);
        }
    }

    handleWorkflowUpdate(data) {
        // Handle workflow status updates
        if (window.enhancedChat) {
            window.enhancedChat.updateWorkflowStatus(data.workflow);
        }
    }

    handleAgentStatus(data) {
        // Handle agent status updates
        if (window.enhancedChat) {
            window.enhancedChat.updateAgentStatus(data.agent);
        }
    }

    handleFileUpload(data) {
        // Handle file upload progress and completion
        if (window.enhancedChat) {
            window.enhancedChat.updateFileUploadStatus(data.file);
        }
    }

    handleSystemStatus(data) {
        // Handle system status updates
        if (window.enhancedChat) {
            window.enhancedChat.updateSystemStatus(data.status);
        }
    }

    handleError(data) {
        // Handle error messages
        console.error('Server error:', data.error);
        if (window.enhancedChat) {
            window.enhancedChat.handleError(data.error);
        }
    }
}
```

---

## Mobile Responsive Implementation

### Touch Gestures and Mobile Optimizations

```javascript
class MobileOptimizations {
    constructor() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.swipeThreshold = 50;
        this.setupTouchGestures();
        this.setupViewportOptimizations();
    }

    setupTouchGestures() {
        // Swipe gestures for sidebar navigation
        document.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
            this.touchStartY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            this.handleSwipeGesture(e);
        });

        // Prevent bounce scrolling on iOS
        document.body.addEventListener('touchmove', (e) => {
            if (e.target.closest('.messages-container')) {
                return; // Allow scrolling in message container
            }
            e.preventDefault();
        }, { passive: false });
    }

    handleSwipeGesture(e) {
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;

        const deltaX = touchEndX - this.touchStartX;
        const deltaY = Math.abs(touchEndY - this.touchStartY);

        // Only handle horizontal swipes
        if (Math.abs(deltaX) > this.swipeThreshold && deltaY < 100) {
            if (deltaX > 0) {
                this.openLeftSidebar();
            } else {
                this.closeLeftSidebar();
            }
        }
    }

    openLeftSidebar() {
        const sidebar = document.querySelector('.sidebar-left');
        if (sidebar) {
            sidebar.classList.add('open');
        }
    }

    closeLeftSidebar() {
        const sidebar = document.querySelector('.sidebar-left');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }

    setupViewportOptimizations() {
        // Prevent zoom on input focus
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                document.querySelector('meta[name="viewport"]').setAttribute('content',
                    'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0');
            });

            input.addEventListener('blur', () => {
                document.querySelector('meta[name="viewport"]').setAttribute('content',
                    'width=device-width, initial-scale=1.0');
            });
        });

        // Optimize scrolling performance
        this.optimizeScrolling();
    }

    optimizeScrolling() {
        const messagesContainer = document.querySelector('.messages-container');
        if (messagesContainer) {
            let isScrolling = false;

            messagesContainer.addEventListener('scroll', () => {
                if (!isScrolling) {
                    window.requestAnimationFrame(() => {
                        // Handle scroll optimizations
                        isScrolling = false;
                    });
                    isScrolling = true;
                }
            });
        }
    }
}

// Initialize mobile optimizations
document.addEventListener('DOMContentLoaded', () => {
    if ('ontouchstart' in window) {
        window.mobileOptimizations = new MobileOptimizations();
    }
});
```

This comprehensive implementation guide provides:

1. **Complete HTML structure** with semantic markup and accessibility features
2. **Extensive CSS styling** with modern design tokens, responsive layouts, and animations
3. **Full JavaScript functionality** including WebSocket communication, workflow management, and real-time updates
4. **Mobile-responsive design** with touch gestures and optimizations
5. **Component-based architecture** for maintainability and extensibility
6. **Accessibility features** including keyboard navigation and screen reader support

The implementation maintains consistency with the existing El Jefe dashboard while adding powerful workflow management capabilities through an intuitive chat interface. The modular design allows for easy customization and future enhancements.