const state = {
  config: null,
  selection: { grade: '', subject: '', mode: 'review' },
  dataset: null,
  questions: [],
  answers: {},
};

const pages = {
  home: document.getElementById('home-page'),
  review: document.getElementById('review-page'),
  exam: document.getElementById('exam-page'),
  result: document.getElementById('result-page'),
};

function showPage(key) {
  Object.entries(pages).forEach(([name, element]) => {
    element.classList.toggle('active', name === key);
  });
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderHome() {
  const { grades = [], subjects = [], modes = [] } = state.config || {};
  pages.home.innerHTML = `
    <h2>Home</h2>
    <p class="subcopy">Select a grade, subject, and mode to begin.</p>
    <div class="form-grid">
      <label>Grade
        <select id="grade-select">${grades.map((grade) => `<option value="${grade}">${grade}</option>`).join('')}</select>
      </label>
      <label>Subject
        <select id="subject-select">${subjects.map((subject) => `<option value="${subject}">${subject}</option>`).join('')}</select>
      </label>
      <label>Mode
        <select id="mode-select">${modes.map((mode) => `<option value="${mode}">${mode}</option>`).join('')}</select>
      </label>
    </div>
    <div class="actions">
      <button id="start-btn">Start</button>
    </div>
  `;

  document.getElementById('grade-select').value = state.selection.grade || grades[0] || '';
  document.getElementById('subject-select').value = state.selection.subject || subjects[0] || '';
  document.getElementById('mode-select').value = state.selection.mode || 'review';

  document.getElementById('start-btn').addEventListener('click', async () => {
    state.selection = {
      grade: document.getElementById('grade-select').value,
      subject: document.getElementById('subject-select').value,
      mode: document.getElementById('mode-select').value,
    };
    await loadQuestions();
  });
}

function createQuestionCard(question, index, mode) {
  const template = document.getElementById('question-template');
  const fragment = template.content.cloneNode(true);
  const article = fragment.querySelector('.question-card');
  article.dataset.questionId = question.id;
  fragment.querySelector('.topic').textContent = question.topic;
  fragment.querySelector('.index').textContent = `Question ${index + 1}`;
  fragment.querySelector('.question-text').textContent = question.question;
  const choices = fragment.querySelector('.choices');
  const feedback = fragment.querySelector('.review-feedback');

  question.choices.forEach((choice) => {
    const label = document.createElement('label');
    label.className = 'choice';
    label.innerHTML = `
      <input type="radio" name="${question.id}" value="${choice}" ${state.answers[question.id] === choice ? 'checked' : ''} />
      <span>${choice}</span>
    `;

    label.querySelector('input').addEventListener('change', () => {
      state.answers[question.id] = choice;
      if (mode === 'review') {
        const isCorrect = choice === question.answer;
        feedback.classList.remove('hidden');
        feedback.innerHTML = `<strong>${isCorrect ? 'Correct' : 'Try again'}</strong><p>${question.explanation || `The correct answer is ${question.answer}.`}</p>`;
        Array.from(choices.children).forEach((node) => {
          const input = node.querySelector('input');
          node.classList.remove('correct', 'incorrect');
          if (input.value === question.answer) node.classList.add('correct');
          if (input.checked && input.value !== question.answer) node.classList.add('incorrect');
        });
      }
    });

    choices.appendChild(label);
  });

  return fragment;
}

function renderQuizPage(pageKey, mode) {
  const page = pages[pageKey];
  const title = mode === 'review' ? 'Review Mode' : 'Exam Mode';
  const helper = mode === 'review'
    ? 'Instant feedback is shown after every answer.'
    : 'Answer all questions, then submit to view your score.';

  page.innerHTML = `
    <div class="summary-grid">
      <div>
        <h2>${title}</h2>
        <p class="subcopy">${helper}</p>
      </div>
      <div class="review-feedback">
        <strong>${state.dataset.subject}</strong>
        <p>Grade ${state.dataset.grade} · ${state.questions.length} questions</p>
      </div>
    </div>
    <div id="question-list"></div>
    <div class="actions">
      <button class="secondary" id="back-home-btn">Back Home</button>
      ${mode === 'exam' ? '<button id="submit-exam-btn">Submit Exam</button>' : '<button id="finish-review-btn">Finish Review</button>'}
    </div>
  `;

  const list = page.querySelector('#question-list');
  state.questions.forEach((question, index) => {
    list.appendChild(createQuestionCard(question, index, mode));
  });

  page.querySelector('#back-home-btn').addEventListener('click', () => showPage('home'));
  const actionButton = mode === 'exam' ? '#submit-exam-btn' : '#finish-review-btn';
  page.querySelector(actionButton).addEventListener('click', submitResults);
}

async function loadQuestions() {
  state.answers = {};
  const params = new URLSearchParams(state.selection);
  const payload = await api(`/api/questions?${params.toString()}`);
  state.dataset = payload.dataset;
  state.questions = payload.questions;
  renderQuizPage(state.selection.mode, state.selection.mode);
  showPage(state.selection.mode);
}

async function submitResults() {
  const payload = await api('/api/submit', {
    method: 'POST',
    body: JSON.stringify({ datasetId: state.dataset.id, answers: state.answers }),
  });

  pages.result.innerHTML = `
    <h2>Result Page</h2>
    <p class="score">${payload.score}/${payload.total}</p>
    <p class="subcopy">Here is a quick summary of your answers.</p>
    <div class="result-list">
      ${payload.results.map((result) => `
        <article class="result-item">
          <strong>${result.isCorrect ? '✅ Correct' : '❌ Incorrect'}</strong>
          <p>${result.question}</p>
          <p><strong>Your answer:</strong> ${result.selected || 'No answer selected'}</p>
          <p><strong>Correct answer:</strong> ${result.correctAnswer}</p>
          <p>${result.explanation || ''}</p>
        </article>
      `).join('')}
    </div>
    <div class="actions">
      <button class="secondary" id="restart-btn">Back Home</button>
      <button id="retry-btn">Try Again</button>
    </div>
  `;

  document.getElementById('restart-btn').addEventListener('click', () => showPage('home'));
  document.getElementById('retry-btn').addEventListener('click', loadQuestions);
  showPage('result');
}

async function init() {
  state.config = await api('/api/config');
  state.selection.grade = state.config.grades[0] || '';
  state.selection.subject = state.config.subjects[0] || '';
  renderHome();
  showPage('home');
}

init().catch((error) => {
  pages.home.innerHTML = `<p>Unable to load app: ${error.message}</p>`;
  showPage('home');
});
