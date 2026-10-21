# Digital DNA

**Continuous Multimodal Behavioral Biometric Authentication System**

Digital DNA is an on-device, continuous authentication engine that establishes and verifies a user's unique behavioral signature in real time. Rather than relying solely on point-in-time perimeter authentication (passwords, PINs, or 2FA at login), Digital DNA continuously validates identity throughout an active session by analyzing micro-patterns in human-computer interaction.

---

## System Architecture

The architecture operates as an asynchronous, multi-stage processing pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEMETRY COLLECTORS                     │
│  - Keystroke Dynamics (Salted SHA-256 Key IDs, Flight/Dwell) │
│  - Mouse Kinematics (Trajectory, Velocity, Acceleration)    │
│  - System Application Context                               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FEATURE EXTRACTION PIPELINE                 │
│  - Keystroke (19 Temporal, Rhythmic & Entropy Features)     │
│  - Mouse (16 Kinematic, Curvature & Sub-movement Features)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               TRI-MODEL BIOMETRIC ENSEMBLES                 │
│  ┌───────────────────┬───────────────────┬────────────────┐ │
│  │  One-Class SVM    │    Mahalanobis    │  Deep PyTorch  │ │
│  │  (Support Vector) │   (Ledoit-Wolf)   │  Autoencoder   │ │
│  └───────────────────┴───────────────────┴────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            DYNAMIC SCORE FUSION & TRUST ENGINE              │
│  - Modality Confidence Weighting (Keystroke + Mouse)        │
│  - Exponential Moving Average (EMA) with Median Smoothing   │
│  - 3-State FSM Decision Engine (ALLOW / WARN / LOCK)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           CONTINUOUS LEARNING & DRIFT ADAPTATION            │
│  - Concept Drift Detector (Gradual Shift vs Impostor Attack)│
│  - Holdout Validation Gate (Promotion Threshold >= 0.68)   │
│  - Zero-Downtime Asynchronous Model Retraining              │
└─────────────────────────────────────────────────────────────┘
```

---

## Machine Learning Models & Ensemble Architecture

For each biometric modality, Digital DNA deploys a heterogeneous three-model ensemble. This multi-perspective design eliminates single-model blind spots, combining geometric boundary separation, statistical distance modeling, and non-linear manifold reconstruction.

### 1. One-Class Support Vector Machine (OCSVM)
- **Role:** High-dimensional non-linear boundary estimation.
- **Kernel:** Radial Basis Function (`rbf`) with scaled gamma.
- **Formulation:** Computes a maximal separation hyperplane bounding the genuine user's feature distribution while rejecting anomalous outliers.
- **Score Calibration:** Raw hyperplane distances are converted into normalized `[0, 1]` similarity scores via an empirical Z-score sigmoid transformation with dynamic scaling and saturation bounds `[-10, 10]`.

### 2. Regularized Mahalanobis Distance Model
- **Role:** Parametric multivariate correlation modeling.
- **Estimator:** Uses **Ledoit-Wolf shrinkage** covariance estimation to compute well-conditioned, invertible covariance matrices even with limited sample sizes.
- **Metric:** Computes statistical distance while accounting for cross-feature correlations:
  $$D_M(x) = \sqrt{(x - \mu)^T \Sigma^{-1} (x - \mu)}$$
- **Calibration:** Distances are inverted and calibrated using baseline mean and standard deviation:
  $$z = \frac{\mu_{\text{train}} - D_M(x)}{\sigma_{\text{train}}}$$
  mapped through a shifted sigmoid function to output calibrated genuine probability.

### 3. Deep PyTorch Reconstruction Autoencoder
- **Role:** Non-linear compression and manifold reconstruction.
- **Network Architecture:**
  - **Encoder:** Fully connected bottleneck (`input_dim` $\rightarrow 32 \rightarrow 16 \rightarrow 8$) with LeakyReLU activations.
  - **Decoder:** Symmetric expansion ($8 \rightarrow 16 \rightarrow 32 \rightarrow$ `input_dim`).
- **Objective:** Trained solely on genuine user samples using Mean Squared Error (MSE) loss with Adam optimizer.
- **Inference:** When anomalous or impostor patterns enter the network, reconstruction error spikes significantly:
  $$\text{Loss}_{\text{rec}} = \frac{1}{D} \sum_{i=1}^D (x_i - \hat{x}_i)^2$$
  Reconstruction loss is inverted into a similarity metric using training distribution statistics.

### 4. Ensemble Scorer Fusion
Predictions from all three models are fused via weighted consensus:
$$\text{Score}_{\text{modality}} = w_{\text{svm}} S_{\text{svm}} + w_{\text{mah}} S_{\text{mah}} + w_{\text{ae}} S_{\text{ae}}$$
*(Default weights: 0.40 OCSVM, 0.35 Mahalanobis, 0.25 Autoencoder)*

---

## Feature Engineering Pipeline

Telemetry events are aggregated into sliding time windows (default 30-second duration with a 5-second slide step).

### Keystroke Dynamics (19 Features)
- **Temporal & Duration:** Mean dwell time, standard deviation of dwell time, median dwell time, interquartile range (IQR) of dwell time.
- **Flight & Transition:** Mean flight time, standard deviation of flight time, median flight time, IQR of flight time.
- **Typing Rhythm & Speed:** Characters per minute (CPM), words per minute (WPM), typing rhythm regularities.
- **Error & Editing Behavior:** Backspace-to-keystroke ratio, error burst frequencies.
- **Distribution Shape & Entropy:** Shannon entropy of key transition intervals (`scipy.stats.entropy`), dwell time skewness, dwell time kurtosis.
- **Burst Dynamics:** Mean inter-burst gap durations, average strokes per burst.

### Mouse Kinematics (16 Features)
- **Velocity Profile:** Mean speed, standard deviation of speed, maximum speed, median speed.
- **Acceleration & Force:** Mean acceleration, standard deviation of acceleration, jerk (rate of change of acceleration).
- **Trajectory Geometry:** Path straightness ratio (Euclidean distance over total arc length), path efficiency, trajectory curvature.
- **Kinematic Dynamics:** Angular velocity changes, movement pause ratio, sub-movement counts (inflection points in velocity).
- **Click & Interaction:** Click hold duration mean and variance, double-click cadence.

---

## Fusion & Trust Engine

### Modality Score Fusion
Modality scores are fused dynamically according to event density and activity confidence:
$$\text{Fused Similarity} = \frac{\sum_{m} w_m \cdot S_m}{\sum_{m} w_m}$$
If a user is typing without moving the mouse (or vice versa), weights adjust dynamically so idle modalities do not penalize the active interaction.

### Exponential Moving Average (EMA) with Median Smoothing
To prevent false-positive alarms from momentary distractions, coughing, or single-character errors:
1. Instant similarity scores are recorded in a rolling FIFO buffer.
2. A 5-window moving median filter removes transient spike noise.
3. The smoothed score updates the continuous Trust Score ($0.0 - 100.0$) using Exponential Moving Average:
   $$\text{Trust}_t = \alpha \cdot \text{Score}_{\text{median}} + (1 - \alpha) \cdot \text{Trust}_{t-1}$$
   *(Default $\alpha = 0.35$)*
4. During user inactivity (idle), the score decays gradually toward neutral ($50.0$) without artificially preserving stale states.

### Finite State Machine Decision Engine
The session state is evaluated against configurable risk boundaries:
- **`ALLOW` (Trust $\ge 75$):** User verified as genuine. Consecutive violation counter decrements.
- **`WARN` ($50 \le \text{Trust} < 75$):** Identity confidence degraded. Passive logging and visual alerts triggered.
- **`LOCK` (Trust $< 50$):** Impostor behavior identified. If confidence remains below threshold for $N$ consecutive windows (default 3 consecutive cycles $\approx 15$ seconds), an automated security lock is dispatched.

---

## Continuous Learning & Concept Drift Architecture

Human behavior evolves due to fatigue, task switching, time of day, and posture. Digital DNA implements a continuous self-tuning cycle to maintain accuracy over weeks and months.

```
       [Live Session Stream]
                 │
                 ▼
     [Trust >= 75 && Genuine?]
          /              \
        (No)             (Yes)
         │                 │
     [Discard]             ▼
                 [Accumulate Samples]
                           │
                           ▼
               [Concept Drift Detector]
              (Gradual Drift vs Impostor)
                           │
                           ▼
             [Background Retrain Trigger]
                           │
                           ▼
            [Holdout Validation Gate]
            (Mean Accuracy >= 0.68?)
                 /           \
               (No)          (Yes)
                │              │
            [Reject]           ▼
                     [Atomic Model Swap]
                     [Save Versioned Checkpoint]
