"""Leitura não bloqueante dos pacotes textuais enviados pela ECU via LoRa."""

from __future__ import annotations

import re
from datetime import datetime

from .modelo import Telemetria


PADRAO_PACOTE = re.compile(r"<([^<>]+)>")


def decodificar_pacote(texto: str) -> Telemetria:
    """Decodifica <vel,consumo,odo,rpm,nivel,tMotor,tCVT,tESP,tracao>."""
    encontrado = PADRAO_PACOTE.search(texto.strip())
    if not encontrado:
        raise ValueError("Pacote sem delimitadores < e >.")
    campos = [campo.strip() for campo in encontrado.group(1).split(",")]
    if len(campos) != 9:
        raise ValueError(f"Esperados 9 campos, recebidos {len(campos)}.")
    return Telemetria(
        velocidade=float(campos[0]),
        consumo_ml=float(campos[1]),
        odometro=float(campos[2]),
        rpm=int(float(campos[3])),
        combustivel_pct=float(campos[4]),
        temp_motor=float(campos[5]),
        temp_cvt=float(campos[6]),
        temp_esp=float(campos[7]),
        tracao_dianteira=int(float(campos[8])),
        timestamp=datetime.now(),
    )


class LeitorSerialLoRa:
    def __init__(self) -> None:
        self._serial = None
        self._porta = ""
        self._baud = 9_600
        self.ultimo_erro = ""

    @property
    def conectado(self) -> bool:
        return bool(self._serial and self._serial.is_open)

    def conectar(self, porta: str, baud: int = 9_600) -> None:
        import serial

        self.desconectar()
        self._serial = serial.Serial(port=porta, baudrate=baud, timeout=0)
        self._porta, self._baud = porta, baud
        self.ultimo_erro = ""

    def desconectar(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None

    def ler_mais_recente(self) -> Telemetria | None:
        if not self.conectado:
            return None
        mais_recente = None
        try:
            while self._serial.in_waiting:
                linha = self._serial.readline().decode("utf-8", errors="ignore")
                if linha.strip():
                    mais_recente = decodificar_pacote(linha)
            self.ultimo_erro = ""
        except (OSError, ValueError) as erro:
            self.ultimo_erro = str(erro)
        return mais_recente
