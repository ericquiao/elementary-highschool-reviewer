# Iteration

Iteration:
Concept-001

Phase:
Mock / Concept

Goal:
Capture the product idea, user problem, core review workflow, and mock interaction behavior before any architecture or implementation planning.

## Idea Snapshot
- Problem: Students struggle to quickly understand lessons, turn study material into quizzes, and review efficiently using fragmented tools.
- Users: Elementary students (Grade 3-6) and junior high students (Grade 7-10).
- Desired outcome: A simple AI reviewer assistant that explains lessons, analyzes one uploaded study image, and generates quiz practice by subject.
- Why now: Students already collect notes, homework photos, and scattered online resources, but do not have one simple review-first workflow.

## Discussion Summary
- Main user flow: A student logs in, chooses an action, selects a subject, submits a question or one image, then receives an explanation, a quiz, or both.
- First-build direction: Keep the app focused on review and practice only. Do not expand into teaching platforms, parent tools, teacher dashboards, gamification, or advanced analytics.
- Proposed stack from the builder: Angular, FastAPI, SQLite, Tailwind CSS, Gemini 1.5 Flash, Gemini Vision, Google OAuth, email/password, local upload storage.
- Scope risk flagged by framework: Dual auth methods, AI chat, quiz generation, vision processing, usage limits, and activity tracking are a large bundle, so the concept record keeps them noted but not yet architecture-scoped.

## Problem Clarification
- Students need faster review, not long-form tutoring.
- The product should reduce the effort required to go from "I have a question or study image" to "I understand this and can practice it."
- Subject selection matters because the same keyword can mean different things across Math, Science, English, MAPEH, ESP, TLE, and Araling Panlipunan.
- The first experience must be simple enough for younger students without relying on complex setup or file management.

## User Definition
- Primary user 1: Elementary student needing short, guided explanations and simple quiz practice.
- Primary user 2: Junior high student preparing for homework checks, quizzes, and exams.
- Excluded from MVP: Senior high students, parents, teachers, and tutors.
- User motivation: Understand school material quickly, practice before exams, and reuse handwritten or printed study material through image upload.

## Core Workflow
1. Student logs in using Google OAuth or email and password.
2. Student chooses `Ask Question`, `Upload Study Image`, or `Generate Quiz`.
3. Student selects one subject from the DepEd-aligned list.
4. System analyzes the request and returns an explanation, a 10-item multiple choice quiz, or both.
5. If the request is unclear, the system asks a focused follow-up question.
6. If the student uploads an image, the system analyzes exactly one image, extracts context, and produces review output.
7. Study activity is logged as a session with estimated time spent until inactivity timeout.

## Mock Interaction Examples
### Example 1: Ask Question
Student: "Why do we carry numbers in addition?"
System: "Choose a subject first."
Student: "Math"
System: "When one column adds up to 10 or more, we move the tens value to the next column. Do you want a short explanation only or a 10-question quiz too?"

### Example 2: Unclear Input
Student: "Cooking"
System: "Choose a subject first."
Student: "TLE"
System: "What do you want to review about cooking: cooking methods, food safety, nutrition, or recipe basics?"

### Example 3: Image Upload
Student: uploads one notebook photo
System: "Choose a subject first."
Student: "Science"
System: "I found notes about the water cycle. I can explain evaporation, condensation, and precipitation, or generate a 10-question quiz from this page."

### Example 4: Generate Quiz
Student: "Make me a quiz about fractions."
System: "Choose a subject first."
Student: "Math"
System: "Here is a 10-question multiple choice quiz on fractions. I can also explain any item you get wrong."

## Mocked System Behavior
- `mock_auth_service`: accepts Google login and email/password login flows at the concept level.
- `mock_ai_review_service`: returns either explanation text, quiz output, or explanation plus quiz.
- `mock_vision_service`: accepts one uploaded image and returns extracted study context.
- `mock_usage_limit_service`: tracks daily explanation, quiz, and image counts for free-tier users.
- `mock_study_session_service`: starts a session on question or quiz start and ends it after inactivity.

## Assumptions To Validate
- Students are comfortable choosing a subject before asking their question.
- A 10-item multiple choice quiz is the right default length for both elementary and junior high students.
- One image per request is enough for the first review experience.
- Students want explanation plus quiz as a common combined output.
- Free-tier daily limits of 20 explanations, 20 quizzes, and 5 image uploads are acceptable.
- Session start and inactivity-based end are sufficient for basic study tracking.

## Validation Signals
- Students can submit a question and reach a useful explanation quickly.
- Students can turn a topic into a quiz without extra setup.
- Students understand how to use the subject picker and action picker.
- Image-based review produces useful explanations or quizzes from real study photos.
- Students feel the workflow is simpler than switching between notes, search, and videos.

## Clarifying Questions
- None required to complete the concept record. The builder supplied the problem, users, workflow, scope boundaries, and proposed stack clearly enough for this stage.

## Stop Point
- Per builder instruction, stop after the Mock / Concept stage.
- Do not produce architecture, implementation plans, or build steps yet.
