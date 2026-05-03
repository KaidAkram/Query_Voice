# QueryVoice — Flutter Frontend

The mobile client for QueryVoice. Provides a voice-first conversational interface for querying business databases and viewing interactive charts.

## Features

- 🎙️ Voice recording with real-time waveform visualization
- 💬 Chat-based query/response interface
- 📊 Dynamic chart rendering from SQL query results
- 🔗 REST API integration with FastAPI backend

## Getting Started

```bash
flutter pub get
flutter run
```

## Architecture

```
lib/
├── main.dart          # App entry point & routing
├── screens/           # Full-page UI screens
├── widgets/           # Reusable UI components
├── services/          # API client layer
└── models/            # Data transfer objects
```
