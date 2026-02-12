import {HttpClient} from '@angular/common/http';
import {Component} from '@angular/core';

@Component({
  selector: 'app-root',
  standalone: true,
  template: `
    <style>
      .aligned {
        align-content: center;
        text-align: center;
      }
    </style>
    <h1>Hello, welcome to {{ title }}!</h1>
    <div class="aligned">
      <img src="favicon.ico" alt="logo" height="75" />
      <h2>WebService example</h2>
    </div>

    <div class="container">
      <button type="button" id="placeholder">Your API request here</button>
    </div>
  `,
  styles: [],
})
export class App {
  title = 'Flowstate';
  constructor(private http: HttpClient) {}
}
