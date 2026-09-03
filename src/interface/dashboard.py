"""Dashboard Mandacaru Baja. Todo dado exibido vem de ImportadorDados."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config.metricas import CORES_ESTADO
from src.dados.importador import ImportadorDados

st.set_page_config(page_title="Mandacaru Baja | Telemetria", page_icon="🏎️", layout="wide",
                   initial_sidebar_state="collapsed")

VERDE, AMARELO, VERMELHO = "#62bb78", "#e8b85c", "#ed554f"
INTERVALO_ATUALIZACAO_S = 1.0
CSS_BASE = """
<style>
:root{--fundo:#020909;--painel:#071312;--borda:#213a34;--texto:#d9dfdc;--suave:#8e9995;--verde:#62bb78}
html,body,[class*="st-"]{font-family:"Arial Narrow","Segoe UI",sans-serif}.stApp{background:radial-gradient(circle at 51% 0,rgba(24,73,58,.17),transparent 36rem),linear-gradient(115deg,#020808,#03100f 55%,#020808);color:var(--texto)}
[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{display:none!important}.block-container{max-width:1680px;padding:1rem .55rem 1.8rem}
.topo{display:grid;grid-template-columns:1fr auto 1fr;align-items:start;padding:.1rem .45rem .8rem}.marca{font-size:1.55rem;font-weight:760;letter-spacing:.035em}.sessao{font-size:1rem;letter-spacing:.11em;font-weight:650;text-align:center;padding-top:.25rem}.conexao{text-align:right}.selo{display:inline-flex;gap:.55rem;align-items:center;border:1px solid var(--verde);color:var(--verde);border-radius:5px;padding:.3rem .65rem}.ultimo{color:var(--suave);font-size:.74rem;margin-top:.35rem}
.barra-fonte{border:1px solid var(--borda);border-radius:6px;padding:.55rem .75rem .1rem;margin-bottom:.45rem;background:rgba(7,19,18,.72)}
.secao{display:flex;align-items:center;gap:.8rem;color:#bdc5c1;font-size:.98rem;letter-spacing:.1em;margin:1rem .5rem .38rem}.secao:after{content:"";height:1px;flex:1;background:linear-gradient(90deg,var(--borda),transparent)}
.resumo{min-height:91px;border:1px solid var(--borda);border-radius:6px;padding:.82rem .95rem;background:linear-gradient(145deg,rgba(10,27,25,.94),rgba(5,16,15,.95))}.resumo-topo{display:flex;align-items:center;justify-content:space-between}.rotulo{color:#aeb7b3;font-size:.75rem;letter-spacing:.09em}.icone{color:#96a19c;font-size:1.25rem;margin-right:.55rem}.valor{font-size:1.62rem;font-weight:680;margin-top:.7rem}.unidade{color:#abb5b0;font-size:.78rem;margin-left:.28rem;font-weight:500}.led{width:.66rem;height:.66rem;border-radius:50%;display:inline-block;box-shadow:0 0 11px currentColor}
.analise{border:1px solid var(--borda);border-radius:6px;background:rgba(6,19,18,.94);padding:.72rem .85rem .35rem;min-height:344px}.cab-analise{display:flex;justify-content:space-between;align-items:center}.titulo-analise{letter-spacing:.1em;font-size:.84rem}.valor-analise{color:var(--verde);font-size:1.4rem;font-weight:700;margin:.35rem 0}.leds{display:flex;gap:.75rem}.leds .led{width:.55rem;height:.55rem;opacity:.25;box-shadow:none}.leds .ativo{opacity:1;box-shadow:0 0 10px currentColor}
.estatisticas{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--borda);padding-top:.5rem}.est{text-align:center;color:#929e98;font-size:.65rem;letter-spacing:.08em}.est+.est{border-left:1px solid var(--borda)}.est strong{display:block;color:#c4ccc8;font-size:.74rem;margin-top:.2rem}
.tanque-area{display:flex;align-items:center;justify-content:center;height:150px;gap:2.4rem}.tanque{position:relative;width:78px;height:116px;border:3px solid #95a09b;border-radius:12px 12px 6px 6px;padding:7px;box-shadow:inset 0 0 0 2px #273a35}.tanque:before{content:"";position:absolute;width:36px;height:9px;border:3px solid #95a09b;border-bottom:0;border-radius:5px 5px 0 0;top:-12px;left:18px}.tanque:after{content:"";position:absolute;width:22px;height:62px;border:3px solid #95a09b;border-left:0;border-radius:0 17px 17px 0;right:-27px;top:22px}.reservatorio{position:relative;width:100%;height:100%;overflow:hidden;border-radius:6px;background:#0b1715}.liquido{position:absolute;left:0;right:0;bottom:0;transition:height .5s;opacity:.92}.liquido:before{content:"";position:absolute;height:5px;left:-8px;right:-8px;top:-2px;border-radius:50%;background:rgba(220,255,230,.38)}.tanque-info{text-align:left;min-width:125px}.tanque-info strong{display:block;font-size:2rem}.tanque-info span{color:var(--suave);font-size:.68rem;letter-spacing:.06em;line-height:1.65}
.media-consumo{display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--borda);padding:.55rem .35rem;color:var(--suave);font-size:.7rem;letter-spacing:.08em}.media-consumo strong{color:#dd78a4;font-size:1rem;letter-spacing:.02em}
.painel-sim{border-left:3px solid var(--verde);padding:.25rem 0 .25rem 1rem;margin:.55rem 0 1rem;color:#aeb9b4}.estado-carro{border:1px solid var(--borda);border-radius:5px;padding:.72rem;text-align:center;background:var(--painel)}
div[data-testid="stTabs"] button{font-weight:650;letter-spacing:.06em;padding:.75rem 2rem}div[data-testid="stTabs"] [data-baseweb="tab-list"]{border:1px solid var(--borda);border-radius:6px;background:rgba(7,19,18,.8)}div[data-testid="stTabs"] [aria-selected="true"]{color:var(--verde)!important;background:rgba(49,119,80,.12)}
@media(max-width:900px){.topo{grid-template-columns:1fr}.sessao,.conexao{text-align:left;margin-top:.5rem}}
</style>
"""

CSS_CLARO = """
<style>
:root{--fundo:#edf3ef;--painel:#ffffff;--borda:#aebfb6;--texto:#142019;--suave:#3f5047}
.stApp{background:radial-gradient(circle at 51% 0,rgba(74,160,107,.13),transparent 34rem),#edf3ef;color:var(--texto)}
.marca,.sessao,.valor,.titulo-analise,.tanque-info strong{color:#17231d}
.secao,.rotulo,.ultimo,.unidade,.est,.tanque-info span,.painel-sim{color:#3f5047}
.resumo{background:linear-gradient(145deg,#ffffff,#f4f8f6)}
[data-testid="stVerticalBlockBorderWrapper"],.estado-carro{background:#ffffff!important;border-color:#c7d7cf!important}
.reservatorio{background:#e3ebe7}.estatisticas,.est+.est{border-color:#c7d7cf}
div[data-baseweb="tab-list"]{background:#ffffff!important}
input,[data-baseweb="select"]>div{background:#ffffff!important;color:#17231d!important}
.stApp [data-testid="stWidgetLabel"] p,.stApp [data-testid="stRadio"] p,.stApp label,
.stApp [data-testid="stCaptionContainer"],.stApp [data-testid="stMarkdownContainer"]{color:#26372e!important}
.stApp input,.stApp [role="combobox"]{color:#142019!important}
.media-consumo strong{color:#8d2855!important}
.est strong{color:#26372e!important}
.stApp button{background:#f7faf8!important;color:#26352d!important;border-color:#b9cbc2!important}
.stApp button[kind="primary"]{background:#3d9d63!important;color:#ffffff!important;border-color:#3d9d63!important}
</style>
"""

ICONES = {"rpm":"◴","combustivel_pct":"▣","velocidade":"⌁","odometro":"⌖",
          "temp_motor":"♨","temp_cvt":"◉","temp_esp":"◇","consumo_ml":"∿",
          "tracao_dianteira":"◆"}
# Identidade visual de cada métrica. Estas cores identificam os dados;
# verde/amarelo/vermelho continuam reservados aos LEDs de estado.
CORES = {
    "rpm":"#58c878",
    "combustivel_pct":"#e4ad49",
    "velocidade":"#46b6d9",
    "odometro":"#7f8ee8",
    "temp_motor":"#f06f5f",
    "temp_cvt":"#b879e2",
    "consumo_ml":"#dd78a4",
}
CORES_CLARO = {
    "rpm":"#176b34",
    "combustivel_pct":"#8a5900",
    "velocidade":"#075f7d",
    "odometro":"#35449a",
    "temp_motor":"#a52d22",
    "temp_cvt":"#68318e",
    "consumo_ml":"#8d2855",
}

def importador() -> ImportadorDados:
    if "importador" not in st.session_state:
        st.session_state.importador = ImportadorDados()
    return st.session_state.importador

def aplicar_tema():
    st.markdown(CSS_BASE,unsafe_allow_html=True)
    if st.session_state.get("tema","escuro")=="claro":
        st.markdown(CSS_CLARO,unsafe_allow_html=True)

def paleta():
    if st.session_state.get("tema","escuro")=="claro":
        return {"fundo":"#ffffff","texto":"#26372e","grade":"#bccdc4"}
    return {"fundo":"rgba(0,0,0,0)","texto":"#8f9b95","grade":"#1b302b"}

def cor_metrica(chave):
    if st.session_state.get("tema","escuro")=="claro":
        return CORES_CLARO[chave]
    return CORES[chave]

def fmt(chave, valor):
    if valor is None:
        return "NULL"
    if chave=="rpm":
        return f"{int(valor):,}".replace(",",".")
    casas = 1 if chave in {"velocidade","combustivel_pct","temp_motor","temp_cvt","temp_esp"} else 2
    return f"{float(valor):.{casas}f}".replace(".",",")

def topo(p):
    if p.fonte=="Simulado":
        cor,status,sessao=VERDE,"SIMULAÇÃO","SESSÃO SIMULADA"
    elif p.recebido:
        cor,status,sessao=VERDE,"RECEBENDO","SESSÃO REAL"
    elif p.conectado:
        cor,status,sessao=AMARELO,"AGUARDANDO","SESSÃO REAL"
    else:
        cor,status,sessao="#718078","DESCONECTADO","SESSÃO REAL"
    horario=f"{p.telemetria.timestamp:%H:%M:%S}" if p.recebido else "--:--:--"
    st.markdown(f"""<div class="topo"><div class="marca">MANDACARU BAJA | TELEMETRIA</div>
    <div class="sessao">{sessao}</div><div class="conexao"><div class="selo" style="border-color:{cor};color:{cor}">
    <span class="led" style="background:{cor};color:{cor}"></span>{status}</div>
    <div class="ultimo">{p.mensagem} · {horario}</div></div></div>""", unsafe_allow_html=True)

def controles_globais(i):
    a,b=st.columns([4,1])
    with a:
        fonte=st.radio("MODO DE OPERAÇÃO",["Simulado","Serial"],horizontal=True,index=0 if i.fonte=="Simulado" else 1)
        mudou=fonte!=i.fonte
        i.selecionar_fonte(fonte)
        if mudou:
            st.session_state.historico=[]
            st.rerun()
    with b:
        st.write("")
        rotulo="☀ MODO CLARO" if st.session_state.tema=="escuro" else "☾ MODO ESCURO"
        if st.button(rotulo,width="stretch"):
            st.session_state.tema="claro" if st.session_state.tema=="escuro" else "escuro"
            st.rerun()

def controles_serial(i):
    titulo("CONEXÃO COM A ECU")
    a,b,c=st.columns([1.2,.8,1])
    with a: porta=st.text_input("PORTA SERIAL","COM3")
    with b: baud=st.selectbox("BAUD RATE",[9600,19200,115200])
    with c:
        st.write("")
        if i.serial.conectado and st.button("DESCONECTAR",width="stretch"):
            i.serial.desconectar(); st.rerun()
        elif not i.serial.conectado and st.button("CONECTAR",type="primary",width="stretch"):
            try: i.serial.conectar(porta,int(baud))
            except Exception as erro: st.error(f"Falha ao abrir {porta}: {erro}")
            else: st.rerun()
    st.caption("Os ajustes abaixo são locais, pois a ECU não recebe comandos pelo protocolo LoRa atual.")
    encher,resetar=st.columns(2)
    with encher:
        if st.button("⛽ ENCHER TANQUE",width="stretch",key="encher_serial"):
            if i.encher_tanque(): st.success("Tanque considerado cheio nesta sessão real.")
            else: st.warning("Aguardando o primeiro pacote válido da ECU.")
    with resetar:
        if st.button("↺ RESETAR CONSUMO",width="stretch",key="resetar_serial"):
            if i.resetar_consumo(): st.success("Consumo e média km/L reiniciados localmente.")
            else: st.warning("Aguardando o primeiro pacote válido da ECU.")

def titulo(texto):
    st.markdown(f'<div class="secao">{texto}</div>',unsafe_allow_html=True)

def resumo(p):
    titulo("RESUMO EM TEMPO REAL")
    ordem=["rpm","combustivel_pct","velocidade","odometro","temp_motor","temp_cvt","consumo_ml"]
    grupos=[ordem[:4],ordem[4:]]
    for grupo in grupos:
        cols=st.columns(len(grupo))
        for col,chave in zip(cols,grupo):
            d=p.dados[chave]; cor=CORES_ESTADO[d.estado]
            valor=fmt(chave,d.valor)
            unidade="" if d.valor is None else d.unidade
            with col:
                st.markdown(f"""<div class="resumo"><div class="resumo-topo"><span class="rotulo"><span class="icone" style="color:{cor_metrica(chave)}">{ICONES[chave]}</span>{d.rotulo}</span>
                <span class="led" style="background:{cor};color:{cor}" title="{d.estado}"></span></div>
                <div class="valor" style="color:{cor_metrica(chave)}">{valor}<span class="unidade">{unidade}</span></div></div>""",unsafe_allow_html=True)

def registrar(p):
    if not p.recebido:
        return
    h=st.session_state.setdefault("historico",[]); t=p.telemetria
    h.append({"horario":t.timestamp,"rpm":t.rpm,"velocidade":t.velocidade,
      "combustivel_pct":t.combustivel_pct,"consumo_ml":t.consumo_ml,"odometro":t.odometro,
      "consumo_kml":t.consumo_kml,"temp_motor":t.temp_motor,"temp_cvt":t.temp_cvt,"temp_esp":t.temp_esp})
    del h[:-300]

def quadro():
    return pd.DataFrame(st.session_state.get("historico",[]))

def faixa_tempo(df):
    if df.empty:
        return None
    fim=pd.Timestamp(df["horario"].max())
    return [fim-pd.Timedelta(seconds=30),fim]

def figura_linha(df,chave,altura=215):
    cores_tema=paleta()
    f=go.Figure()
    if not df.empty:
        f.add_trace(go.Scatter(x=df.horario,y=df[chave],mode="lines",line=dict(color=cor_metrica(chave),width=1.9),
          fill="tozeroy",fillcolor="rgba(77,145,91,.045)",hovertemplate="%{y:.2f}<extra></extra>"))
    f.update_layout(height=altura,margin=dict(l=52,r=24,t=12,b=42),showlegend=False,paper_bgcolor=cores_tema["fundo"],
      plot_bgcolor=cores_tema["fundo"],font=dict(color=cores_tema["texto"],size=11),
      xaxis=dict(gridcolor=cores_tema["grade"],zeroline=False,tickformat="%H:%M:%S",range=faixa_tempo(df),
                 tickfont=dict(color=cores_tema["texto"],size=10),title_font=dict(color=cores_tema["texto"],size=11),
                 automargin=True),
      yaxis=dict(
          gridcolor=cores_tema["grade"],zeroline=False,
          range=[0,6000] if chave=="rpm" else None,
          tickvals=[0,1000,2000,3000,4000,5000,6000] if chave=="rpm" else None,
          tickfont=dict(color=cores_tema["texto"],size=10),title_font=dict(color=cores_tema["texto"],size=11),
          automargin=True,
      ))
    return f

def leds(estado):
    html=""
    for nome,cor in [("verde",VERDE),("amarelo",AMARELO),("vermelho",VERMELHO)]:
        html+=f'<span class="led {"ativo" if nome==estado else ""}" style="background:{cor};color:{cor}"></span>'
    return f'<div class="leds">{html}</div>'

def stats(df,chave,unidade):
    if df.empty:
        minimo=maximo=media="NULL"
        unidade=""
    else:
        minimo,maximo,media=(f"{df[chave].min():.1f}",f"{df[chave].max():.1f}",f"{df[chave].mean():.1f}")
    return f"""<div class="estatisticas"><div class="est">MÍN.<strong>{minimo} {unidade}</strong></div>
    <div class="est">MÁX.<strong>{maximo} {unidade}</strong></div>
    <div class="est">MÉDIA<strong>{media} {unidade}</strong></div></div>"""

def painel_grafico(p,df,chave):
    d=p.dados[chave]
    unidade="" if d.valor is None else d.unidade
    st.markdown(f'<div class="cab-analise"><span class="titulo-analise">{d.rotulo}</span>{leds(d.estado)}</div>'
      f'<div class="valor-analise" style="color:{cor_metrica(chave)}">{fmt(chave,d.valor)}<span class="unidade">{unidade}</span></div>',unsafe_allow_html=True)
    st.plotly_chart(
        figura_linha(df,chave),
        width="stretch",
        theme=None,
        config={"displayModeBar":False},
        key=f"grafico_sensor_{chave}",
    )
    st.markdown(stats(df,chave,d.unidade),unsafe_allow_html=True)

def figura_combustivel(df):
    """Mostra as duas grandezas da ECU sem misturá-las: nível e consumo."""
    tema=paleta(); f=go.Figure()
    if not df.empty:
        f.add_trace(go.Scatter(
            x=df.horario,y=df["combustivel_pct"],name="Nível (%)",mode="lines",
            line=dict(color=cor_metrica("combustivel_pct"),width=2.2),
            hovertemplate="Nível: %{y:.2f}%<extra></extra>",
        ))
        f.add_trace(go.Scatter(
            x=df.horario,y=df["consumo_ml"],name="Consumido (mL)",mode="lines",yaxis="y2",
            line=dict(color=cor_metrica("consumo_ml"),width=2.2),
            hovertemplate="Consumido: %{y:.2f} mL<extra></extra>",
        ))
    f.update_layout(
        height=195,margin=dict(l=52,r=58,t=38,b=42),
        paper_bgcolor=tema["fundo"],plot_bgcolor=tema["fundo"],font=dict(color=tema["texto"],size=10),
        legend=dict(orientation="h",y=1.20,font=dict(size=10)),
        xaxis=dict(gridcolor=tema["grade"],tickformat="%H:%M:%S",range=faixa_tempo(df),tickfont=dict(color=tema["texto"],size=9),automargin=True),
        yaxis=dict(title="%",range=[0,105],gridcolor=tema["grade"],tickfont=dict(color=tema["texto"],size=9),title_font=dict(color=tema["texto"],size=10),automargin=True),
        yaxis2=dict(title="mL",overlaying="y",side="right",showgrid=False,tickfont=dict(color=tema["texto"],size=9),title_font=dict(color=tema["texto"],size=10),automargin=True),
    )
    return f

def painel_tanque(p,df):
    d=p.dados["combustivel_pct"]
    sem_dados=d.valor is None
    pct=0.0 if sem_dados else max(0,min(100,float(d.valor)))
    consumo=p.dados["consumo_ml"].valor
    texto_pct="NULL" if sem_dados else f"{pct:.1f}%"
    texto_consumo="AGUARDANDO DADOS" if consumo is None else f"{consumo:.1f} mL CONSUMIDOS"
    media=p.dados["consumo_kml"].valor
    texto_media="NULL" if media is None else f"{media:.2f} km/L"
    cor_liquido="#718078" if sem_dados else cor_metrica("combustivel_pct")
    st.markdown(f'<div class="cab-analise"><span class="titulo-analise">SISTEMA DE COMBUSTÍVEL</span>{leds(d.estado)}</div>',unsafe_allow_html=True)
    st.markdown(f"""<div class="tanque-area"><div class="tanque"><div class="reservatorio"><div class="liquido"
    style="height:{pct:.1f}%;background:linear-gradient(#f2c866,{cor_liquido})"></div></div></div>
    <div class="tanque-info"><strong style="color:{cor_metrica('combustivel_pct')}">{texto_pct}</strong>
    <span>{texto_consumo}<br>CAPACIDADE: 5.670 mL</span></div></div>""",unsafe_allow_html=True)
    st.plotly_chart(figura_combustivel(df),width="stretch",theme=None,config={"displayModeBar":False},key="grafico_combustivel")
    st.markdown(f'<div class="media-consumo"><span>CONSUMO MÉDIO DA SESSÃO</span><strong>{texto_media}</strong></div>',unsafe_allow_html=True)
    st.markdown(stats(df,"combustivel_pct","%"),unsafe_allow_html=True)

def analises(p):
    df=quadro(); titulo("ANÁLISE DOS SENSORES")
    linhas=[[("rpm",0),("velocidade",0),("combustivel_pct",1)],
            [("odometro",0),("consumo_ml",0),("temp_motor",0),("temp_cvt",0)]]
    for linha in linhas:
        cols=st.columns(len(linha))
        for col,(chave,tanque) in zip(cols,linha):
            with col:
                with st.container(border=True):
                    painel_tanque(p,df) if tanque else painel_grafico(p,df,chave)

def grafico_geral():
    df=quadro(); tema=paleta(); titulo("TELEMETRIA GERAL EM TEMPO REAL")
    op={"RPM":"rpm","Velocidade":"velocidade","Motor °C":"temp_motor","CVT °C":"temp_cvt",
        "Combustível %":"combustivel_pct","Consumo mL":"consumo_ml","Distância km":"odometro"}
    escolhas=st.multiselect(
        "SÉRIES EXIBIDAS",list(op),
        default=["RPM","Velocidade","Motor °C","CVT °C","Combustível %"],
    )
    f=go.Figure()
    chaves_eixo_principal=[op[nome] for nome in escolhas if op[nome]!="rpm"]
    maior_valor=0.0
    if not df.empty and chaves_eixo_principal:
        janela=faixa_tempo(df)
        dados_visiveis=df[df["horario"]>=janela[0]] if janela else df
        maior_valor=max(float(dados_visiveis[chave].max()) for chave in chaves_eixo_principal)
    limite_superior=max(1.0,maior_valor*1.10)
    if not df.empty:
        for nome in escolhas:
            chave=op[nome]
            f.add_trace(go.Scatter(
                x=df.horario,y=df[chave],name=nome,mode="lines",
                yaxis="y2" if chave=="rpm" else "y",
                line=dict(color=cor_metrica(chave),width=2.2),
                hovertemplate=f"{nome}: %{{y:.2f}}<extra></extra>",
            ))
    f.update_layout(height=400,margin=dict(l=70,r=72,t=42,b=52),paper_bgcolor=tema["fundo"],plot_bgcolor=tema["fundo"],
      font=dict(color=tema["texto"],size=11),legend=dict(orientation="h",y=1.10,font=dict(size=11)),
      xaxis=dict(gridcolor=tema["grade"],tickformat="%H:%M:%S",range=faixa_tempo(df),tickfont=dict(color=tema["texto"],size=10),automargin=True),
      yaxis=dict(title="Valores reais",gridcolor=tema["grade"],range=[0,limite_superior],tickfont=dict(color=tema["texto"],size=10),title_font=dict(color=tema["texto"],size=11),automargin=True),
      yaxis2=dict(title="RPM",overlaying="y",side="right",showgrid=False,range=[0,6000],tickfont=dict(color=tema["texto"],size=10),title_font=dict(color=tema["texto"],size=11),automargin=True,
                  tickvals=[0,1000,2000,3000,4000,5000,6000]))
    st.plotly_chart(f,width="stretch",theme=None,config={"displayModeBar":False},key="grafico_geral")

def simulador(i):
    s=i.simulador
    st.markdown('<div class="painel-sim"><b>CONTROLE DO VEÍCULO SIMULADO</b><br>A ignição e o acelerador são os controles; todos os demais dados são calculados.</div>',unsafe_allow_html=True)
    a,b,c,d,e=st.columns(5)
    with a:
        if st.button("▶ LIGAR CARRO",type="primary",width="stretch"):
            s.ligar(); i.selecionar_fonte("Simulado"); st.rerun()
    with b:
        if st.button("■ DESLIGAR CARRO",width="stretch"): s.desligar(); st.rerun()
    with c:
        if st.button("↻ REINICIAR SIMULAÇÃO",width="stretch"):
            s.reiniciar(); st.session_state.historico=[]; st.rerun()
    with d:
        if st.button("⛽ ENCHER TANQUE",width="stretch",key="encher_simulado"):
            i.encher_tanque(); st.rerun()
    with e:
        if st.button("↺ RESETAR CONSUMO",width="stretch",key="resetar_simulado"):
            i.resetar_consumo(); st.rerun()
    acelerador=st.slider("ACELERADOR",0,100,int(s.acelerador_pct),1,"%d%%",disabled=not s.ligado)
    s.definir_acelerador(acelerador); p=i.ler()
    st.markdown(f'<div class="estado-carro">CARRO {"LIGADO" if s.ligado else "DESLIGADO"} · {s.acelerador_pct:.0f}% DE ACELERADOR · {p.telemetria.rpm} RPM</div>',unsafe_allow_html=True)

@st.fragment(run_every=INTERVALO_ATUALIZACAO_S)
def tempo_real(i):
    p=i.ler(); registrar(p); resumo(p); analises(p); grafico_geral()

@st.fragment(run_every=INTERVALO_ATUALIZACAO_S)
def cabecalho(i):
    topo(i.ler())

def executar():
    if "tema" not in st.session_state:
        st.session_state.tema="escuro"
    aplicar_tema()
    i=importador()
    controles_globais(i)
    cabecalho(i)
    if i.fonte=="Serial":
        controles_serial(i)
        tempo_real(i)
    else:
        titulo("DADOS SIMULADOS")
        simulador(i)
        tempo_real(i)
