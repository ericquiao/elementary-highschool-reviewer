import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize, Observable } from 'rxjs';

import { ReviewApiService } from '../services/review-api.service';
import { ReviewResult } from '../types/review-result';

type InputMode = 'text' | 'image';

@Component({
  selector: 'app-review-page',
  imports: [FormsModule],
  templateUrl: './review-page.component.html',
  styleUrl: './review-page.component.css',
})
export class ReviewPageComponent {
  protected readonly gradeOptions = Array.from({ length: 12 }, (_, index) => `Grade ${index + 1}`);
  protected readonly subjectOptions = [
    'Math',
    'Science',
    'English',
    'MAPEH',
    'ESP',
    'TLE',
    'Araling Panlipunan',
  ];
  protected readonly mode = signal<InputMode>('text');
  protected readonly subject = signal('Science');
  protected readonly gradeLevel = signal('Grade 5');
  protected readonly questionCount = signal(10);
  protected readonly question = signal('');
  protected readonly imageContext = signal('');
  protected readonly includeQuiz = signal(true);
  protected readonly selectedFile = signal<File | null>(null);
  protected readonly selectedFileName = signal('');
  protected readonly isLoading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly result = signal<ReviewResult | null>(null);
  protected readonly selectedAnswers = signal<Record<number, string>>({});

  private readonly reviewApi = inject(ReviewApiService);

  protected setMode(mode: InputMode): void {
    this.mode.set(mode);
    this.errorMessage.set('');
    this.result.set(null);
    this.selectedAnswers.set({});
  }

  protected onQuestionChange(value: string): void {
    this.question.set(value);
  }

  protected setSubject(value: string): void {
    this.subject.set(value);
    this.result.set(null);
    this.selectedAnswers.set({});
  }

  protected onImageContextChange(value: string): void {
    this.imageContext.set(value);
  }

  protected setGradeLevel(value: string): void {
    this.gradeLevel.set(value);
    this.result.set(null);
    this.selectedAnswers.set({});
  }

  protected setQuestionCount(value: string | number): void {
    const parsed = Number(value);
    const nextValue = Number.isFinite(parsed) ? Math.min(30, Math.max(1, Math.round(parsed))) : 10;
    this.questionCount.set(nextValue);
    this.result.set(null);
    this.selectedAnswers.set({});
  }

  protected onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.selectedFile.set(file);
    this.selectedFileName.set(file?.name ?? '');
    this.errorMessage.set('');
  }

  protected clearSelectedImage(): void {
    this.selectedFile.set(null);
    this.selectedFileName.set('');
    this.imageContext.set('');
  }

  protected setIncludeQuiz(includeQuiz: boolean): void {
    this.includeQuiz.set(includeQuiz);
    this.result.set(null);
    this.selectedAnswers.set({});
  }

  protected chooseAnswer(index: number, choice: string): void {
    if (this.selectedAnswers()[index]) {
      return;
    }
    this.selectedAnswers.update((current) => ({ ...current, [index]: choice }));
  }

  protected isAnswered(index: number): boolean {
    return Boolean(this.selectedAnswers()[index]);
  }

  protected isCorrectChoice(index: number, correctAnswer: string, choice: string): boolean {
    if (!this.isAnswered(index)) {
      return false;
    }
    return this.normalizeAnswer(correctAnswer) === this.normalizeAnswer(choice);
  }

  protected isWrongSelectedChoice(index: number, correctAnswer: string, choice: string): boolean {
    if (!this.isAnswered(index)) {
      return false;
    }
    const selected = this.selectedAnswers()[index];
    return this.normalizeAnswer(selected) === this.normalizeAnswer(choice)
      && this.normalizeAnswer(correctAnswer) !== this.normalizeAnswer(choice);
  }

  protected selectedAnswerText(index: number): string | null {
    return this.selectedAnswers()[index] ?? null;
  }

  protected selectedAnswerIsCorrect(index: number, correctAnswer: string): boolean {
    const selected = this.selectedAnswers()[index];
    if (!selected) {
      return false;
    }
    return this.normalizeAnswer(selected) === this.normalizeAnswer(correctAnswer);
  }

  private normalizeAnswer(value: string): string {
    return value.replace(/^[A-D][.)]\s*/, '').trim().toLowerCase();
  }

  protected submit(): void {
    this.errorMessage.set('');
    this.result.set(null);
    this.selectedAnswers.set({});

    if (this.mode() === 'text') {
      const question = this.question().trim();
      if (!question) {
        this.errorMessage.set('Enter a study question first.');
        return;
      }
      this.runRequest(
        this.reviewApi.submitQuestion(
          question,
          this.subject(),
          this.includeQuiz(),
          this.gradeLevel(),
          this.questionCount(),
        ),
      );
      return;
    }

    const image = this.selectedFile();
    if (!image) {
      this.errorMessage.set('Choose an image or capture one before submitting.');
      return;
    }
    this.runRequest(
      this.reviewApi.submitImage(
        image,
        this.imageContext().trim(),
        this.subject(),
        this.includeQuiz(),
        this.gradeLevel(),
        this.questionCount(),
      ),
    );
  }

  private runRequest(request$: Observable<ReviewResult>): void {
    this.isLoading.set(true);
    request$
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: (result) => this.result.set(result),
        error: (error: HttpErrorResponse) => {
          const detail = typeof error.error?.detail === 'string' ? error.error.detail : null;
          this.errorMessage.set(detail ?? 'Something went wrong while generating the review.');
        },
      });
  }
}
