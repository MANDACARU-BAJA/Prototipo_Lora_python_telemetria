"""Modelos normalizados compartilhados pelas fontes e pela interface."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Telemetria:
    velocidade: float = 0.0
    consumo_ml: float = 0.0
    consumo_kml: float | None = None
    odometro: float = 0.0
    rpm: int = 0
    combustivel_pct: float = 100.0
    temp_motor: float = 25.0
    temp_cvt: float = 25.0
    temp_esp: float = 35.0
    tracao_dianteira: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def como_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class DadoExibicao:
    chave: str
    rotulo: str
    valor: float | int | None
    unidade: str
    estado: str


@dataclass(slots=True)
class PacoteInterface:
    telemetria: Telemetria
    dados: dict[str, DadoExibicao]
    fonte: str
    conectado: bool
    recebido: bool
    mensagem: str
