export interface QuizItem {
  question: string;
  choices: string[];
  correctAnswer: string;
  explanation: string;
}

export interface ReviewResult {
  detectedSubject: string;
  detectedTopic: string;
  explanationBullets: string[];
  example: string;
  quiz: QuizItem[];
}
