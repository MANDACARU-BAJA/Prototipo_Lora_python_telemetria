# Mandacaru Baja — Telemetria LoRa

Interface Streamlit com uma única camada de importação de dados. A tela pode
alternar entre a porta serial da ECU e um veículo simulado controlável.

## Executar no VS Code

No terminal, dentro desta pasta:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Protocolo serial esperado

```text
<velocidade,consumo_ml,odometro,rpm,combustivel_pct,temp_motor,temp_cvt,temp_esp,tracao>
```

Exemplo:

```text
<42,135.00,3.27,2850,97,86.00,61.00,48.00,0>
```

As regras dos LEDs ficam centralizadas em `src/config/metricas.py`. Todos os
dados, inclusive os simulados, passam por `ImportadorDados` antes de chegar à
interface.
