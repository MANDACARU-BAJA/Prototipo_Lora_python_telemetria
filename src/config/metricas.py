"""Limites usados para classificar cada dado antes de chegar à interface.

Este é o ponto central para calibrar os LEDs. A interface não decide cores:
ela recebe o estado já calculado pelo ImportadorDados.

Modos disponíveis:
- ``maximo``: valores baixos são melhores (temperaturas e RPM).
- ``minimo``: valores altos são melhores (nível de combustível).
- ``informativo``: não representa falha e permanece verde.
"""

METRICAS = {
    "velocidade": {
        "rotulo": "VELOCIDADE",
        "unidade": "km/h",
        "modo": "informativo",
    },
    "consumo_ml": {
        "rotulo": "COMBUSTÍVEL CONSUMIDO",
        "unidade": "mL",
        "modo": "informativo",
    },
    "consumo_kml": {
        "rotulo": "CONSUMO MÉDIO",
        "unidade": "km/L",
        "modo": "informativo",
    },
    "odometro": {
        "rotulo": "DISTÂNCIA",
        "unidade": "km",
        "modo": "informativo",
    },
    "rpm": {
        "rotulo": "ROTAÇÃO DO MOTOR",
        "unidade": "RPM",
        "modo": "maximo",
        "limite_amarelo": 4_000,
        "limite_vermelho": 5_000,
    },
    "combustivel_pct": {
        "rotulo": "NÍVEL DE COMBUSTÍVEL",
        "unidade": "%",
        "modo": "minimo",
        "limite_amarelo": 30,
        "limite_vermelho": 15,
    },
    "temp_motor": {
        "rotulo": "TEMPERATURA DO MOTOR",
        "unidade": "°C",
        "modo": "maximo",
        "limite_amarelo": 90,
        "limite_vermelho": 105,
    },
    "temp_cvt": {
        "rotulo": "TEMPERATURA DA CVT",
        "unidade": "°C",
        "modo": "maximo",
        "limite_amarelo": 80,
        "limite_vermelho": 95,
    },
    "temp_esp": {
        "rotulo": "TEMPERATURA DO ESP32",
        "unidade": "°C",
        "modo": "maximo",
        "limite_amarelo": 70,
        "limite_vermelho": 85,
    },
    "tracao_dianteira": {
        "rotulo": "TRAÇÃO DIANTEIRA",
        "unidade": "",
        "modo": "informativo",
    },
}


CORES_ESTADO = {
    "verde": "#39d98a",
    "amarelo": "#ffc857",
    "vermelho": "#ff5d5d",
    "sem_dados": "#718078",
}
