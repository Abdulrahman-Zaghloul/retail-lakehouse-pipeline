# Engineering Decisions

This document records important design decisions made during the project.

## Decision Log

### 001 - Start local-first before AWS

We will build the first version locally using Docker, PostgreSQL, and MinIO before deploying to AWS.

Reason:

- Avoid unnecessary cloud cost while developing.
- Make the project easy to run from a laptop.
- Prove the architecture locally before moving to managed cloud services.

Tradeoff:

- Local Docker services are not the same as managed AWS services.
- Some cloud-specific behavior will need to be handled later.
