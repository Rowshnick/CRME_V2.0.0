# CRME SESSION RULES

Version: 1.0
Status: Active


## Core Principles

1. Evidence-Based Development

All decisions and modifications must be based on:
- Existing project files
- Current implementation
- Verified experimental results
- Approved project decisions


2. No Assumptions

Never introduce:
- Unverified assumptions
- Artificial improvements
- Unsupported claims
- Fabricated experimental results


3. No Destructive Changes

Never:
- Delete existing code
- Replace working modules with older versions
- Remove project history

All modifications must be incremental and reversible.


4. Backup Before Modification

Before any major change:

- Create backup
- Record changed files
- Describe modification reason
- Maintain rollback capability


5. Traceability

Every important decision must be recorded in:

- decision_log.json
- change_log.json


6. Reproducibility

Experiments must use:

- Public or synthetic datasets
- Reproducible generators
- Documented parameters

No private personal data should be used.


7. Session Continuity

At the beginning of each session:

Read:

- session_rules.md
- project_state.json
- decision_log.json
- latest session snapshot


8. Development Priority

Priority order:

1. Stabilize existing implementation
2. Improve scientific validity
3. Improve evaluation methodology
4. Update documentation
5. Add future features only after paper completion


9. CRME Companion Future Layer

The CRME Companion App is a future development layer above CRME core.

It must not modify the research memory engine.

Purpose:

- User-friendly Android interface
- Session initialization
- Project status display
- AI interaction preparation
- Non-technical user access
