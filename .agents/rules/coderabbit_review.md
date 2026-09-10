---
trigger: always_on
description: Ensures code changes comply with CodeRabbit AI review guidelines and standards.
---

# CodeRabbit Code Quality & Review Rule

When editing or creating code in this codebase, adhere strictly to the following standards so that all pull requests pass CodeRabbit automated code reviews:

## 1. Type Safety & Explicit Signatures
*   **Python (FastAPI):** Always provide explicit return types and type hints for function arguments. Use Pydantic models for request/response bodies.
*   **TypeScript (Next.js):** Avoid implicit `any`. Explicitly define prop types and API response interfaces.

## 2. Error Handling & Logging
*   Never swallow exceptions silently or return dummy fallbacks.
*   Trace root causes and log explicit error context before handling or re-raising exceptions.

## 3. Performance & Clean Code
*   **Canvas & MediaPipe:** Release OpenCV video captures and MediaPipe instances cleanly after processing to prevent memory leaks.
*   **React Components:** Avoid inline non-memoized heavy calculations inside render loops.

## 4. PR Readiness
*   Write clear, self-documenting commit messages following standard conventions (`feat:`, `fix:`, `refactor:`, `docs:`).
