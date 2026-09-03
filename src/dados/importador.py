"""Única porta de entrada de telemetria para toda a interface."""

from __future__ import annotations

import time
from dataclasses import replace

from src.config.metricas import METRICAS

from .modelo import DadoExibicao, PacoteInterface, Telemetria
from .serial_lora import LeitorSerialLoRa
from .simulador import SimuladorECU


class ImportadorDados:
    """Seleciona a fonte, normaliza valores e aplica as métricas dos LEDs."""

    def __init__(self) -> None:
        self.fonte = "Simulado"
        self.simulador = SimuladorECU()
        self.serial = LeitorSerialLoRa()
        self._ultima_telemetria = Telemetria()
        self._ultima_serial = Telemetria()
        self._serial_recebeu_dados = False
        self._base_consumo_serial = 0.0
        self._base_tanque_serial: float | None = None
        self._base_odometro_kml = {"Simulado": 0.0, "Serial": 0.0}
        self._ultimo_instante = time.monotonic()

    def selecionar_fonte(self, fonte: str) -> None:
        if fonte not in {"Serial", "Simulado"}:
            raise ValueError("A fonte deve ser Serial ou Simulado.")
        if fonte == self.fonte:
            return
        self.fonte = fonte
        if fonte == "Serial":
            # Uma nova sessão real começa vazia e só exibe dados efetivamente lidos.
            self._serial_recebeu_dados = False
            self._base_consumo_serial = 0.0
            self._base_tanque_serial = None
            self._base_odometro_kml["Serial"] = 0.0
        self._ultimo_instante = time.monotonic()

    def encher_tanque(self) -> bool:
        if self.fonte == "Simulado":
            self.simulador.encher_tanque()
            return True
        if not self._serial_recebeu_dados:
            return False
        # O rádio da ECU é somente transmissor. A leitura atual vira a
        # referência local de um tanque cheio para esta sessão.
        self._base_tanque_serial = self._ultima_serial.consumo_ml
        return True

    def resetar_consumo(self) -> bool:
        if self.fonte == "Simulado":
            self.simulador.resetar_consumo()
            self._base_odometro_kml["Simulado"] = self.simulador.odometro
            return True
        if not self._serial_recebeu_dados:
            return False
        self._base_consumo_serial = self._ultima_serial.consumo_ml
        self._base_odometro_kml["Serial"] = self._ultima_serial.odometro
        return True

    @staticmethod
    def _classificar(valor: float | int, metrica: dict) -> str:
        modo = metrica["modo"]
        if modo == "informativo":
            return "verde"
        amarelo = metrica["limite_amarelo"]
        vermelho = metrica["limite_vermelho"]
        if modo == "maximo":
            return "vermelho" if valor >= vermelho else "amarelo" if valor >= amarelo else "verde"
        if modo == "minimo":
            return "vermelho" if valor <= vermelho else "amarelo" if valor <= amarelo else "verde"
        return "sem_dados"

    def _preparar(
        self,
        telemetria: Telemetria,
        conectado: bool,
        recebido: bool,
        mensagem: str,
    ) -> PacoteInterface:
        # Eficiência média acumulada desde o início da sessão. A ECU informa
        # consumo em mililitros, por isso a conversão para litros.
        distancia_consumo = max(
            0.0,
            telemetria.odometro - self._base_odometro_kml[self.fonte],
        )
        telemetria.consumo_kml = (
            distancia_consumo / (telemetria.consumo_ml / 1_000.0)
            if recebido and telemetria.consumo_ml > 0
            else None
        )
        valores = telemetria.como_dict()
        dados = {}
        for chave, metrica in METRICAS.items():
            valor = valores[chave] if recebido else None
            dados[chave] = DadoExibicao(
                chave=chave,
                rotulo=metrica["rotulo"],
                valor=valor,
                unidade=metrica["unidade"],
                estado=self._classificar(valor, metrica) if recebido and valor is not None else "sem_dados",
            )
        return PacoteInterface(telemetria, dados, self.fonte, conectado, recebido, mensagem)

    def ler(self) -> PacoteInterface:
        agora = time.monotonic()
        dt = agora - self._ultimo_instante
        self._ultimo_instante = agora

        if self.fonte == "Simulado":
            self._ultima_telemetria = self.simulador.atualizar(dt)
            estado = "Carro ligado" if self.simulador.ligado else "Carro desligado"
            return self._preparar(self._ultima_telemetria, True, True, estado)

        nova = self.serial.ler_mais_recente()
        if nova is not None:
            self._ultima_serial = nova
            self._serial_recebeu_dados = True
        mensagem = self.serial.ultimo_erro or (
            "Recebendo dados da ECU"
            if self._serial_recebeu_dados
            else "Serial conectada; aguardando o primeiro pacote"
            if self.serial.conectado
            else "Serial desconectada"
        )
        serial_exibida = replace(self._ultima_serial)
        serial_exibida.consumo_ml = max(
            0.0,
            self._ultima_serial.consumo_ml - self._base_consumo_serial,
        )
        if self._base_tanque_serial is not None:
            consumo_desde_abastecimento = max(
                0.0,
                self._ultima_serial.consumo_ml - self._base_tanque_serial,
            )
            serial_exibida.combustivel_pct = max(
                0.0,
                100.0 - consumo_desde_abastecimento / 5_670.0 * 100.0,
            )
        return self._preparar(
            serial_exibida,
            self.serial.conectado and not bool(self.serial.ultimo_erro),
            self._serial_recebeu_dados,
            mensagem,
        )
