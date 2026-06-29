# GridSense Analytics Platform Engine

This workspace contains the complete, containerized polyglot data architecture implementation for the Advanced Data Management final project.

## Prerequisites
* Docker Desktop (configured with at least 4GB of allocated RAM memory)
* Python 3.10+ (for running localized benchmark execution validation scripts)

## Rapid Deployment (The One-Command Boot Test)
To spin up all 5 distributed database engine nodes alongside the automated initialization routines and the API core, execute:
```bash
docker compose up --build