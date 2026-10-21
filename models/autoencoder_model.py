from typing import Union, List, Optional

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler

from .model_utils import save_model, load_model, inverted_calibrated_score


class _AutoencoderNet(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 8):
        super().__init__()
        hidden_1 = max(16, input_dim)
        hidden_2 = max(8, hidden_1 // 2)

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_1),
            nn.BatchNorm1d(hidden_1),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_1, hidden_2),
            nn.BatchNorm1d(hidden_2),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_2, latent_dim),
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_2),
            nn.BatchNorm1d(hidden_2),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_2, hidden_1),
            nn.BatchNorm1d(hidden_1),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_1, input_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))


class AutoencoderModel:
    """Reconstruction-error anomaly detector using a symmetric autoencoder."""

    def __init__(self, latent_dim: int = 8, epochs: int = 60, lr: float = 0.008):
        self.latent_dim = latent_dim
        self.epochs = epochs
        self.lr = lr
        self.scaler = StandardScaler()
        self.input_dim: Optional[int] = None
        self.net: Optional[_AutoencoderNet] = None
        self.is_fitted = False
        self.train_mean: float = 0.0
        self.train_std: float = 1.0

    def fit(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> "AutoencoderModel":
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        n_samples, self.input_dim = arr.shape
        X_scaled = self.scaler.fit_transform(arr).astype(np.float32)

        self.net = _AutoencoderNet(input_dim=self.input_dim, latent_dim=self.latent_dim)
        self.net.train()

        tensor_x = torch.from_numpy(X_scaled)
        dataset = torch.utils.data.TensorDataset(tensor_x)
        batch_size = min(16, max(4, n_samples // 4))
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=False)

        optimizer = torch.optim.Adam(self.net.parameters(), lr=self.lr, weight_decay=1e-4)
        criterion = nn.MSELoss()

        for _ in range(self.epochs):
            for (batch_x,) in loader:
                if len(batch_x) < 2:
                    continue
                optimizer.zero_grad()
                loss = criterion(self.net(batch_x), batch_x)
                loss.backward()
                optimizer.step()

        self.net.eval()
        with torch.no_grad():
            recon = self.net(tensor_x)
            errors = torch.mean((tensor_x - recon) ** 2, dim=-1).cpu().numpy()

        self.train_mean = float(np.mean(errors))
        self.train_std = max(float(np.std(errors)), 1e-4)
        self.is_fitted = True
        return self

    def _reconstruction_error(self, X_scaled: np.ndarray) -> np.ndarray:
        if self.net is None:
            return np.zeros(len(X_scaled))
        self.net.eval()
        with torch.no_grad():
            tensor_x = torch.from_numpy(X_scaled.astype(np.float32))
            recon = self.net(tensor_x)
            return torch.mean((tensor_x - recon) ** 2, dim=-1).cpu().numpy()

    def score(self, X: Union[np.ndarray, pd.DataFrame, List[float], List[List[float]]]) -> float:
        """0-1 similarity. Lower reconstruction error → higher score."""
        if not self.is_fitted or self.net is None:
            return 0.5
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        X_scaled = self.scaler.transform(arr)
        errors = self._reconstruction_error(X_scaled)
        sim = inverted_calibrated_score(errors, self.train_mean, self.train_std)
        return float(np.mean(sim))

    def predict(self, X: Union[np.ndarray, pd.DataFrame, List[List[float]]]) -> np.ndarray:
        if not self.is_fitted:
            return np.array([1])
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        X_scaled = self.scaler.transform(arr)
        errors = self._reconstruction_error(X_scaled)
        thresh = self.train_mean + 2.0 * self.train_std
        return np.where(errors <= thresh, 1, -1)

    def save(self, filepath: str):
        save_model(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "AutoencoderModel":
        return load_model(filepath)
