import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { ReviewResult } from '../types/review-result';

interface ReviewApiResponse {
  detected_subject?: string;
  detected_topic?: string;
  explanation_bullets?: string[];
  example?: string;
  quiz?: Array<{
    question: string;
    choices: string[];
    correct_answer: string;
    explanation?: string;
  }>;
  result?: string;
}

@Injectable({ providedIn: 'root' })
export class ReviewApiService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = `${environment.apiBaseUrl}/api/review`;

  submitQuestion(
    question: string,
    subject: string,
    includeQuiz: boolean,
    gradeLevel: string,
    questionCount: number,
  ): Observable<ReviewResult> {
    const formData = new FormData();
    formData.append('question', question);
    formData.append('subject', subject);
    formData.append('include_quiz', String(includeQuiz));
    formData.append('grade_level', gradeLevel);
    formData.append('question_count', String(questionCount));
    return this.http.post<ReviewApiResponse>(this.endpoint, formData).pipe(map(this.mapResponse));
  }

  submitImage(
    image: File,
    imageContext: string,
    subject: string,
    includeQuiz: boolean,
    gradeLevel: string,
    questionCount: number,
  ): Observable<ReviewResult> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('image_context', imageContext);
    formData.append('subject', subject);
    formData.append('include_quiz', String(includeQuiz));
    formData.append('grade_level', gradeLevel);
    formData.append('question_count', String(questionCount));
    return this.http.post<ReviewApiResponse>(this.endpoint, formData).pipe(map(this.mapResponse));
  }

  private readonly mapResponse = (response: ReviewApiResponse): ReviewResult => {
    if (response.result) {
      return this.parseTextResult(response.result);
    }

    return {
      detectedSubject: response.detected_subject ?? 'Unknown',
      detectedTopic: response.detected_topic ?? 'Unknown',
      explanationBullets: response.explanation_bullets ?? [],
      example: response.example ?? '',
      quiz: (response.quiz ?? []).map((item) => ({
        question: item.question,
        choices: item.choices,
        correctAnswer: item.correct_answer,
        explanation: item.explanation ?? '',
      })),
    };
  };

  private parseTextResult(result: string): ReviewResult {
    const lines = result.split('\n').map((line) => line.trim()).filter(Boolean);

    const detectedSubject = this.extractValue(lines, 'Detected Subject:') ?? 'Unknown';
    const detectedTopic = this.extractValue(lines, 'Detected Topic:') ?? 'Unknown';

    const explanationBullets = this.extractSection(lines, 'Explanation:', ['Example:', 'Quiz:'])
      .map((line) => line.replace(/^[-•]\s*/, '').trim())
      .filter(Boolean);

    const exampleLines = this.extractSection(lines, 'Example:', ['Quiz:']);
    const example = exampleLines.join(' ').trim();

    const quizLines = this.extractSection(lines, 'Quiz:', []);
    const quiz = this.parseQuiz(quizLines);

    return {
      detectedSubject,
      detectedTopic,
      explanationBullets,
      example,
      quiz,
    };
  }

  private extractValue(lines: string[], prefix: string): string | null {
    const line = lines.find((item) => item.startsWith(prefix));
    return line ? line.slice(prefix.length).trim() : null;
  }

  private extractSection(lines: string[], startMarker: string, endMarkers: string[]): string[] {
    const startIndex = lines.findIndex((line) => line === startMarker);
    if (startIndex === -1) {
      return [];
    }

    const section: string[] = [];
    for (const line of lines.slice(startIndex + 1)) {
      if (endMarkers.includes(line)) {
        break;
      }
      section.push(line);
    }
    return section;
  }

  private parseQuiz(lines: string[]): ReviewResult['quiz'] {
    const quiz: ReviewResult['quiz'] = [];
    let currentQuestion: ReviewResult['quiz'][number] | null = null;

    for (const line of lines) {
      if (/^\d+\.\s+/.test(line)) {
        if (currentQuestion) {
          quiz.push(currentQuestion);
        }
        currentQuestion = {
          question: line.replace(/^\d+\.\s+/, '').trim(),
          choices: [],
          correctAnswer: '',
          explanation: '',
        };
        continue;
      }

      if (!currentQuestion) {
        continue;
      }

      if (/^[A-D]\.\s+/.test(line)) {
        currentQuestion.choices.push(line.replace(/^[A-D]\.\s+/, '').trim());
        continue;
      }

      if (line.startsWith('Answer:')) {
        currentQuestion.correctAnswer = line.replace('Answer:', '').trim();
        continue;
      }

      if (line.startsWith('Explanation:')) {
        currentQuestion.explanation = line.replace('Explanation:', '').trim();
      }
    }

    if (currentQuestion) {
      quiz.push(currentQuestion);
    }

    return quiz;
  }
}
