"""Modelo simples do veículo controlado por ignição e acelerador."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .modelo import Telemetria


@dataclass
class SimuladorECU:
    ligado: bool = False
    acelerador_pct: float = 0.0
    rpm: float = 0.0
    velocidade: float = 0.0
    consumo_ml: float = 0.0
    odometro: float = 0.0
    tanque_ml: float = 5_670.0
    temp_motor: float = 25.0
    temp_cvt: float = 25.0
    temp_esp: float = 35.0

    CAPACIDADE_TANQUE_ML = 5_670.0
    PULSOS_PARA_TANQUE_CHEIO = 945_302.4
    ML_POR_REVOLUCAO = CAPACIDADE_TANQUE_ML / PULSOS_PARA_TANQUE_CHEIO
    TEMPERATURA_AMBIENTE = 25.0

    def ligar(self) -> None:
        self.ligado = True

    def desligar(self) -> None:
        self.ligado = False
        self.acelerador_pct = 0.0

    def definir_acelerador(self, percentual: float) -> None:
        self.acelerador_pct = max(0.0, min(100.0, percentual)) if self.ligado else 0.0

    def encher_tanque(self) -> None:
        """Reabastece sem alterar o consumo acumulado da sessão."""
        self.tanque_ml = self.CAPACIDADE_TANQUE_ML

    def resetar_consumo(self) -> None:
        """Zera somente o contador de combustível consumido."""
        self.consumo_ml = 0.0

    @staticmethod
    def _aproximar(atual: float, alvo: float, rapidez: float, dt: float) -> float:
        fator = min(1.0, max(0.0, rapidez * dt))
        return atual + (alvo - atual) * fator

    def atualizar(self, dt: float) -> Telemetria:
        dt = max(0.0, min(dt, 2.0))
        alvo_rpm = (1_450.0 + self.acelerador_pct * 45.0) if self.ligado else 0.0
        self.rpm = self._aproximar(self.rpm, alvo_rpm, 2.3, dt)

        # A embreagem centrífuga começa a transmitir movimento acima da marcha lenta.
        alvo_velocidade = max(0.0, (self.rpm - 1_650.0) / 58.0) if self.ligado else 0.0
        self.velocidade = self._aproximar(self.velocidade, alvo_velocidade, 0.75, dt)
        if not self.ligado and self.velocidade < 0.08:
            self.velocidade = 0.0

        self.odometro += self.velocidade * dt / 3_600.0

        if self.ligado and self.tanque_ml > 0:
            # Mesma calibração usada pela ECU: após dividir as duas bordas do
            # sinal, cada pulso real corresponde a uma revolução do motor.
            vazao_ml_s = (self.rpm / 60.0) * self.ML_POR_REVOLUCAO
            consumido = min(self.tanque_ml, vazao_ml_s * dt)
            self.tanque_ml -= consumido
            self.consumo_ml += consumido
        elif self.tanque_ml <= 0:
            self.desligar()

        carga = self.acelerador_pct / 100.0 if self.ligado else 0.0
        alvo_motor = 42.0 + 72.0 * carga if self.ligado else self.TEMPERATURA_AMBIENTE
        alvo_cvt = 36.0 + 64.0 * carga if self.ligado else self.TEMPERATURA_AMBIENTE
        alvo_esp = 44.0 + 18.0 * carga if self.ligado else 34.0
        self.temp_motor = self._aproximar(self.temp_motor, alvo_motor, 0.018, dt)
        self.temp_cvt = self._aproximar(self.temp_cvt, alvo_cvt, 0.022, dt)
        self.temp_esp = self._aproximar(self.temp_esp, alvo_esp, 0.035, dt)

        return Telemetria(
            velocidade=self.velocidade,
            consumo_ml=self.consumo_ml,
            odometro=self.odometro,
            rpm=round(self.rpm),
            combustivel_pct=max(0.0, self.tanque_ml / self.CAPACIDADE_TANQUE_ML * 100.0),
            temp_motor=self.temp_motor,
            temp_cvt=self.temp_cvt,
            temp_esp=self.temp_esp,
            tracao_dianteira=0,
            timestamp=datetime.now(),
        )

    def reiniciar(self) -> None:
        estado_novo = type(self)()
        self.__dict__.update(estado_novo.__dict__)
