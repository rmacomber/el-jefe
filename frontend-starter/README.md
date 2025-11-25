# El Jefe Dashboard - Modern Frontend Implementation

A modern, responsive React-based monitoring dashboard for El Jefe agents, built with TypeScript, Material-UI, and real-time WebSocket updates.

## 🚀 Features

- **Real-time Updates**: Live WebSocket connection for instant agent and workflow status updates
- **Responsive Design**: Mobile-first approach with touch-optimized interactions
- **Data Visualization**: Interactive charts and metrics with Material-UI X-Charts
- **Accessibility**: WCAG 2.1 AA compliant with comprehensive ARIA support
- **Performance**: Optimized with code splitting, lazy loading, and virtualization
- **Dark Mode**: Automatic theme detection with manual override
- **Search & Filtering**: Advanced filtering for agents and workflows
- **Chat Integration**: Enhanced El Jefe chat with markdown support

## 🛠️ Tech Stack

### Core Technologies
- **React 18** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **Material-UI (MUI)** for consistent design system
- **Redux Toolkit** for state management
- **React Query** for server state management
- **Socket.IO** for WebSocket communication

### Development Tools
- **ESLint** + **Prettier** for code quality
- **Vitest** for unit testing
- **Testing Library** for component testing
- **TypeScript** for static type checking

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd el-jefe-dashboard

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

The development server will start at `http://localhost:3000` with proxy configuration for the backend API at `http://localhost:8080`.

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
# API Configuration
VITE_API_URL=http://localhost:8080
VITE_WS_URL=ws://localhost:8080/ws

# Feature Flags
VITE_ENABLE_DARK_MODE=true
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_SOUND_EFFECTS=false

# Performance Settings
VITE_REFRESH_INTERVAL=30000
VITE_MAX_RETRIES=5
```

### Backend Integration

The dashboard is designed to work with the existing Python backend. Ensure the monitoring dashboard is running:

```bash
# Start the Python backend
python monitoring_dashboard.py
```

## 🏗️ Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components (Button, Card, etc.)
│   ├── layout/          # Layout components (Header, Sidebar, etc.)
│   └── features/        # Feature-specific components
│       ├── Dashboard/   # Dashboard metrics and overview
│       ├── Agents/      # Agent management and monitoring
│       ├── Workflows/   # Workflow visualization and control
│       └── Chat/        # El Jefe chat interface
├── pages/               # Route components
├── hooks/               # Custom React hooks
├── store/               # Redux store configuration
├── services/            # API and WebSocket services
├── utils/               # Utility functions
├── types/               # TypeScript type definitions
├── styles/              # Global styles and theme
└── assets/              # Static assets
```

## 🎯 Key Components

### MetricCard
Displays key performance indicators with trend information:

```tsx
<MetricCard
  title="Active Agents"
  value={activeAgents}
  change={5}
  changeType="increase"
  icon={<AgentsIcon />}
  loading={false}
/>
```

### StatusIndicator
Visual status indicator with pulse animation:

```tsx
<StatusIndicator
  status="online"
  pulse={true}
  size="medium"
/>
```

### WebSocket Hook
Custom hook for real-time updates:

```tsx
const { isConnected, lastMessage, send } = useWebSocket('ws://localhost:8080/ws');
```

## 🎨 Theming

The dashboard supports light, dark, and auto themes. The theme configuration is in `src/styles/theme.ts`:

```tsx
// Use auto theme (based on system preference)
const theme = getTheme('auto');

// Force specific theme
const darkTheme = createTheme({ palette: { mode: 'dark' } });
```

### Custom Colors

The theme maintains the original purple gradient aesthetic:

- Primary: `#667eea` to `#764ba2`
- Success: `#27ae60`
- Warning: `#f39c12`
- Error: `#e74c3c`

## 📱 Mobile Optimization

### Responsive Breakpoints
- **xs**: 0px - 599px
- **sm**: 600px - 899px
- **md**: 900px - 1199px
- **lg**: 1200px - 1535px
- **xl**: 1536px+

### Touch Interactions
- Minimum touch targets: 44px
- Swipe gestures for navigation
- Pull-to-refresh functionality
- Touch-optimized controls

## ♿ Accessibility

### WCAG 2.1 AA Compliance
- Semantic HTML structure
- Comprehensive ARIA labels
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management

### Keyboard Shortcuts
- `Tab`: Navigate through interactive elements
- `Enter/Space`: Activate buttons and links
- `Escape`: Close modals and dropdowns
- `Arrow Keys`: Navigate lists and menus

## 🚀 Performance

### Bundle Optimization
- Code splitting by route and feature
- Dynamic imports for heavy components
- Tree shaking for unused code
- Compression and minification

### Runtime Performance
- React.memo for expensive components
- Virtualization for long lists
- Debounced search and filtering
- Optimistic UI updates

### Performance Metrics
- Target load time: < 3 seconds on 3G
- Time to Interactive: < 2 seconds
- Bundle size: < 500KB gzipped
- Lighthouse score: > 90

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

### Component Testing
Components are tested with React Testing Library:

```tsx
import { render, screen } from '@testing-library/react';
import { MetricCard } from './MetricCard';

test('renders metric card with correct value', () => {
  render(<MetricCard title="Test" value={42} />);
  expect(screen.getByText('42')).toBeInTheDocument();
});
```

## 🔒 Security

### Best Practices
- No inline scripts or styles
- Content Security Policy headers
- XSS prevention
- Secure WebSocket connections (WSS in production)
- Input sanitization
- Dependency vulnerability scanning

## 📊 Monitoring

### Error Tracking
- Error boundaries for graceful failure
- Centralized error reporting
- Performance monitoring
- User interaction tracking

### Analytics
- Page view tracking
- Feature usage metrics
- Performance metrics
- Error rates

## 🚀 Deployment

### Build Configuration
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Configuration
The build automatically detects environment variables and optimizes accordingly.

## 🔧 Development

### Code Quality
```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check

# Format code
npm run format
```

### Pre-commit Hooks
Husky is configured to run linting and tests before commits:

```bash
# Install pre-commit hooks
npm run prepare
```

## 📚 API Documentation

### WebSocket Events
- `agent_update`: Agent status change
- `workflow_update`: Workflow progress update
- `chat_message`: New chat message
- `system_status`: System health update

### REST Endpoints
- `GET /api/status`: System status
- `GET /api/agents`: Agent list
- `GET /api/workflows`: Workflow sessions
- `GET /api/metrics`: Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed description
4. Include steps to reproduce and expected behavior

---

**Note**: This frontend implementation is designed to work alongside the existing Python backend. Migration should be done incrementally to ensure minimal disruption to existing functionality.