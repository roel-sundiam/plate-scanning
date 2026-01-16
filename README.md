# License Plate Scanning System

A comprehensive license plate scanning system for guard house gates with real-time detection, API backend, and web dashboard.

## Features

- 🎥 Video capture from iPhone (DroidCam/IP Webcam) or RTSP cameras
- 🔍 Automatic license plate detection using YOLO and OCR
- 🗄️ MongoDB storage with timestamps and snapshots
- 🚀 REST API built with Node.js and Express
- 📊 Angular dashboard for monitoring and management
- 🔄 Duplicate detection with configurable time windows
- 📸 Optional snapshot saving with each detection
- 🔌 Modular design for easy camera source switching

## Architecture

```
┌─────────────────────┐
│   iPhone/RTSP       │
│   Camera Feed       │
└──────────┬──────────┘
           │
┌──────────▼──────────────────────┐
│  Python Detection Service       │
│  - Video capture                │
│  - YOLO plate detection         │
│  - OCR (Tesseract/API)         │
│  - Duplicate filtering          │
└──────────┬──────────────────────┘
           │ HTTP POST
┌──────────▼──────────────────────┐
│  Node.js Express API            │
│  - Plate storage                │
│  - Query endpoints              │
│  - Image management             │
└──────────┬──────────────────────┘
           │
┌──────────▼──────────────────────┐
│  MongoDB Database               │
│  - Plates collection            │
│  - Timestamps & metadata        │
└─────────────────────────────────┘
           ▲
           │
┌──────────┴──────────────────────┐
│  Angular Dashboard              │
│  - Live feed display            │
│  - Search & filter              │
│  - Manual corrections           │
└─────────────────────────────────┘
```

## Technology Stack

### Detection Service (Python)
- **OpenCV**: Video capture and processing
- **YOLO**: License plate detection
- **Tesseract OCR**: Text recognition
- **Requests**: API communication
- **Alternative**: Plate Recognizer API

### Backend (Node.js)
- **Express.js**: REST API framework
- **MongoDB & Mongoose**: Database
- **Multer**: Image upload handling
- **Moment.js**: Timestamp management
- **CORS**: Cross-origin support

### Frontend (Angular)
- **Angular 17+**: Framework
- **RxJS**: Reactive programming
- **Angular Material**: UI components
- **Chart.js**: Analytics visualization

## Project Structure

```
License_Plate_Scanning/
├── python-service/          # Detection service
│   ├── main.py             # Main video processing
│   ├── detector.py         # Plate detection logic
│   ├── camera_sources.py   # Camera abstraction
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
├── backend/                # Node.js API
│   ├── src/
│   │   ├── models/        # MongoDB schemas
│   │   ├── routes/        # API endpoints
│   │   ├── controllers/   # Business logic
│   │   └── server.js      # Entry point
│   └── package.json       # Node dependencies
├── frontend/              # Angular dashboard
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── models/
│   │   └── environments/
│   └── package.json
├── docker-compose.yml     # Container orchestration
└── README.md             # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB 5.0+
- iPhone with DroidCam or IP Webcam app (for development)

### 1. Set Up Python Detection Service

```bash
cd python-service
pip install -r requirements.txt
python main.py --source iphone
```

### 2. Set Up Backend API

```bash
cd backend
npm install
npm start
```

### 3. Set Up Frontend Dashboard

```bash
cd frontend
npm install
ng serve
```

### 4. Access the Dashboard

Open http://localhost:4200 in your browser.

## Camera Setup

### iPhone Camera (Development)

1. **Install DroidCam** (iOS):
   - Download from App Store
   - Note the IP address shown (e.g., `192.168.1.100:4747`)

2. **Update Configuration**:
   ```python
   IPHONE_URL = "http://192.168.1.100:4747/video"
   ```

### RTSP Camera (Production)

1. **Update Configuration**:
   ```python
   RTSP_URL = "rtsp://username:password@camera-ip:554/stream"
   ```

2. **Switch Source**:
   ```bash
   python main.py --source rtsp
   ```

## Configuration

### Python Service (config.py)

```python
# Camera sources
IPHONE_URL = "http://192.168.1.100:4747/video"
RTSP_URL = "rtsp://admin:password@192.168.1.50:554/stream"

# API endpoint
API_URL = "http://localhost:3000/api/plates"

# Detection settings
CONFIDENCE_THRESHOLD = 0.5
DUPLICATE_WINDOW_SECONDS = 60
GATE_IDENTIFIER = "gate_01"
```

### Backend (backend/.env)

```env
PORT=3000
MONGODB_URI=mongodb://localhost:27017/license_plates
DUPLICATE_WINDOW=60
IMAGE_STORAGE_PATH=./uploads
```

### Frontend (frontend/src/environments/)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api'
};
```

## API Endpoints

### POST /api/plates
Create new plate detection
```json
{
  "plateNumber": "ABC123",
  "gateId": "gate_01",
  "confidence": 0.95,
  "image": "base64-encoded-image"
}
```

### GET /api/plates
Get all plates with pagination
- Query params: `page`, `limit`, `gateId`, `startDate`, `endDate`

### GET /api/plates/search/:plateNumber
Search specific plate

### PUT /api/plates/:id
Update plate (manual correction)

### DELETE /api/plates/:id
Delete plate record

## Development Tips

### Testing with iPhone Camera

1. Ensure iPhone and computer are on same WiFi
2. Use DroidCam's IP address
3. Test video stream: `http://IPHONE_IP:4747/video`
4. Adjust camera angle for optimal plate capture

### Improving Detection Accuracy

- Ensure good lighting conditions
- Position camera 2-3 meters from vehicles
- Adjust YOLO confidence threshold
- Train custom model with local plate samples
- Consider using Plate Recognizer API for better accuracy

### Performance Optimization

- Process every 3rd frame to reduce CPU usage
- Use GPU acceleration if available
- Implement frame skipping during duplicate window
- Cache recent detections in memory

## Docker Deployment

```bash
docker-compose up -d
```

This starts:
- MongoDB container
- Backend API container
- Frontend container
- Python service container

## Troubleshooting

### Camera Connection Issues
- Verify iPhone app is running
- Check firewall settings
- Ensure devices are on same network

### OCR Accuracy Problems
- Install language packs: `apt-get install tesseract-ocr-eng`
- Consider Plate Recognizer API as alternative
- Retrain YOLO model with local samples

### Performance Issues
- Reduce video resolution
- Increase frame skip interval
- Enable GPU support for YOLO

## Future Enhancements

- [ ] Multiple camera support
- [ ] Real-time notifications (WebSocket)
- [ ] Vehicle type classification
- [ ] Access control integration
- [ ] Mobile app for guards
- [ ] Analytics and reporting
- [ ] Cloud backup
- [ ] License plate whitelist/blacklist

## License

MIT License

## Support

For issues or questions, please create an issue in the repository.
