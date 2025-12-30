import {HttpClient} from '@angular/common/http';
import {Component} from '@angular/core';
import {Inject} from '@angular/core';

import {BASE_URL} from './app-config';

// Output format of SolutionStatus API
export declare interface SolutionStatus {
  state: number;
  state_reason: number;
  name: string;
  display_name: string;
  simulated: boolean;
  cluster_name: string;
  platform_version: number;
}

// Output format of ExecutiveService.ListOperations API
export declare interface Operation {
  name: string;
  // tslint:disable:no-any
  metadata?: any;
  done: boolean;
  error?: any;
  result?: any;
  // tslint:enable:no-any
}

@Component({
  selector: 'app-root',
  standalone: true,
  template: `
    <h1>Hello, welcome to {{ title }}!</h1>
    <h2>Service-based HMI for Flowstate</h2>

    <div>
      <button type="button" id="load-operation-id" (click)="listOperations()">
        Load Operation ID
      </button>
      <div class="output">
        @if (operationResponse !== null) {
          @for (opID of operationResponse; track $index) {
            <p>Operation ID: {{ opID.name }}</p>
          }
        } @else {
          <p>No operations running</p>
        }
      </div>
    </div>

    <div class="container">
      <button
        type="button"
        id="load-operation-id"
        (click)="getSolutionStatus()"
      >
        Load Solution status
      </button>

      @if (statusResponse !== null) {
        <div class="output">
          <p>Solution name: {{ statusResponse.display_name }}</p>
          <p>Current status: {{ statusResponse.state }}</p>
          <p>Cluster id: {{ statusResponse.cluster_name }}</p>
        </div>
      }
    </div>
  `,
  styles: [],
})
export class App {
  title = 'HMI-angular';
  operationID: number | null = null;
  operationResponse: Operation[] = []; // Object to parse the Executive Service response
  statusResponse: SolutionStatus | null = null; // Object to parse the Solution status response

  constructor(
    private http: HttpClient,
    @Inject(BASE_URL) private readonly urlPrefix: string,
  ) {}

  listOperations(): void {
    const apiURL =
      window.location.origin + this.urlPrefix + 'api/executive/operations';
    this.http.get<Operation[]>(apiURL).subscribe(
      (response) => {
        this.operationResponse = response;
      },
      (error) => {
        console.error('Error while running executive service client');
        this.operationID = null;
      },
    );
  }

  getSolutionStatus(): void {
    const apiURL =
      window.location.origin + this.urlPrefix + 'api/solution/status';
    this.http.get<SolutionStatus>(apiURL).subscribe(
      (response) => {
        this.statusResponse = response;
      },
      (error) => {
        console.error('Error while running solution status client');
        this.operationID = null;
      },
    );
  }
}
