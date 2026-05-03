# Phase 5: The Interface
## Step 1 - API and Premium Flutter Blueprint
=============================================

## 🚀 The Flutter Setup Commands
To properly initialize the frontend application, we are using the following command suite. (Note: Ensure the Flutter SDK is installed and configured in your system PATH).

Navigate to `D:\NLP_MINI_Project\` and run:
```bash
flutter create query_voice_app
cd query_voice_app
flutter pub add http speech_to_text provider flutter_animate lottie glassmorphism google_fonts
```

## 🎨 UI/UX Animation Theory & "The Brain"
For the Phase 5 presentation to AI professors, the UI cannot simply be a generic CRUD interface. It must *feel* like a premium AI agent.

### Why `flutter_animate`?
We chose `flutter_animate` over pre-rendered Lottie files for the **Brain Flowchart Animation**. 
* **Dynamic Staggering:** It allows us to sequentially stagger the rendering of the `User -> Router -> RAG -> LLM -> Output` nodes using `.fadeIn().shimmer().scaleXY()`.
* **The "Pulse" Effect:** It enables us to animate the connecting lines mimicking real-time data flow, giving the illusion that the pipeline is "thinking" while waiting for the LLM response.
* **Latency Masking:** The 10-20 second local inference time is completely masked by this engaging flowchart.

### Premium Theming
We established a strict monochromatic tech-theme in `lib/main.dart`:
- **Matte Black Background:** `#121212` prevents eye strain and feels sleek.
- **Dark Grey Containers:** `#1E1E1E` creates subtle depth for cards and the Bottom Navigation Bar.
- **Deep Purple Primary:** Used to signify active AI processing.
- **Semantic Feedback:** Colors like Red (listening/errors) and Green (success) give instant visual feedback.

## 🌉 The FastAPI Bridge Connection (Networking & Endpoints)
The Flutter app connects to the Python Agentic RAG pipeline via a high-performance **FastAPI** server.

### 1. Network Bridging
To allow communication between the teammate's frontend device and the server machine, we transitioned from `localhost` to a local network broadcast:
- **Server Address:** `http://10.208.58.5:8000/api/v1`
- **CORS Configuration:** Fully enabled to allow cross-origin requests from mobile clients.

### 2. Audio Transmission logic
Unlike standard JSON APIs, voice queries require binary data transmission. We implemented a **Multipart/Form-Data** pipeline:
- **Field Name:** `audio`
- **Content Type:** `.wav`
- **Logic:** The mobile app captures raw PCM audio, wraps it in a `.wav` container, and streams it to the `/query/voice` endpoint.

### 3. API Response Schema
The server returns a unified JSON object that maps directly to the UI's `QueryResponse` model:
- `natural_language_query`: The transcript as heard by Whisper.
- `generated_sql`: The synthesized SQL for transparency.
- `results`: The raw data for the `ChartWidget`.
- `summary`: The final human-readable answer.

---

---
**Next Step:** Implement Voice-to-Text (`speech_to_text`) and connect real Database logic in the Dashboard.
