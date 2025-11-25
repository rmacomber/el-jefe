# El Jefe Dashboard Migration Guide

## Overview

This guide provides step-by-step instructions for migrating from the vanilla HTML/CSS/JavaScript dashboard to the modern React implementation. The migration is designed to be gradual, allowing both implementations to run in parallel during the transition period.

## Pre-Migration Checklist

### 1. Backup Current Implementation
```bash
# Create backup of current static files
cp -r static static-backup-$(date +%Y%m%d)
cp monitoring_dashboard.py monitoring_dashboard.py.backup
```

### 2. Verify Current Functionality
```bash
# Test current dashboard
python monitoring_dashboard.py
# Navigate to http://localhost:8080
# Verify all features are working:
# - Agent monitoring
# - Workflow visualization
# - Chat functionality
# - WebSocket updates
```

### 3. Check Dependencies
```bash
# Verify Python dependencies
pip list | grep -E "(aiohttp|websockets|aiohttp-cors)"

# Install any missing dependencies
pip install -r requirements.txt
```

## Migration Strategy

### Phase 1: Parallel Development (Week 1-2)

**Goal**: Set up React development environment alongside existing implementation

#### 1.1 Initialize React Project
```bash
# Create frontend directory
mkdir frontend
cd frontend

# Initialize React project with Vite
npm create vite@latest . -- --template react-ts
npm install

# Install required dependencies
npm install @reduxjs/toolkit react-redux @tanstack/react-query
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material @mui/x-charts recharts
npm install socket.io-client react-router-dom date-fns lodash

# Install dev dependencies
npm install -D @testing-library/react @testing-library/jest-dom
npm install -D vitest @vitest/ui jsdom
npm install -D eslint-plugin-accessibility
```

#### 1.2 Configure Vite for Backend Integration
Create `vite.config.ts` (already provided in starter):

```typescript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
});
```

#### 1.3 Update Backend for Dual Support
Modify `monitoring_dashboard.py` to support both implementations:

```python
# Add new route for React app
async def serve_react_app(request):
    """Serve the React development or production app."""
    if os.path.exists('frontend/dist/index.html'):
        # Production build
        return web.FileResponse('frontend/dist/index.html')
    else:
        # Development proxy or fallback
        return web.Response(text="React app not built. Run 'npm run build' in frontend/", status=503)

# Add to routes
self.app.router.add_get('/dashboard', self.serve_react_app)
self.app.router.add_static('/react/', path='frontend/dist/', name='react')
```

#### 1.4 Test Parallel Setup
```bash
# Terminal 1: Start backend
python monitoring_dashboard.py

# Terminal 2: Start React development
cd frontend
npm run dev
```

Access both implementations:
- Original: `http://localhost:8080/`
- New React: `http://localhost:3000/`

### Phase 2: Feature Migration (Week 3-4)

**Goal**: Migrate core features one by one

#### 2.1 Dashboard Metrics Migration

**Step 1: Create API Adapter**
```typescript
// src/services/api.ts
export const apiAdapter = {
  transformAgentData: (legacyAgent: any): AgentJob => ({
    job_id: legacyAgent.job_id,
    agent_type: legacyAgent.agent_type,
    // ... field mappings
  }),

  transformWorkflowData: (legacyWorkflow: any): WorkflowSession => ({
    session_id: legacyWorkflow.session_id,
    goal: legacyWorkflow.goal,
    // ... field mappings
  }),
};
```

**Step 2: Implement Metric Cards**
```typescript
// src/components/Dashboard/MetricsGrid.tsx
import { MetricCard } from '@/components/common/MetricCard';
import { useRealTimeData } from '@/hooks/useRealTimeData';

export const MetricsGrid = () => {
  const { data: metrics, loading } = useRealTimeData('/api/metrics', 'metrics_update');

  return (
    <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={3}>
      <MetricCard
        title="Active Agents"
        value={metrics?.active_agents || 0}
        loading={loading}
        icon={<AgentsIcon />}
      />
      <MetricCard
        title="Active Workflows"
        value={metrics?.active_workflows || 0}
        loading={loading}
        icon={<WorkflowIcon />}
      />
      {/* Additional metrics */}
    </Box>
  );
};
```

