## Build Plan
- Project structure:
  - `app/frontend/` for the Angular single-page UI.
  - `app/backend/` for the FastAPI API.
  - `app/backend/app/` for FastAPI source files.
  - `app/backend/app/main.py` for FastAPI app startup and route registration.
  - `app/backend/app/models.py` for request and response schemas.
  - `app/backend/app/gemini_service.py` for Gemini request construction and response parsing.
  - `app/backend/app/temp_files.py` for temporary image save and cleanup helpers.
  - `app/backend/requirements.txt` for Python dependencies.
  - `app/frontend/src/app/` for Angular components and services.
  - `app/frontend/src/app/review-page/` for the single review UI.
  - `app/frontend/src/app/services/review-api.service.ts` for HTTP calls to `POST /api/review`.
  - `app/frontend/src/app/types/review-result.ts` for the frontend response contract.
  - `app/frontend/src/styles.css` for Tailwind entry and minimal global styles.
  - No database directory is required for the first pass.
- Files to generate:
  - Backend:
    - `app/backend/app/main.py`
    - `app/backend/app/models.py`
    - `app/backend/app/gemini_service.py`
    - `app/backend/app/temp_files.py`
    - `app/backend/requirements.txt`
    - `app/backend/.env.example`
  - Frontend:
    - `app/frontend/angular.json` if not already scaffolded by Angular CLI
    - `app/frontend/package.json` if not already scaffolded by Angular CLI
    - `app/frontend/src/app/app.component.ts`
    - `app/frontend/src/app/app.component.html`
    - `app/frontend/src/app/review-page/review-page.component.ts`
    - `app/frontend/src/app/review-page/review-page.component.html`
    - `app/frontend/src/app/review-page/review-page.component.css`
    - `app/frontend/src/app/services/review-api.service.ts`
    - `app/frontend/src/app/types/review-result.ts`
    - `app/frontend/src/environments/environment.ts`
    - `app/frontend/src/environments/environment.development.ts`
- API endpoints:
  - `POST /api/review`
    - Accepts multipart form data.
    - Allowed inputs:
      - `question` text field only
      - `image` file only
    - Rejects empty submissions or requests containing both unsupported combinations after validation rules are defined.
    - Returns JSON with:
      - `detected_subject`
      - `detected_topic`
      - `explanation_bullets`
      - `example`
      - `quiz`
    - `quiz` contains 10 items, each with:
      - `question`
      - `choices`
      - `correct_answer`
- Database schema:
  - None for the initial one-shot build.
  - Optional SQLite logging is deferred and should not be built unless the one-shot implementation needs minimal debug logging later.
- UI components:
  - `ReviewPageComponent`
    - Contains the whole Core POC user flow.
    - Manages input mode selection: text or image.
    - Renders text textarea, file upload button, camera capture control, submit button, loading state, error state, and result state.
  - Result display sections inside the same page:
    - Detected subject block
    - Detected topic block
    - Explanation bullet list
    - Example block
    - Quiz list with 10 MCQ items
  - `ReviewApiService`
    - Builds `FormData`
    - Sends request to backend
    - Maps backend response to frontend types
- Mock data:
  - No mocked AI responses in the main happy path because Gemini is the capability under test.
  - Prepare 5-7 real study images locally for manual verification:
    - Math homework photo
    - Science notes photo
    - English worksheet photo
    - MAPEH notes photo
    - Araling Panlipunan notes photo
    - TLE page photo
  - Prepare 2-3 sample text questions for manual verification.
- Run instructions:
  - Backend:
    - Create a Python virtual environment in `app/backend/`
    - Install dependencies from `requirements.txt`
    - Set Gemini API key in local environment or `.env`
    - Start FastAPI locally with Uvicorn
  - Frontend:
    - Initialize Angular project in `app/frontend/`
    - Install Angular dependencies and Tailwind CSS
    - Configure environment file with backend base URL
    - Start Angular dev server locally
  - Local run model:
    - Open Angular app in the browser
    - Submit text or image input
    - Backend calls Gemini and returns structured JSON
- Verification steps:
  - Text flow:
    - Enter a simple question such as a homework-style prompt
    - Confirm the UI shows detected subject, detected topic, explanation bullets, example, and 10 quiz items
    - Confirm the explanation language is short and student-friendly
  - Image flow:
    - Upload one test image
    - Confirm the backend accepts the file, calls Gemini, and returns structured output
    - Confirm temporary image cleanup occurs after the request completes
    - Confirm detected subject and topic are mostly aligned with the image content
  - Camera flow:
    - Capture one image from the browser camera input
    - Confirm it follows the same backend path as file upload
  - Error handling:
    - Submit with no input and confirm validation error
    - Test malformed or unsupported image input and confirm safe error handling
    - Confirm frontend loading and error states render clearly

## One-Shot Implementation Sequence
1. Scaffold the Angular frontend in `app/frontend/`.
2. Scaffold the FastAPI backend in `app/backend/`.
3. Add backend schemas for the normalized review response.
4. Implement temporary image save and delete helpers.
5. Implement Gemini service logic with one prompt builder and one response parser.
6. Implement `POST /api/review` in FastAPI.
7. Build the Angular review page and API service.
8. Wire text question submission to the backend.
9. Wire image upload and camera capture submission to the same backend endpoint.
10. Render structured results in the Angular UI.
11. Run the frontend and backend locally.
12. Verify the text, upload, and camera flows using real study inputs.

## Backend Implementation Notes
- Keep prompt instructions inline in `gemini_service.py` or `main.py`, not in a separate prompt system.
- Use one request builder for both text and image inputs so the response shape stays consistent.
- Instruct Gemini to return structured JSON or a strongly structured response that can be normalized.
- Validate that exactly one supported input is present before calling Gemini.
- Always delete temporary image files in success and failure paths.

## Frontend Implementation Notes
- Keep all UI inside one page to match the architecture.
- Use a single submit action for both text and image modes.
- Camera capture should feed an image file into the same upload path used by normal file selection.
- Keep styling minimal and focused on readability of explanation and quiz output.

## Local Development Checklist
- Angular app starts on localhost.
- FastAPI app starts on localhost.
- Frontend can reach backend API.
- Gemini API key is loaded locally.
- One text request completes successfully.
- One image upload request completes successfully.
- One camera capture request completes successfully.
