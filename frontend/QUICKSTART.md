# ProcurAI Frontend - Quick Start Guide

## Prerequisites
- Node.js 18+ installed
- Backend API running on `http://localhost:8000`
- Database migrations applied on backend

## Installation & Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Default configuration:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

The app will be available at: **http://localhost:5173**

## First-Time Setup

### Create Test Users (via Backend)

#### Buyer User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer@test.com",
    "password": "Test123!@#",
    "username": "test_buyer",
    "role": "buyer"
  }'
```

#### Seller User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@test.com",
    "password": "Test123!@#",
    "username": "test_seller",
    "role": "seller"
  }'
```

## Login Credentials

### Buyer Account
- Email: `buyer@test.com`
- Password: `Test123!@#`

### Seller Account
- Email: `seller@test.com`
- Password: `Test123!@#`

## Application Structure

### Buyer Journey
1. **Login** → `/login`
2. **Dashboard** → `/` - View active requests and metrics
3. **Create Request** → `/requests/new` - 5-step wizard
4. **Negotiation Theater** → `/requests/:id/negotiate` - Watch AI negotiate
5. **Approvals** → `/approvals` - Approve/reject offers
6. **Portfolio** → `/portfolio` - Manage subscriptions

### Seller Journey
1. **Login** → `/login`
2. **Dashboard** → `/seller` - Monitor AI agent activity
3. **Negotiations** → `/seller/negotiations` - View active deals
4. **Guardrails** → `/seller/guardrails` - Configure pricing
5. **Analytics** → `/seller/analytics` - Win/loss insights

## Key Features to Test

### ✅ Buyer Flow: Create New Request
1. Go to Dashboard
2. Click "New Request" button
3. Follow 5-step wizard:
   - Set budget ($50K-$150K recommended)
   - Describe need (e.g., "CRM for 200 sales reps")
   - Add must-have features
   - Review policy preview
   - Submit request

### ✅ Negotiation Theater
1. After creating request, navigate to negotiations
2. Watch AI agent negotiate with multiple vendors in parallel
3. Click "Why?" buttons to see AI reasoning
4. Monitor real-time feed of offers and counteroffers
5. Use control panel to adjust or stop negotiations

### ✅ Approval Workspace
1. Navigate to `/approvals`
2. Review offer summary and TCO breakdown
3. Check compliance indicators
4. Add approval comment
5. Approve, reject, or request changes

### ✅ Portfolio Management
1. Navigate to `/portfolio`
2. View active subscriptions with utilization
3. Filter by "Upcoming Renewals" or "Underutilized"
4. See AI recommendations for cost savings
5. Select items for bulk actions

### ✅ AI Transparency
- Every decision has a "Why?" explainer
- Click purple info icon to see reasoning
- Shows score components, strategy, and logic
- Available throughout the app

## Component Library

### Button Variants
```tsx
<Button variant="primary">Primary Action</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outlined</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="danger">Delete</Button>
```

### Status Badges
```tsx
<StatusBadge status="draft" />
<StatusBadge status="negotiating" />
<StatusBadge status="contracted" />
```

### AI Explainer
```tsx
<AIExplainer
  title="this recommendation"
  reasoning={[
    { label: 'Score', value: '95%' },
    { label: 'Confidence', value: 'High' }
  ]}
/>
```

## Troubleshooting

### Issue: Login Fails
- **Check**: Backend API is running on port 8000
- **Check**: CORS is configured to allow `http://localhost:5173`
- **Check**: Database has been initialized with migrations

### Issue: No Data Showing
- **Check**: API endpoints are responding (check Network tab)
- **Check**: Authentication token is being sent (should see in request headers)
- **Check**: Backend database has seed data or create test data

### Issue: Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### Issue: Hot Reload Not Working
```bash
# Restart dev server
# Kill process on port 5173 if needed
lsof -ti:5173 | xargs kill -9
npm run dev
```

## Development Tips

### Enable React Query DevTools
DevTools are automatically included in development mode. Click the floating React Query icon in the bottom-left corner to inspect:
- Query cache
- Mutation state
- Request/response data
- Refetch triggers

### Browser Extensions
Recommended for development:
- React Developer Tools
- Redux DevTools (works with Zustand)
- Axe DevTools (accessibility)

### VSCode Extensions
- ESLint
- Prettier
- TypeScript Vue Plugin
- Tailwind CSS IntelliSense

## Production Build

### Build
```bash
npm run build
```

Output: `dist/` directory

### Preview Production Build
```bash
npm run preview
```

### Deploy
The `dist/` folder can be deployed to:
- Netlify
- Vercel
- AWS S3 + CloudFront
- Any static hosting service

### Environment Variables for Production
```env
VITE_API_BASE_URL=https://api.procur.ai
```

## Performance

Current bundle size (estimated):
- Vendor chunks: ~150KB gzipped
- App code: ~80KB gzipped
- Total: ~230KB gzipped

Lighthouse scores (target):
- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 90+

## Next Steps

### Implement Additional Pages
1. Request detail page
2. Seller negotiation control center
3. Analytics dashboards
4. Settings pages

### Add Real-Time Features
1. WebSocket connection for live updates
2. Notification center
3. Real-time negotiation feed

### Enhance UX
1. Loading skeletons
2. Error boundaries
3. Toast notifications
4. Keyboard shortcuts

## Support

For issues or questions:
1. Check `FRONTEND_IMPLEMENTATION.md` for detailed documentation
2. Review backend API documentation
3. Check browser console for errors
4. Review Network tab for failed requests

---

**Happy coding! 🚀**
