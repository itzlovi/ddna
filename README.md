# Digital DNA

**Continuous Multimodal Behavioral Biometrics for Continuous Authentication**

Digital DNA is an open-source continuous authentication system that builds a unique behavioral profile of a user by analyzing how they interact with their device. It continuously monitors multiple behavioral signals, fuses them into a single "Digital DNA" trust score, and can detect when another person tries to use the system.

---

## Vision

Traditional authentication only checks identity at login. After that, the system trusts the session forever.

Digital DNA flips this model:

> Continuously verify that the person currently using the device is still the same person who logged in — by analyzing their unique behavioral patterns.

If the behavioral signature drifts significantly (for example, someone else sits down at the computer), the system can lock the device or trigger step-up authentication.

---

## Key Features

- **Multimodal Behavioral Biometrics**
  - Keystroke dynamics (dwell time, flight time, rhythm, typing speed)
  - Mouse / pointer dynamics (trajectory, speed, acceleration, click patterns)
  - App usage patterns
  - Touch dynamics (mobile)
  - Gait / device motion (mobile sensors)

- **Continuous Authentication**
  - Sliding window analysis
  - Real-time Digital DNA Trust Score (0–100)
  - Automatic lock or warning when an impostor is detected

- **Privacy-First Design**
  - Never stores the actual content of what is typed
  - Only timing and behavioral features are collected
  - Local processing preferred

- **Zero-Cost Stack**
  - Built entirely with free and open-source tools

---

## High-Level Architecture

```
┌─────────────────────┐
│  Data Collectors    │  (Desktop / Mobile)
│  - Keystroke        │
│  - Mouse / Touch    │
│  - Motion / Gait    │
│  - App Usage        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Feature Extraction  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Individual Models   │  (One model per modality)
│  - Keystroke Model  │
│  - Mouse Model      │
│  - Motion Model     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   Fusion Engine     │  → Digital DNA Trust Score
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Decision Engine    │
│  Allow / Warn / Lock│
└─────────────────────┘
```

---

## Project Structure

```
digital-dna/
├── collectors/
│   ├── desktop/          # Keystroke + Mouse collectors
│   └── mobile/           # Touch + Motion collectors (future)
├── features/             # Feature extraction logic
├── models/               # Trained models per modality
├── fusion/               # Score fusion → Digital DNA
├── core/                 # Auth engine & continuous loop
├── data/                 # Local data storage (gitignored)
├── notebooks/            # Experimentation & analysis
├── docs/                 # Documentation
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Component              | Technology                          |
|------------------------|-------------------------------------|
| Language               | Python 3.11+                        |
| Desktop Collection     | pynput, psutil                      |
| Machine Learning       | scikit-learn, joblib                |
| Deep Learning (later)  | TensorFlow / PyTorch (optional)     |
| GUI (MVP)              | CustomTkinter / PyQt                |
| Mobile (Phase 2)       | Flutter                             |
| Version Control        | GitHub                              |
| Experiment Tracking    | Google Colab                        |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/digital-dna.git
cd digital-dna
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# or
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the desktop collector (example)

```bash
python collectors/desktop/main_collector.py
```

The collector runs in the background and saves behavioral features locally.  
No key content is ever stored — only timing information.

---

## Development Roadmap

| Phase | Focus                                   | Status      |
|-------|-----------------------------------------|-------------|
| 1     | Desktop keystroke + mouse collector     | In Progress |
| 2     | Feature extraction + individual models  | Planned    |
| 3     | Fusion engine (Digital DNA Score)       | Planned    |
| 4     | Continuous authentication loop          | Planned    |
| 5     | Simple desktop MVP + lock feature       | Planned    |
| 6     | Android collector + gait                | Future     |
| 7     | Cross-device Digital DNA                | Future     |

---

## Privacy & Ethics

- We only collect behavioral timing and movement patterns.
- We never store the actual characters typed by the user.
- All processing can run fully on-device.
- Users must explicitly enroll and can delete their profile at any time.

---

## Team

This project is currently in its initial stage.  
Shieldove is actively working on Digital DNA.

---

## License

This project is released under the MIT License.  
See the LICENSE file for details.

---

## Acknowledgements

Inspired by research in continuous behavioral biometrics (keystroke dynamics, mouse dynamics, multimodal fusion) and systems such as M2auth, TypingDNA, and academic work on continuous authentication.

---

**Status:** Early development – MVP focused on desktop continuous authentication using keystroke + mouse dynamics.
