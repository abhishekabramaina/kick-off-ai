# ADR-001: Transition to Multi-Tier Architecture

## Status
Proposed

## Context
The current backend implementation of the Brain project is a 2-tier monolithic structure where API controllers (FastAPI routers) are tightly coupled with the database layer (SQLAlchemy) and business logic (LLM orchestration). 

As the project scales to include more complex features like distributed task queues, vector search, and advanced resource allocation algorithms, this tight coupling introduces several risks:
- **Low Testability:** Business logic cannot be tested without a database connection.
- **High Maintenance Cost:** Changes to the database schema require changes to the API routes.
- **Rigidity:** Difficult to swap components (e.g., changing LLM providers or database types).

## Decision
We will refactor the backend into a **Multi-Tiered Architecture** utilizing the following patterns:
1.  **Repository Pattern:** Abstracting all database interactions into a Data Access Layer.
2.  **Service Layer Pattern:** Encapsulating business logic and domain rules.
3.  **Dependency Injection:** Using FastAPI's `Depends` to inject repositories into services and services into controllers.

## Consequences
### Positive
- **Decoupling:** Layers can evolve independently.
- **Mockability:** Services can be unit-tested using mock repositories.
- **Standardization:** Follows industry-standard patterns expected at Tier-1 tech companies like Amazon.
- **Portability:** Easier to migrate specific logic to microservices or serverless functions in the future.

### Negative
- **Boilerplate:** Increases the number of files and lines of code for simple CRUD operations.
- **Complexity:** Higher initial cognitive load for new developers to understand the flow of data across three layers.

## Compliance
- All new features must be implemented following the Service/Repository pattern.
- Direct database access from API routers is strictly prohibited post-refactor.
