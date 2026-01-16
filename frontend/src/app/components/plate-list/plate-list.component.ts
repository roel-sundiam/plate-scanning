import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

import { PlateService } from '../../services/plate.service';
import { Plate, PlateSearchParams } from '../../models/plate.model';

@Component({
  selector: 'app-plate-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    MatTableModule,
    MatPaginatorModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatChipsModule,
    MatDialogModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './plate-list.component.html',
  styleUrls: ['./plate-list.component.scss']
})
export class PlateListComponent implements OnInit, OnDestroy {
  plates: Plate[] = [];
  displayedColumns: string[] = ['timestamp', 'plateNumber', 'gateId', 'confidence', 'verified', 'actions'];
  
  // Pagination
  totalPlates = 0;
  pageSize = 20;
  pageIndex = 0;
  
  // Filters
  searchParams: PlateSearchParams = {
    page: 1,
    limit: 20
  };
  
  // Auto-refresh
  private refreshSubscription?: Subscription;
  autoRefresh = true;
  refreshInterval = 5000; // 5 seconds
  
  loading = false;

  constructor(private plateService: PlateService) { }

  ngOnInit(): void {
    this.loadPlates();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    this.stopAutoRefresh();
  }

  loadPlates(): void {
    this.loading = true;
    this.plateService.getPlates(this.searchParams).subscribe({
      next: (response) => {
        this.plates = response.data;
        this.totalPlates = response.pagination.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading plates:', error);
        this.loading = false;
      }
    });
  }

  onPageChange(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.searchParams.page = event.pageIndex + 1;
    this.searchParams.limit = event.pageSize;
    this.loadPlates();
  }

  onSearch(plateNumber: string): void {
    this.searchParams.plateNumber = plateNumber || undefined;
    this.searchParams.page = 1;
    this.pageIndex = 0;
    this.loadPlates();
  }

  onGateFilter(gateId: string): void {
    this.searchParams.gateId = gateId || undefined;
    this.searchParams.page = 1;
    this.pageIndex = 0;
    this.loadPlates();
  }

  onDateRangeFilter(startDate: Date | null, endDate: Date | null): void {
    this.searchParams.startDate = startDate ? startDate.toISOString() : undefined;
    this.searchParams.endDate = endDate ? endDate.toISOString() : undefined;
    this.searchParams.page = 1;
    this.pageIndex = 0;
    this.loadPlates();
  }

  clearFilters(): void {
    this.searchParams = {
      page: 1,
      limit: this.pageSize
    };
    this.pageIndex = 0;
    this.loadPlates();
  }

  deletePlate(id: string): void {
    if (confirm('Are you sure you want to delete this plate record?')) {
      this.plateService.deletePlate(id).subscribe({
        next: () => {
          this.loadPlates();
        },
        error: (error) => {
          console.error('Error deleting plate:', error);
          alert('Failed to delete plate');
        }
      });
    }
  }

  getImageUrl(imageUrl: string): string {
    return this.plateService.getImageUrl(imageUrl);
  }

  toggleAutoRefresh(): void {
    this.autoRefresh = !this.autoRefresh;
    if (this.autoRefresh) {
      this.startAutoRefresh();
    } else {
      this.stopAutoRefresh();
    }
  }

  private startAutoRefresh(): void {
    if (this.autoRefresh) {
      this.refreshSubscription = interval(this.refreshInterval)
        .pipe(switchMap(() => this.plateService.getPlates(this.searchParams)))
        .subscribe({
          next: (response) => {
            this.plates = response.data;
            this.totalPlates = response.pagination.total;
          },
          error: (error) => {
            console.error('Auto-refresh error:', error);
          }
        });
    }
  }

  private stopAutoRefresh(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
  }

  getConfidenceColor(confidence: number): string {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
  }

  formatDate(date: Date): string {
    return new Date(date).toLocaleString();
  }
}