#### 2.2 Agent List Migration

**Step 1: Create Agent Components**
```typescript
// src/components/Agents/AgentList.tsx
export const AgentList = () => {
  const { data: agents, loading } = useRealTimeData('/api/agents', 'agent_update');

  return (
    <VirtualizedList
      height={600}
      itemCount={agents?.length || 0}
      itemSize={120}
      renderItem={({ index, style }) => (
        <div style={style}>
          <AgentListItem agent={agents[index]} />
        </div>
      )}
    />
  );
};
```

#### 2.3 Workflow Section Migration

**Step 1: Workflow Visualization**
```typescript
// src/components/Workflows/WorkflowList.tsx
export const WorkflowList = () => {
  const { data: workflows, loading } = useRealTimeData('/api/workflows', 'workflow_update');

  return (
    <Grid container spacing={3}>
      {workflows?.map((workflow) => (
        <Grid item xs={12} md={6} lg={4} key={workflow.session_id}>
          <WorkflowCard workflow={workflow} />
        </Grid>
      ))}
    </Grid>
  );
};
```

#### 2.4 Chat Integration Migration

**Step 1: WebSocket Chat Hook**
```typescript
// src/hooks/useChat.ts
export const useChat = () => {
  const { send } = useWebSocket();
  const { data: messages } = useRealTimeData('/api/chat/history', 'chat_message');

  const sendMessage = useCallback((content: string) => {
    send({ type: 'chat_message', message: content });
  }, [send]);

  return { messages, sendMessage };
};
```

### Phase 3: Advanced Features (Week 5-6)

**Goal**: Implement enhanced features not present in original implementation

#### 3.1 Data Visualization

```typescript
// src/components/Dashboard/Charts/AgentActivityChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export const AgentActivityChart = () => {
  const { data: activityData } = useRealTimeData('/api/metrics/timeline', 'timeline_update');

  return (
    <LineChart data={activityData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="timestamp" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="active_agents" stroke="#667eea" />
      <Line type="monotone" dataKey="active_workflows" stroke="#764ba2" />
    </LineChart>
  );
};
```

#### 3.2 Search and Filtering

```typescript
// src/components/Agents/AgentFilters.tsx
export const AgentFilters = () => {
  const { filters, setFilters } = useAgentFilters();

  return (
    <Accordion>
      <AccordionSummary>Filters</AccordionSummary>
      <AccordionDetails>
        <FormControl>
          <InputLabel>Status</InputLabel>
          <Select
            multiple
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <MenuItem value="running">Running</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
          </Select>
        </FormControl>
      </AccordionDetails>
    </Accordion>
  );
};
```

### Phase 4: Full Migration (Week 7-8)

**Goal**: Complete cutover to React implementation

#### 4.1 Production Build
```bash
cd frontend
npm run build
```

#### 4.2 Update Backend Routes
```python
# Update monitoring_dashboard.py
async def serve_index(request):
    """Serve the main dashboard page."""
    react_app_path = Path(__file__).parent / "frontend" / "dist" / "index.html"
    legacy_app_path = Path(__file__).parent / "static" / "index.html"

    if react_app_path.exists():
        return web.FileResponse(react_app_path)
    elif legacy_app_path.exists():
        return web.FileResponse(legacy_app_path)
    else:
        return web.Response(text=self.get_basic_html(), content_type="text/html")

# Update static file serving
self.app.router.add_static('/assets/', path='frontend/dist/assets/', name='react-assets')
```

#### 4.3 DNS and Routing Update
```python
# Set React as default
self.app.router.add_get('/', self.serve_index)
# Keep legacy available at /legacy if needed
self.app.router.add_get('/legacy', lambda request: web.FileResponse(static/index.html))
```

## Testing Strategy During Migration

### 1. Feature Parity Testing

```typescript
// tests/migration/feature-parity.test.ts
describe('Feature Parity Tests', () => {
  test('Agent data matches legacy implementation', async () => {
    const legacyData = await fetchLegacyAgents();
    const reactData = await fetchReactAgents();

    expect(reactData).toEqual(
      expect.arrayContaining(legacyData.map(apiAdapter.transformAgentData))
    );
  });

  test('WebSocket messages are consistent', async () => {
    const legacyMessages = await captureLegacyWebSocketMessages();
    const reactMessages = await captureReactWebSocketMessages();

    expect(reactMessages).toEqual(legacyMessages);
  });
});
```

