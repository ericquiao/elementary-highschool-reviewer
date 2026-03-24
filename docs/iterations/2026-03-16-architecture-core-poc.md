Iteration:
Architecture-001

Phase:
Core POC / Architecture

Goal:
Define the smallest local system capable of validating the locked text-and-image review pipeline.

Changes Implemented:
- Created the Core POC architecture definition.
- Locked the system to a single Angular frontend, single FastAPI backend, and one Gemini request per user action.
- Defined temporary image handling with immediate cleanup.
- Defined a single structured response contract for both text and image inputs.

Files Modified:
- docs/architecture.md
- docs/project_overview.md

New Features:
- Architecture for text question review flow.
- Architecture for image upload and camera capture review flow.
- Structured AI response contract covering detected subject, detected topic, explanation, example, and quiz.

Bug Fixes:
- None

Known Issues:
- Subject/topic accuracy remains unproven until real Gemini responses are tested.
- Structured model output may need validation guards if Gemini returns inconsistent formatting.
- Camera capture behavior depends on browser permissions during local testing.

Next Planned Iteration:
- Move to build planning for the locked Core POC only.
