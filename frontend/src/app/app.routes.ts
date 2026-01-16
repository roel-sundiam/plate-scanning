import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { PlateListComponent } from './components/plate-list/plate-list.component';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'plates', component: PlateListComponent },
  { path: '**', redirectTo: '' }
];
