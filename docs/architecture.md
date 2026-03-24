## Architecture
- Frontend:
  - Single Angular application with one review page.
  - Tailwind CSS used for simple layout and form styling only.
  - UI supports three input paths inside the same flow: typed text question, image file upload, and camera capture.
  - Frontend builds one request payload per user action and sends it to the backend.
  - Frontend displays a single structured result view containing detected subject, detected topic, explanation bullets, example text, and 10 multiple choice quiz questions.
  - Frontend does not manage accounts, quotas, dashboards, history, or saved uploads.
- Backend:
  - Single FastAPI application exposing a small HTTP API for the review workflow.
  - Inline prompt instructions in the FastAPI code define the required response structure and student-friendly explanation style.
  - Backend accepts either text input or one image file per request.
  - Backend constructs exactly one Gemini multimodal request per user action.
  - Backend normalizes the Gemini response into a predictable JSON shape for the frontend.
  - Backend performs basic request validation, temporary file cleanup, and error handling for missing input or malformed model output.
- Database:
  - Not required for the Core POC.
  - SQLite remains optional and unused unless simple request logging becomes necessary during local testing.
- Integration points:
  - Gemini Flash multimodal model is the only required external integration.
  - Browser camera access is used on the frontend to capture an image and submit it as a standard image file.
  - No authentication, billing, analytics, or document-processing integrations are included.
- Local development setup:
  - Run Angular locally for the browser UI.
  - Run FastAPI locally for the API layer.
  - Configure the Gemini API key through local environment variables.
  - Store uploaded images only in a temporary local path during request handling, then delete them after the Gemini response is processed.
- Key tradeoffs:
  - Subject detection is inferred by Gemini instead of being chosen by the user to keep the POC closer to the locked experiment.
  - One backend endpoint handles both text and image requests to reduce branching and keep the system small.
  - No database is included because the POC is validating output quality, not persistence or analytics.
  - Prompt instructions stay inline for speed, even though that would not scale cleanly beyond the POC.

## Architecture Draft
- Frontend:
  - One page with an input mode toggle or segmented control for `Text Question` and `Image Input`.
  - Text mode shows a textarea and submit button.
  - Image mode shows upload control, camera capture option, image preview, and submit button.
  - Result area renders loading, error, and success states.
- Backend:
  - `POST /api/review` accepts multipart form data with either `question` or `image`.
  - Request handling path:
    - validate exactly one supported input
    - read text or temporary image
    - build one Gemini prompt with required output instructions
    - call Gemini
    - parse and return structured JSON
    - delete temporary image if one was created
  - Response shape:
    - `detected_subject`
    - `detected_topic`
    - `explanation_bullets`
    - `example`
    - `quiz`
  - Quiz item shape:
    - `question`
    - `choices`
    - `correct_answer`
- Database:
  - None in the first implementation pass.
- Mock integrations:
  - None for AI. Gemini is real because it is the capability under test.
  - No mocked auth because auth is out of scope.
- Local run model:
  - Angular on localhost for interaction.
  - FastAPI on localhost for request orchestration.
  - Direct backend-to-Gemini API call from the local machine.

## Data Flow
### Text Question Flow
1. Student enters a question in the Angular UI.
2. Angular sends `POST /api/review` with the question text.
3. FastAPI inserts the question into an inline prompt that asks Gemini to:
   - detect subject
   - detect topic
   - write a short structured explanation for Grades 3-10
   - include a short example when possible
   - generate 10 multiple choice questions with mostly basic difficulty
4. FastAPI sends one request to Gemini.
5. Gemini returns structured content.
6. FastAPI converts it to a stable JSON response.
7. Angular renders the detected subject, detected topic, explanation, example, and quiz.

### Image Input Flow
1. Student uploads an image or captures one from the browser camera.
2. Angular sends `POST /api/review` with one image file.
3. FastAPI stores the file temporarily for request processing only.
4. FastAPI sends one multimodal request to Gemini with the image and the same output instructions.
5. Gemini returns detected subject, detected topic, explanation, example, and quiz content.
6. FastAPI normalizes the response and deletes the temporary image.
7. Angular renders the structured result.

## Gemini Interaction Design
- One Gemini request per user action.
- The request includes either:
  - the student’s text question, or
  - one uploaded image
- The same backend prompt instructs Gemini to return:
  - detected subject
  - detected topic
  - 3-5 short explanation bullets
  - one short example when possible
  - 10 multiple choice quiz questions with answer options and correct answer
- Backend should instruct Gemini to keep language simple and suitable for Grades 3-10.
- Backend should request machine-friendly structured output so FastAPI can map it reliably into JSON.

## Temporary Image Handling Strategy
- Accept one image per request.
- Save the uploaded or captured image only to a temporary local path during backend processing.
- Use the temporary file immediately in the Gemini request.
- Delete the file after the response is parsed, whether the request succeeds or fails.
- Do not keep an image history, user media library, or permanent uploads directory for this POC.

## Minimal UI Interaction Flow
1. Open the single review page.
2. Choose text question or image input.
3. Enter a question or provide one image through upload or camera capture.
4. Submit the request.
5. See a loading state while FastAPI calls Gemini.
6. View one result page section with detected subject, detected topic, explanation, example, and quiz.
7. Optionally clear the form and try another input.

## Notes
- Tradeoffs:
  - The architecture favors one simple route and one result schema over specialized endpoints.
  - Camera capture is treated as a frontend convenience layer over normal image upload.
  - Parsing model output into strict JSON adds some fragility, but it keeps the UI much simpler.
- Simplifications:
  - No login or user state.
  - No database-backed history.
  - No background jobs, queues, or asynchronous processing beyond the normal request-response cycle.
  - No permanent image storage.
