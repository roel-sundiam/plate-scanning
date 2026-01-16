## License Plate Scanning AI Prompt

I want to build a license plate scanning system for a guard house gate. The system should:

1. Capture video from a camera:

   - Currently, I will use an iPhone as a temporary camera.
   - Later, I will use a proper RTSP-enabled IP camera.

2. Detect vehicles passing the gate and automatically recognize their license plate numbers.
3. Save plate numbers to a database (MongoDB) with:

   - Plate number
   - Timestamp
   - Camera/gate identifier
   - Optional: snapshot image

4. Provide a backend API using Node.js (Express) to handle data storage, duplicate filtering, and retrieval.
5. Provide a frontend dashboard using Angular to:

   - Show live captured plates
   - Search plate numbers
   - Display snapshots
   - Allow manual correction if OCR fails

6. Handle duplicate entries (ignore same plate if detected within a short time window)
7. Start with a development version using the iPhone camera, then switch to RTSP camera when available.
8. Support optional integration with a plate recognition API (like Plate Recognizer) or local OCR (YOLO + Tesseract).
9. Be modular so the video input source can be changed easily without rewriting the whole system.

Please provide:

- Suggested technology stack
- Architecture diagram
- Sample code for capturing video from the camera, performing OCR, sending results to the API, and storing in MongoDB
- Angular dashboard mockup or structure
- Tips for development and testing with the iPhone camera before switching to RTSP

**Optional (for working code):**
Please provide working Python code for reading the camera stream, detecting license plates using OCR, and sending the results to the Node.js API. Include example MongoDB schema and Angular frontend code for displaying the results.

---

_This file is saved as a Markdown file: `license_plate_ai_prompt.md`. You can download it from the workspace or copy its content to create a local `.md` file._
