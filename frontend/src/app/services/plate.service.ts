import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Plate, PlateSearchParams, PlateResponse, Statistics } from '../models/plate.model';

@Injectable({
  providedIn: 'root'
})
export class PlateService {
  private apiUrl = `${environment.apiUrl}/plates`;

  constructor(private http: HttpClient) { }

  // Get all plates with filters
  getPlates(params: PlateSearchParams = {}): Observable<PlateResponse> {
    let httpParams = new HttpParams();
    
    Object.keys(params).forEach(key => {
      const value = params[key as keyof PlateSearchParams];
      if (value !== undefined && value !== null) {
        httpParams = httpParams.set(key, value.toString());
      }
    });

    return this.http.get<PlateResponse>(this.apiUrl, { params: httpParams });
  }

  // Get single plate
  getPlate(id: string): Observable<{ success: boolean; data: Plate }> {
    return this.http.get<{ success: boolean; data: Plate }>(`${this.apiUrl}/${id}`);
  }

  // Search plates
  searchPlates(plateNumber: string): Observable<{ success: boolean; count: number; data: Plate[] }> {
    return this.http.get<{ success: boolean; count: number; data: Plate[] }>(
      `${this.apiUrl}/search/${plateNumber}`
    );
  }

  // Update plate (manual correction)
  updatePlate(id: string, data: Partial<Plate>): Observable<{ success: boolean; data: Plate }> {
    return this.http.put<{ success: boolean; data: Plate }>(`${this.apiUrl}/${id}`, data);
  }

  // Delete plate
  deletePlate(id: string): Observable<{ success: boolean; message: string }> {
    return this.http.delete<{ success: boolean; message: string }>(`${this.apiUrl}/${id}`);
  }

  // Get statistics
  getStatistics(params: { gateId?: string; startDate?: string; endDate?: string } = {}): 
    Observable<{ success: boolean; data: Statistics }> {
    let httpParams = new HttpParams();
    
    Object.keys(params).forEach(key => {
      const value = params[key as keyof typeof params];
      if (value) {
        httpParams = httpParams.set(key, value);
      }
    });

    return this.http.get<{ success: boolean; data: Statistics }>(
      `${this.apiUrl}/statistics`,
      { params: httpParams }
    );
  }

  // Get image URL
  getImageUrl(imageUrl: string): string {
    if (!imageUrl) return '';
    return imageUrl.startsWith('http') ? imageUrl : `${environment.apiUrl.replace('/api', '')}${imageUrl}`;
  }
}
