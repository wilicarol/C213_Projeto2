# Simulador de Elevador com Controle Fuzzy e Interface Gráfica

Este projeto simula o comportamento de um elevador residencial com controle fuzzy para deslocamento entre andares. A interface gráfica permite interações em tempo real, visualização da posição da cabine e controle de acesso aos andares. O sistema utiliza `PyQt5` e `PyQtGraph` para a interface e `scikit-fuzzy` para o controle fuzzy.

---

## 🎯 Funcionalidades

- Interface gráfica amigável com botões de chamada para todos os andares
- Controle fuzzy para aceleração e desaceleração suaves
- Regime de inicialização (aceleração controlada nos primeiros 2 segundos)
- Gráfico de deslocamento da cabine em tempo real
- Acesso protegido por senha para Subsolo e Andar Técnico
- Parada de emergência via botão STOP
- Suporte opcional a chamadas externas via MQTT

---

## 🧰 Requisitos

- Python 3.10+
- `pip install -r requirements.txt`

Recomenda-se instalar em um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate   # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