### 2. Performance Comparison

```typescript
// tests/migration/performance.test.ts
describe('Performance Tests', () => {
  test('React dashboard loads faster than legacy', async () => {
    const legacyLoadTime = await measurePageLoadTime('http://localhost:8080/legacy');
    const reactLoadTime = await measurePageLoadTime('http://localhost:8080/');

    expect(reactLoadTime).toBeLessThan(legacyLoadTime);
  });
});
```

### 3. User Acceptance Testing

Create a checklist for users to verify functionality:

```markdown
# User Acceptance Testing Checklist

## Dashboard Overview
- [ ] Metrics display correctly
- [ ] Real-time updates work
- [ ] Loading states show properly

## Agent Monitoring
- [ ] Agent list populates
- [ ] Agent status updates
- [ ] Progress bars work
- [ ] Agent actions (pause, resume, stop) work

## Workflow Management
- [ ] Workflows display correctly
- [ ] Workflow progress shows
- [ ] Workflow controls work

## Chat Functionality
- [ ] Can send messages to El Jefe
- [ ] Receive responses correctly
- [ ] Chat history loads

## Mobile Responsiveness
- [ ] Works on mobile devices
- [ ] Touch interactions work
- [ ] No horizontal scrolling
```

## Rollback Plan

### Immediate Rollback (< 1 hour)
```bash
# Revert to legacy implementation
cp monitoring_dashboard.py.backup monitoring_dashboard.py
cp -r static-backup-* static
python monitoring_dashboard.py
```

### Partial Rollback (Feature-specific)
```python
# Feature flag implementation
USE_REACT_DASHBOARD = os.getenv('USE_REACT_DASHBOARD', 'false').lower() == 'true'

async def serve_index(request):
    if USE_REACT_DASHBOARD:
        return web.FileResponse('frontend/dist/index.html')
    else:
        return web.FileResponse('static/index.html')
```

## Monitoring During Migration

### 1. Error Tracking
```typescript
// src/utils/errorReporting.ts
export const reportError = (error: Error, context: string) => {
  console.error(`[${context}]`, error);

  // Send to error tracking service
  if (import.meta.env.PROD) {
    // Sentry, LogRocket, etc.
  }
};
```

### 2. Performance Monitoring
```typescript
// src/utils/performance.ts
export const measurePerformance = (name: string, fn: () => void) => {
  const start = performance.now();
  fn();
  const end = performance.now();

  console.log(`${name} took ${end - start} milliseconds`);

  // Report to analytics
  if (import.meta.env.PROD) {
    gtag('event', 'performance_metric', {
      metric_name: name,
      duration: end - start,
    });
  }
};
```

## Post-Migration Tasks

### 1. Cleanup
```bash
# Remove legacy files after verification period (30 days)
rm -rf static-backup-*
rm monitoring_dashboard.py.backup

# Update documentation
# Update deployment scripts
# Train users on new interface
```

### 2. Optimization
- Bundle analysis: `npm run build && npx vite-bundle-analyzer dist`
- Performance profiling
- A/B testing for new features
- User feedback collection

### 3. Maintenance
- Regular dependency updates
- Security audits
- Performance monitoring
- Accessibility testing

## Troubleshooting

### Common Issues

#### 1. WebSocket Connection Issues
```bash
# Check if WebSocket is running
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: test" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8080/ws
```

#### 2. CORS Issues
```python
# Update CORS configuration in monitoring_dashboard.py
cors = aiohttp_cors.setup(self.app, defaults={
    "http://localhost:3000": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
        allow_methods="*"
    )
});
```

#### 3. Build Issues
```bash
# Clear build cache
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check

# Check for linting issues
npm run lint
```

## Support Contacts

- **Technical Issues**: Development team
- **User Training**: Documentation team
- **Deployment Issues**: DevOps team
- **Rollback Requests**: System administrator

---

**Important**: This migration should be performed during a maintenance window to minimize user impact. Always have a rollback plan ready and test thoroughly before production deployment.