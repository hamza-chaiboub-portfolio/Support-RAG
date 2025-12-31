# CLAUDE.md - SupportRAG AI

## Frontend

### Commands
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests (Vitest)
- `npx tsc --noEmit` - Type check TypeScript
- `npm run lint` - Run ESLint

### Code Structure
- `src/components/chat/` - Chat interface components
- `src/components/auth/` - Authentication components
- `src/services/` - API services (chat, auth, etc.)
- `src/types/` - TypeScript definitions
- `src/context/` - React Context providers
- `tests/` - Unit and Integration tests

### Testing
- Tests are written using Vitest and React Testing Library
- Run `npm test` to execute all tests
- Tests verify component rendering, user interactions, and service logic

### Authentication
- JWT-based authentication
- Token stored in localStorage
- `authService` handles login/logout
- `apiClient` interceptor attaches `Authorization: Bearer <token>` header automatically

### Configuration
- Environment variables in `.env` (copied from `.env.example`)
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_PROJECT_ID` - Project ID for RAG queries
