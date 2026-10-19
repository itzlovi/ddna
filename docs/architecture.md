# Digital DNA Architecture

## System Overview

Digital DNA is an on-device continuous behavioral biometric authentication system. It continuously captures user interaction patterns across multiple modalities (Keystroke Dynamics, Mouse Dynamics, App Usage, and Mobile Motion/Touch), extracts time-domain and frequency-domain behavioral features, evaluates similarity using one-class anomaly detection models, and fuses scores into an on-device Trust Score (0–100).

```
+-------------------------------------------------------------+
|                      Data Collectors                        |
|  - KeystrokeCollector (Dwell, Flight, Rhythm)               |
|  - MouseCollector (Speed, Acceleration, Curvature, Jerk)    |
|  - AppUsageCollector (Context & Process Switches)           |
|  - MotionCollector & TouchCollector (Mobile Extension)      |
+------------------------------+------------------------------+
                               | Raw Events
                               v
+-------------------------------------------------------------+
|                      Feature Pipeline                       |
|  - Statistical Moments (Mean, Std, Median, IQR)             |
|  - N-graph Interval Analysis (Digraphs, Trigraphs)          |
|  - Trajectory Kinematics (Curvature, Jerk, Entropy)         |
+------------------------------+------------------------------+
                               | Feature Vectors
                               v
+-------------------------------------------------------------+
|                     Modality Models                         |
|  - KeystrokeModel (One-Class SVM with RBF Kernel)           |
|  - MouseModel (Isolation Forest with Robust Scaler)         |
|  - MotionModel & TouchModel (Sensor Baseline)               |
+------------------------------+------------------------------+
                               | Similarity Scores [0.0 - 1.0]
                               v
+-------------------------------------------------------------+
|                       Fusion Engine                         |
|  - Weighted Multi-Modality Score Fusion                     |
|  - Exponential Moving Average (EMA) Smoothing               |
|  - Trust Score Calculation (0 - 100)                        |
+------------------------------+------------------------------+
                               | Trust Score
                               v
+-------------------------------------------------------------+
|                      Decision Engine                        |
|  - Score >= 75: ALLOW (Authenticated)                       |
|  - Score 50-74: WARN (Suspicious / Warning)                 |
|  - Score < 50 (consecutive): LOCK (Auto Workstation Lock)   |
+-------------------------------------------------------------+
```
