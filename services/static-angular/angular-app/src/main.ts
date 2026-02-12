import {provideHttpClient} from '@angular/common/http';
import {bootstrapApplication} from '@angular/platform-browser';

import {App} from './app/app';

bootstrapApplication(App, {
  providers: [provideHttpClient()],
}).catch((err) => console.error(err));
