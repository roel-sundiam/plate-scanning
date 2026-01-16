import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import { DetectionService, DetectionStatus } from '../../services/detection.service';

@Component({
  selector: 'app-detection-control',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatSnackBarModule
  ],
  templateUrl: './detection-control.component.html',
  styleUrls: ['./detection-control.component.scss']
})
export class DetectionControlComponent implements OnInit, OnDestroy {
  status: DetectionStatus | null = null;
  selectedSource: string = 'iphone';
  loading = false;
  
  private statusSubscription?: Subscription;

  sources = [
    { value: 'iphone', label: 'iPhone Camera (DroidCam)' },
    { value: 'webcam', label: 'Webcam' },
    { value: 'rtsp', label: 'RTSP Camera' }
  ];

  constructor(
    private detectionService: DetectionService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadStatus();
    this.startStatusPolling();
  }

  ngOnDestroy(): void {
    this.stopStatusPolling();
  }

  loadStatus(): void {
    this.detectionService.getStatus().subscribe({
      next: (status) => {
        this.status = status;
      },
      error: (err) => {
        console.error('Error loading status:', err);
      }
    });
  }

  startStatusPolling(): void {
    this.statusSubscription = this.detectionService.pollStatus().subscribe({
      next: (status) => {
        this.status = status;
      },
      error: (err) => {
        console.error('Error polling status:', err);
      }
    });
  }

  stopStatusPolling(): void {
    if (this.statusSubscription) {
      this.statusSubscription.unsubscribe();
    }
  }

  startDetection(): void {
    this.loading = true;
    
    this.detectionService.startDetection(this.selectedSource).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.snackBar.open('✓ Detection service started successfully!', 'Close', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadStatus();
        } else {
          this.snackBar.open(`Failed: ${response.message}`, 'Close', {
            duration: 5000,
            panelClass: ['error-snackbar']
          });
        }
      },
      error: (err) => {
        this.loading = false;
        this.snackBar.open(`Error: ${err.error?.message || 'Failed to start detection'}`, 'Close', {
          duration: 5000,
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  stopDetection(): void {
    this.loading = true;
    
    this.detectionService.stopDetection().subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.snackBar.open('✓ Detection service stopped', 'Close', {
            duration: 3000,
            panelClass: ['success-snackbar']
          });
          this.loadStatus();
        } else {
          this.snackBar.open(`Failed: ${response.message}`, 'Close', {
            duration: 5000,
            panelClass: ['error-snackbar']
          });
        }
      },
      error: (err) => {
        this.loading = false;
        this.snackBar.open(`Error: ${err.error?.message || 'Failed to stop detection'}`, 'Close', {
          duration: 5000,
          panelClass: ['error-snackbar']
        });
      }
    });
  }

  getStatusColor(): string {
    if (!this.status) return 'grey';
    
    switch (this.status.status) {
      case 'running': return 'green';
      case 'starting': return 'orange';
      case 'stopping': return 'orange';
      case 'stopped': return 'red';
      default: return 'grey';
    }
  }

  getStatusIcon(): string {
    if (!this.status) return 'help';
    
    switch (this.status.status) {
      case 'running': return 'play_circle';
      case 'starting': return 'hourglass_empty';
      case 'stopping': return 'hourglass_empty';
      case 'stopped': return 'stop_circle';
      default: return 'help';
    }
  }

  getStatusText(): string {
    if (!this.status) return 'Unknown';
    return this.status.status.charAt(0).toUpperCase() + this.status.status.slice(1);
  }

  canStart(): boolean {
    return !this.loading && this.status?.status === 'stopped';
  }

  canStop(): boolean {
    return !this.loading && this.status?.status === 'running';
  }
}
