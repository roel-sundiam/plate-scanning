export interface Plate {
  _id: string;
  plateNumber: string;
  gateId: string;
  confidence: number;
  timestamp: Date;
  imageUrl?: string;
  verified: boolean;
  correctedPlateNumber?: string;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface PlateSearchParams {
  page?: number;
  limit?: number;
  gateId?: string;
  plateNumber?: string;
  startDate?: string;
  endDate?: string;
  verified?: boolean;
}

export interface PlateResponse {
  success: boolean;
  data: Plate[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    pages: number;
  };
}

export interface Statistics {
  summary: {
    totalDetections: number;
    uniquePlatesCount: number;
    avgConfidence: number;
    verifiedCount: number;
  };
  recentPlates: Plate[];
  topPlates: Array<{
    _id: string;
    count: number;
    lastSeen: Date;
  }>;
}