```

1. **Selective Accumulation:** Only windows verified with high confidence (`ALLOW` state, trust $\ge 75$) are buffered.
2. **Concept Drift Detection:** Tracks split-window score trajectories to differentiate natural performance drift from sudden impostor intrusions.
3. **Holdout Validation Gate:** Candidate retrained models must pass a validation check against historical holdout data (minimum accuracy threshold $\ge 0.68$). Defective or corrupted retrains are automatically rejected.
4. **Asynchronous Execution:** Model fitting runs in a dedicated background worker thread, ensuring real-time monitoring and GUI responsiveness remain unaffected.

---

## Security & Anti-Tamper Hardening

- **Cryptographic Model Signing:** Machine learning checkpoints (`.joblib`) are signed using HMAC-SHA256 upon export. Every model load validates cryptographic integrity against tampering to mitigate arbitrary code execution risks.
- **Path Traversal Defenses:** Strict regex sanitization (`^[a-zA-Z0-9_\-]{1,64}$`) is enforced across profile management and raw event stores to prevent directory traversal exploits.
- **Salted Key Privacy:** Keypress events are anonymized using dynamic SHA-256 hashing combined with unique cryptographic salts (`secrets.token_hex(16)`). Plaintext key values are never stored or logged.
- **Complete Profile Purging:** Comprehensive session reset mechanisms permanently sanitize all raw telemetry, metadata, and trained weight artifacts on demand.

---

## Privacy & Ethical Framework

- **Content Agnostic:** Digital DNA captures *how* a user types and moves, never *what* is typed or read.
- **Zero-Cloud Dependency:** The entire capture, feature extraction, training, and continuous verification pipeline executes entirely on the local machine.
- **Transparent Profiles:** User models and session logs are stored locally under transparent, readable structures.

---

## Technology Stack

- **Core Runtime:** Python 3.11+
- **Deep Learning Framework:** PyTorch (`torch.nn`)
- **Machine Learning & Covariance:** Scikit-Learn (`OneClassSVM`, `IsolationForest`, `LedoitWolf`, `StandardScaler`, `RobustScaler`)
- **Mathematical & Statistical Computing:** NumPy, SciPy (`scipy.stats.entropy`), Pandas
- **Serialization & Security:** Joblib, HMAC, SHA-256, Secrets
- **System & Input Telemetry:** Pynput, Psutil
- **Desktop Interface:** PySide6 / PyQt (QThread, Custom Widgets, Real-Time Charting)
