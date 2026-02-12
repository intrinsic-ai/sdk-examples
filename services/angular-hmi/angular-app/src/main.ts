import {provideHttpClient} from '@angular/common/http';
import {bootstrapApplication} from '@angular/platform-browser';

import {App} from './app/app';
import {BASE_URL} from './app/app-config';

// For in-cluster on an arbitrary cluster.
const DEFAULT_BASE_URL = '/api/v1alpha1/';
// testing with ng serve
// const DEFAULT_BASE_URL = 'http://workcell.lan:17080/ext/services/{name}';

const runtimeURL = (window as any).__env?.BASE_URL || DEFAULT_BASE_URL;

bootstrapApplication(App, {
  providers: [
    provideHttpClient(),
    // Provide baseURL for the frontend
    {provide: BASE_URL, useValue: runtimeURL},
  ],
}).catch((err) => console.error(err));
