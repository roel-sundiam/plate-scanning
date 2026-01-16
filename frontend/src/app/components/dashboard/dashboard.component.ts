import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { PlateService } from '../../services/plate.service';
import { Statistics } from '../../models/plate.model';
import { DetectionControlComponent } from '../detection-control/detection-control.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatGridListModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    DetectionControlComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  stats: Statistics | null = null;
  loading = true;
  error: string | null = null;
  
  private refreshSubscription?: Subscription;
  private refreshInterval = 5000; // 5 seconds - auto refresh for live updates

  constructor(private plateService: PlateService) {}

  ngOnInit(): void {
    this.loadStatistics();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
  }

  loadStatistics(): void {
    this.loading = true;
    this.error = null;
    
    this.plateService.getStatistics().subscribe({
      next: (response) => {
        this.stats = response.data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load statistics';
        this.loading = false;
        console.error('Error loading statistics:', err);
      }
    });
  }

  startAutoRefresh(): void {
    this.refreshSubscription = interval(this.refreshInterval)
      .pipe(
        switchMap(() => this.plateService.getStatistics())
      )
      .subscribe({
        next: (response) => {
          this.stats = response.data;
          this.error = null;
        },
        error: (err) => {
          console.error('Error refreshing statistics:', err);
        }
      });
  }

  stopAutoRefresh(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
  }

  getConfidenceColor(confidence: number): string {
    if (confidence >= 0.9) return '#4caf50'; // Green
    if (confidence >= 0.7) return '#ff9800'; // Orange
    return '#f44336'; // Red
  }

  formatPercentage(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }
}
