# Digital DNA Roadmap

| Phase | Milestone | Scope | Status |
|-------|-----------|-------|--------|
| Phase 1 | Foundation & Project Setup | Repo structure, environment dependencies, config dataclasses | Completed |
| Phase 2 | Desktop Collectors | Real-time keystroke, mouse, and app usage event capture | Completed |
| Phase 3 | Feature Extraction | 19 keystroke dimensions, 16 mouse dimensions, mobile sensor features | Completed |
| Phase 4 | Modality Models | One-Class SVM (keystroke) & Isolation Forest (mouse) with joblib | Completed |
| Phase 5 | Fusion Layer | Adaptive weighted score fusion + EMA smoothing -> Trust Score (0-100) | Completed |
| Phase 6 | Continuous Auth Engine | Background sliding-window loop with ALLOW / WARN / LOCK decisions | Completed |
| Phase 7 | Desktop Application | PyQt6 GUI with live telemetry gauge, enrollment tab, settings, and tray | Completed |
| Phase 8 | Performance & Benchmarking | FAR, FRR, and Equal Error Rate (EER) evaluation pipeline | Completed |
| Phase 9 | Mobile Expansion | Sensor ingestion for gait, motion, and touch biometrics | Framework Ready |
