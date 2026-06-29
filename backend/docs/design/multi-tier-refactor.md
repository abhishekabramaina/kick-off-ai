# Technical Design: Multi-Tier Backend Refactor

## 1. Goal
The objective is to decouple the FastAPI routers from the SQLAlchemy database layer and business logic. This will be achieved by implementing the Service and Repository patterns, ensuring the system is testable, maintainable, and ready for future scaling (e.g., microservices or background tasks).

## 2. New Architecture Structure

### 2.1. Folder Layout
The `backend/app` directory will be expanded with two new packages:
- `repositories/`: Contains classes for data access logic.
- `services/`: Contains classes for business and domain logic.
- `dependencies.py`: A central file to manage FastAPI dependency injection providers.

### 2.2. Data Flow
`Request` -> `Router (Presentation)` -> `Service (Business)` -> `Repository (Data)` -> `Database`

## 3. Implementation Details

### 3.1. The Repository Layer
Each entity (`Project`, `Employee`, `Role`, `Match`) will have a corresponding repository class.
- **Responsibility:** Executing SQLAlchemy queries, handling commits/refreshes.
- **Pattern:** One repository class per database model.
- **Convention:** `backend/app/repositories/{entity}_repo.py` containing `{Entity}Repository`.

### 3.2. The Service Layer
Services will orchestrate business operations.
- **Responsibility:** Input validation beyond schemas, LLM orchestration, coordinating multiple repositories.
- **Pattern:** Domain-focused service classes.
- **Convention:** `backend/app/services/{domain}_service.py` containing `{Domain}Service`.

### 3.3. Dependency Injection
We will use FastAPI's `Depends` to maintain a clean dependency graph.
- Routers will depend on Services.
- Services will depend on Repositories and `LLMService`.
- A centralized `dependencies.py` will provide factory functions for these layers.

## 4. Migration Strategy
To maintain control and verify parity at each step, we will refactor incrementally:
1. **Repository Setup:** Create `repositories/` and move core DB queries for one entity at a time.
2. **Service Setup:** Create `services/` and move business logic for one domain at a time.
3. **Router Refactor:** Update routers to use the new Services.
4. **Validation:** Verify endpoint functionality after each domain is migrated.

## 5. Verification Plan
- **Manual parity check:** Ensure all existing API endpoints return the same data format.
- **Unit Testing:** Implement a sample unit test for `ResourcingService` using a mock repository to prove decoupling.
