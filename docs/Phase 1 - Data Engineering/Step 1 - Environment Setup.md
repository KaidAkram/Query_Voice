# Phase 1, Step 1 — Environment Configuration
==========================================

## Overview
This document covers the foundational environment setup for the QueryVoice project. Proper environment configuration ensures credentials are never hardcoded and secrets remain out of version control.

## 🎓 Teaching: Why Environment Variables?
Environment variables are **key-value pairs** that live *outside* your code. This prevents accidental exposure of sensitive data (like database passwords) when pushing to Git.

## 📂 Configuration
We created a centralized `.env` file at the project root:
```env
POSTGRES_USER=queryvoice_admin
POSTGRES_PASSWORD=supersecurepassword123
POSTGRES_DB=queryvoice_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## 🔒 Security Measures
- **.gitignore:** The `.env` file is explicitly excluded to prevent accidental commits.
- **D: Drive Isolation:** Redirected HuggingFace cache and virtual environment to the D: drive (`$env:HF_HOME = "D:/huggingface_cache"`) to prevent C: drive exhaustion.
- **Encoding:** Set `$env:PYTHONUTF8 = "1"` to ensure consistent character handling across Windows environments.
