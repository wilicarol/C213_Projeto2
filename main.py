import time
import numpy as np
import matplotlib.pyplot as plt
from fuzzy_controller import controle_fuzzy

def simular_elevador(sp, posicao_inicial=4.0):
    # Parametros do sistema
    k1_subida = 1
    k1_descida = -1
    k2 = 0.212312
    Ts = 0.2  # 200 ms

    # Estados iniciais
    posicao_atual = posicao_inicial
    historico_posicao = [posicao_atual]
    historico_tempo = [0]

    # Cálculo do tempo total com base na distância e velocidade média
    distancia = abs(sp - posicao_atual)
    tempo_estimado = distancia / 0.5  # estimando 0.5 m/s de velocidade média
    tempo_total = tempo_estimado + 6  # margem de segurança

    erro_anterior = sp - posicao_atual
    tempo = 0
    tempo_inicial = 2.0  # tempo fixo de inicialização do motor
    em_fase_parada = False

    # Inicialização do motor
    tempo_passado = 0
    potencia_inicial = 0.315  # 31.5% de potência

    while tempo_passado < tempo_inicial:
        sentido = k1_subida if sp > posicao_atual else k1_descida
        posicao_atual = sentido * posicao_atual * 0.9995 + potencia_inicial * k2

        tempo += Ts
        tempo_passado += Ts
        historico_tempo.append(tempo)
        historico_posicao.append(posicao_atual)
        time.sleep(Ts)

    # loop de controle fuzzy
    while tempo <= tempo_total:

        erro = sp - posicao_atual
        delta_erro = erro - erro_anterior

        # Verifica condição de parada suave
        if abs(erro) < 0.0354 and abs(delta_erro) < 0.01:
            em_fase_parada = True

        if not em_fase_parada:
            # Entrada no fuzzy (limitando para universo)
            erro = np.clip(erro, 0, 28)
            delta_erro = np.clip(delta_erro, -10, 10)

            controle_fuzzy.input['Erro'] = erro
            controle_fuzzy.input['DeltaErro'] = delta_erro
            controle_fuzzy.compute()
            potencia = controle_fuzzy.output['PotenciaMotor']

        else:
            # Parada suave (freando aos poucos)
            potencia *= 0.85  # Vai reduzindo gradualmente

        # Aplica movimento
        sentido = k1_subida if sp > posicao_atual else k1_descida
        posicao_atual = sentido * posicao_atual * 0.9995 + potencia * k2

        tempo += Ts
        erro_anterior = erro
        historico_posicao.append(posicao_atual)
        historico_tempo.append(tempo)
        time.sleep(Ts)

    
    plt.figure(figsize=(10, 4))
    plt.plot(historico_tempo, historico_posicao, label='Posição da Cabine', color='blue')
    plt.axhline(y=sp, linestyle='--', color='red', label='SetPoint')
    plt.xlabel('Tempo [s]')
    plt.ylabel('Altura [m]')
    plt.title('Simulação do Movimento da Cabine (com Inicialização e Freio)')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

    return historico_tempo, historico_posicao, sp


# pra chamar o ambiente: .\.venv\Scripts\activate
