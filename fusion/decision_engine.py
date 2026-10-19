from typing import Dict, Any

class DecisionEngine:
    def __init__(self, threshold_allow: float = 75.0, threshold_warn: float = 50.0, max_consecutive_violations: int = 3):
        self.threshold_allow = threshold_allow
        self.threshold_warn = threshold_warn
        self.max_consecutive_violations = max_consecutive_violations
        self.consecutive_violations = 0

    def evaluate(self, trust_score: float) -> Dict[str, Any]:
        if trust_score >= self.threshold_allow:
            self.consecutive_violations = max(0, self.consecutive_violations - 1)
            decision = "ALLOW"
        elif trust_score >= self.threshold_warn:
            decision = "WARN"
        else:
            self.consecutive_violations += 1
            if self.consecutive_violations >= self.max_consecutive_violations:
                decision = "LOCK"
            else:
                decision = "WARN"

        return {
            "decision": decision,
            "trust_score": trust_score,
            "consecutive_violations": self.consecutive_violations,
            "threshold_allow": self.threshold_allow,
            "threshold_warn": self.threshold_warn
        }

    def reset(self):
        self.consecutive_violations = 0
