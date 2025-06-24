import numpy as np
from fuzzy_controller import novo_controlador_fuzzy

class SimuladorElevador:
    def __init__(self, sp, posicao_inicial=4.0, Ts=0.05):
        self.sp = sp
        self.Ts = Ts
        self.k1_subida = 1
        self.k1_descida = -1
        self.k2 = 0.251287  # ganho realista para deslocamento
        self.k1 = 1.0

        self.posicao_atual = posicao_inicial
        self.tempo = 0.0
        self.tempo_passado = 0.0

        self.tempo_inicial = 0.0
        self.inicializando = True
        self.em_fase_parada = False

        self.erro_anterior = sp - posicao_inicial

        self.fuzzy = novo_controlador_fuzzy()

        self.historico_posicao = [posicao_inicial]
        self.historico_tempo = [0.0]

    def passo(self):
        sentido = self.k1_subida if self.sp > self.posicao_atual else self.k1_descida

        if self.inicializando:
            self.tempo_inicial += self.Ts
            potencia_inicial = (self.tempo_inicial / 2.0) * 0.315
            potencia_inicial = min(potencia_inicial, 0.315)

            self.posicao_atual += potencia_inicial * self.k2 * sentido

            if self.tempo_inicial >= 2.0:
                self.inicializando = False
        else:
            erro = self.sp - self.posicao_atual
            delta_erro = erro - self.erro_anterior

            if abs(erro) < 0.0354 and abs(delta_erro) < 0.01:
                self.em_fase_parada = True

            if not self.em_fase_parada:
                delta_erro = np.clip(delta_erro, -10, 10)
                self.fuzzy.input['Erro'] = erro
                self.fuzzy.input['DeltaErro'] = delta_erro
                self.fuzzy.compute()
                potencia = self.fuzzy.output['PotenciaMotor']
            else:
                potencia = self.fuzzy.output['PotenciaMotor'] * 0.85

            self.posicao_atual += potencia * self.k2 * sentido
            self.erro_anterior = erro

        self.tempo += self.Ts
        self.historico_posicao.append(self.posicao_atual)
        self.historico_tempo.append(self.tempo)

        return not (self.em_fase_parada and potencia < 0.01)
