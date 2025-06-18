import time
import numpy as np
import matplotlib.pyplot as plt
from fuzzy_controller import controle_fuzzy

# Parâmetros do sistema
k1_subida = 1
k1_descida = -1
k2 = 0.212312  
Ts = 0.2  # período de amostragem 

# Estado inicial
posicao_atual = 4  # teste no térreo
historico_posicao = [posicao_atual]
historico_tempo = [0]
tempo_total = 30  # segundos de simulação
sp = 16  #quarto andar

# Inicialização
erro_anterior = sp - posicao_atual
tempo = 0

# Loop de controle fuzzy
while tempo <= tempo_total:
    erro = sp - posicao_atual
    delta_erro = erro - erro_anterior

    # Evita valores fora do universo
    erro = max(0, min(erro, 28))
    delta_erro = max(-10, min(delta_erro, 10))

    # Entradas para o controle fuzzy
    controle_fuzzy.input['Erro'] = erro
    controle_fuzzy.input['DeltaErro'] = delta_erro
    controle_fuzzy.compute()

    potencia_motor = controle_fuzzy.output['PotenciaMotor']

    # Verifica sentido do movimento
    sentido = k1_subida if sp > posicao_atual else k1_descida

    # Atualiza posição com base na equação dada
    posicao_atual = sentido * posicao_atual * 0.9995 + potencia_motor * k2

    # Atualiza histórico
    tempo += Ts
    erro_anterior = erro
    historico_posicao.append(posicao_atual)
    historico_tempo.append(tempo)

    # Espera (simula tempo real)
    time.sleep(Ts)

# Plotando resultado
plt.figure(figsize=(10, 4))
plt.plot(historico_tempo, historico_posicao, label='Posição da Cabine', color='blue')
plt.axhline(y=sp, linestyle='--', color='red', label='SetPoint')
plt.xlabel('Tempo [s]')
plt.ylabel('Altura [m]')
plt.title('Simulação do Movimento da Cabine')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
