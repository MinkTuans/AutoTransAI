# AGENTS.md — Mandates & Rules for AI Agents

Welcome to **AutoTransAI** (WorkflowVdAi). This document specifies mandatory operational rules, execution workflows, and verification requirements for any AI agent or assistant modifying or interacting with this codebase.

---

## 📌 MANDATORY AGENT RULES

### RULE 1: Read Knowledge Base First
Before making **ANY** code edits, configuration changes, or architectural proposals, you **MUST** read [PROJECT_KNOWLEDGE_BASE.md](file:///c:/Hack/AutoTransAI/PROJECT_KNOWLEDGE_BASE.md).
- Understand how the system is structured.
- Understand the 6-stage Unified Workflow Engine architecture.
- Understand the database schema and AI provider failover mechanisms.

### RULE 2: Source Code is the Ultimate Ground Truth
While [PROJECT_KNOWLEDGE_BASE.md](file:///c:/Hack/AutoTransAI/PROJECT_KNOWLEDGE_BASE.md) provides comprehensive documented context, active source code files are the authoritative ground truth. If there is a discrepancy between documentation and actual implementation:
1. Inspect the relevant active code files.
2. Follow the implementation in the source code.
3. Update [PROJECT_KNOWLEDGE_BASE.md](file:///c:/Hack/AutoTransAI/PROJECT_KNOWLEDGE_BASE.md) to match the current ground truth.

### RULE 3: Analyze Impact Before Modification
Before modifying any file, perform a complete impact analysis:
- **Files**: Search for all imports, usages, and references across backend and frontend.
- **Dependencies**: Verify if function signatures, parameters, or return types change.
- **Database**: Check if ORM models, foreign keys, or database column constraints are affected.
- **API Contracts**: Ensure REST API endpoints, request bodies, and SSE event payloads maintain backward compatibility.
- **AI & Storage**: Check if AI provider integrations, API key rotation, or file storage paths are affected.

### RULE 4: No Assumptions or Hallucinations
- **NEVER** guess file paths, function signatures, variable names, or database column names.
- Always use file search (`grep_search` / `view_file`) to inspect the actual implementation.
- Base diagnostic hypotheses strictly on empirical evidence from log tracebacks or test outputs.

### RULE 5: Keep Knowledge Base Synchronized
After completing a task that changes:
- Architecture or directory structure
- Features or status
- Database schema or ORM models
- API endpoints or schemas
- AI providers or model configurations
- Environment variables or settings
- Storage mechanisms
You **MUST** update the relevant sections in [PROJECT_KNOWLEDGE_BASE.md](file:///c:/Hack/AutoTransAI/PROJECT_KNOWLEDGE_BASE.md).

### RULE 6: Maintain AI Changelog
After completing any significant task, update [CHANGELOG_AI.md](file:///c:/Hack/AutoTransAI/CHANGELOG_AI.md) with a clear record of:
- Task description and date
- Added / Modified / Removed features
- Affected files
- Database / API / Configuration changes
- Knowledge Base updates

### RULE 7: Pre-Completion Verification Checklist
Before declaring any task complete, verify each checklist item:
```text
[ ] Read PROJECT_KNOWLEDGE_BASE.md for context
[ ] Inspected relevant source code and verified exact symbols
[ ] Analyzed downstream impact on dependencies, API contracts, and database
[ ] Implemented only necessary, clean, un-bloated changes
[ ] Verified changes (ran pytest / build commands if applicable)
[ ] Updated PROJECT_KNOWLEDGE_BASE.md if architecture/API/DB/Config changed
[ ] Updated CHANGELOG_AI.md with task summary
[ ] Ensured 100% backward compatibility
```

### RULE 8: Strict Prohibition of Autonomous Project Deletion
- **NEVER** delete the project repository, codebase directories, database, or key source files on your own initiative without explicit user instruction.
- Workspace cleanup commands or deletions must strictly target only authorized temporary/scratch files, and must never touch active project files or project root directories.

---

## 🔄 STANDARD AGENT EXECUTION WORKFLOW

```text
NEW TASK RECEIVED
       │
       ▼
READ AGENTS.md & PROJECT_KNOWLEDGE_BASE.md
       │
       ▼
INSPECT RELEVANT SOURCE CODE (Grep / View)
       │
       ▼
ANALYZE DOWNSTREAM IMPACT
       │
       ▼
IMPLEMENT EDITS / MODIFICATIONS
       │
       ▼
RUN VERIFICATION / TESTS
       │
       ▼
UPDATE PROJECT_KNOWLEDGE_BASE.md
       │
       ▼
UPDATE CHANGELOG_AI.md
       │
       ▼
TASK COMPLETE & SYNTHESIZE REPORT
```
