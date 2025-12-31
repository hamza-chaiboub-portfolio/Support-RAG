# Testing Guide

## Overview
This project uses **Vitest** for testing and **React Testing Library** for component testing.

## Running Tests
- **Run all tests:** `npm test`
- **Run specific test file:** `npm test <filename>`
- **Run with UI:** `npm test -- --ui`

## Test Structure
- `tests/unit/`: Unit tests for individual components and utilities
- `tests/integration/`: Integration tests for full flows (e.g., Authentication, Chat)

## Key Test Files
- `AuthFlow.integration.test.tsx`: Verifies the login/logout flow and protected route access.
- `ChatInterface.integration.test.tsx`: Verifies the main chat functionality.

## Mocks
- API calls are mocked using `vi.mock` in each test file or in `setupTests.ts`.
- `authService` and `chatService` are key services that are often mocked to simulate backend responses.
