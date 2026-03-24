import { Component } from '@angular/core';

import { ReviewPageComponent } from './review-page/review-page.component';

@Component({
  selector: 'app-root',
  imports: [ReviewPageComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
}
