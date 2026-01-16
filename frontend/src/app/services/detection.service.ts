import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface DetectionStatus {
  success: boolean;
  status: 'stopped' | 'starting' | 'running' | 'stopping';
  isRunning: boolean;
  pid?: number;
}

export interface DetectionResponse {
  success: boolean;
  message: string;
  status?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class DetectionService {
  private apiUrl = `${environment.apiUrl}/detection`;

  constructor(private http: HttpClient) { }

  startDetection(source: string = 'iphone'): Observable<DetectionResponse> {
    return this.http.post<DetectionResponse>(`${this.apiUrl}/start`, { source });
  }

  stopDetection(): Observable<DetectionResponse> {
    return this.http.post<DetectionResponse>(`${this.apiUrl}/stop`, {});
  }

  getStatus(): Observable<DetectionStatus> {
    return this.http.get<DetectionStatus>(`${this.apiUrl}/status`);
  }

  // Auto-polling status every 3 seconds
  pollStatus(): Observable<DetectionStatus> {
    return interval(3000).pipe(
      startWith(0),
      switchMap(() => this.getStatus())
    );
  }
}
