import numpy as np
from fuzzy_controller import novo_controlador_fuzzy

class SimuladorElevador:
    def __init__(self, sp, posicao_inicial=4.0, Ts=0.2, debug=False):

        self.sp = sp
        self.Ts = Ts
        self.debug = debug  

        self.k1_subida = 1
        self.k1_descida = -1
        self.k1 = 1.0 # amortecimento em relação a posição

        self.k2_inicializacao = 0.251287
        self.k2_fuzzy = 0.212312

        # Posições e tempos atuais
        self.posicao_atual = posicao_inicial
        self.tempo = 0.0
        self.tempo_inicial = 0.0

        #Cotrole do estado
        self.inicializando = True
        self.em_fase_parada = False
        self.desligar_fuzzy = False
        self.em_parada_completa = False

        self.potencia_inercia = None
        self.erro_anterior = sp - posicao_inicial

        # Controlador fuzzy
        self.fuzzy = novo_controlador_fuzzy()

        self.historico_posicao = [posicao_inicial]
        self.historico_tempo = [0.0]

    def iniciar_parada_suave(self):
        self.potencia_inercia = self.fuzzy.output.get('PotenciaMotor', 0.25)

    def passo(self):
        sentido = self.k1_subida if self.sp > self.posicao_atual else self.k1_descida

        # Inicialização 
        if self.inicializando:
            self.tempo_inicial += self.Ts
            potencia_inicial = min((self.tempo_inicial / 2.0) * 0.315, 0.315)

            self.posicao_atual = (
                self.k1 * self.posicao_atual * 0.999 + potencia_inicial * self.k2_inicializacao * sentido
            )

            if self.debug:
                print(f"[Inicialização] Tempo: {self.tempo_inicial:.2f}s | Potência: {potencia_inicial:.3f} | Posição: {self.posicao_atual:.3f}")

            if self.tempo_inicial >= 2.0:
                self.inicializando = False

        else: # Inercia
            erro = self.sp - self.posicao_atual
            delta_erro = erro - self.erro_anterior
            delta_erro = np.clip(delta_erro, -1, 1)

            if self.desligar_fuzzy:
                if self.potencia_inercia is None:
                    self.potencia_inercia = self.fuzzy.output.get('PotenciaMotor', 0.25)

                self.potencia_inercia *= 0.90

                self.posicao_atual = (
                    self.k1 * self.posicao_atual * 0.9995 + self.potencia_inercia * self.k2_fuzzy * sentido
                )

                if self.debug:
                    print(f"[Inércia] Potência: {self.potencia_inercia:.3f} | Posição: {self.posicao_atual:.3f}")

                if self.potencia_inercia < 0.01:
                    self.em_parada_completa = True
                    return False

            else: # Controle Fuzzy
                classe_erro = self.classificar_erro(erro)
                classe_delta = self.classificar_delta_erro(delta_erro)

                # Condição de parada suave
                if classe_erro == 'pequeno' and classe_delta == 'variando':
                    self.em_fase_parada = True

                self.fuzzy.input['Erro'] = abs(erro)
                self.fuzzy.input['DeltaErro'] = abs(delta_erro)
                self.fuzzy.compute()
                
                #ajustando a intensidade da força do moter quando chega próximo ao destino
                potencia = self.fuzzy.output.get('PotenciaMotor', 0.25)
                if self.em_fase_parada:
                    potencia *= 0.85

                self.posicao_atual = (
                    self.k1 * self.posicao_atual * 0.9995 + potencia * self.k2_fuzzy * sentido
                )

                if self.debug:
                    print(f"[Fuzzy] Erro: {abs(erro):.3f} ({classe_erro}) | ΔErro: {abs(delta_erro):.3f} ({classe_delta}) | Potência: {potencia:.3f} | Posição: {self.posicao_atual:.3f}")

                self.erro_anterior = erro

        self.tempo += self.Ts
        self.historico_posicao.append(self.posicao_atual)
        self.historico_tempo.append(self.tempo)

        return not (self.em_fase_parada and self.desligar_fuzzy)

    # Classificadores para condição de parada
    def classificar_erro(self, erro):
        erro_abs = abs(erro)
        if erro_abs < 0.02:
            return 'muito_pequeno'
        elif erro_abs < 0.05:
            return 'pequeno'
        else:
            return 'grande'

    def classificar_delta_erro(self, delta_erro):
        delta_abs = abs(delta_erro)
        if delta_abs < 0.005:
            return 'estável'
        elif delta_abs < 0.02:
            return 'variando'
        else:
            return 'instável'
