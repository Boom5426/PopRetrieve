"""Two-phase training schedule (BCE warmup -> BCE + InfoNCE) with cosine anneals."""
from __future__ import annotations

import math
from dataclasses import dataclass


def cosine_anneal(v0: float, v1: float, epoch: int, start: int, end: int) -> float:
    if epoch <= start:
        return v0
    if epoch >= end:
        return v1
    t = (epoch - start) / max(1, (end - start))
    return v1 + 0.5 * (v0 - v1) * (1 + math.cos(math.pi * t))


@dataclass
class PhaseState:
    phase: int
    temperature: float
    lambda_dt: float          # weight on BCE during Phase 2
    lambda_recon: float       # weight on recon during Phase 1
    use_infonce: bool


class PhaseScheduler:
    def __init__(self, phase1_epochs: int = 20,
                 temp0: float = 0.20, temp1: float = 0.10, temp_end: int = 120,
                 lam0: float = 50.0, lam1: float = 5.0, lam_end: int = 120,
                 lambda_recon: float = 0.1):
        self.p1 = phase1_epochs
        self.temp0, self.temp1, self.temp_end = temp0, temp1, temp_end
        self.lam0, self.lam1, self.lam_end = lam0, lam1, lam_end
        self.lambda_recon = lambda_recon

    def state(self, epoch: int) -> PhaseState:
        if epoch < self.p1:
            return PhaseState(1, self.temp0, 0.0, self.lambda_recon, use_infonce=False)
        temp = cosine_anneal(self.temp0, self.temp1, epoch, self.p1, self.temp_end)
        lam = cosine_anneal(self.lam0, self.lam1, epoch, self.p1, self.lam_end)
        return PhaseState(2, temp, lam, 0.0, use_infonce=True)
