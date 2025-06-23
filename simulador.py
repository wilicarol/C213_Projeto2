import numpy as np
from fuzzy_controller import novo_controlador_fuzzy

class SimuladorElevador:
    def __init__(self, sp, posicao_inicial=4.0, Ts=0.05):
        self.sp = sp
        self.Ts = Ts
        self.k1_subida = 1
        self.k1_descida = -1
        self.k2 = 0.45
        self.posicao_atual = posicao_inicial
        self.tempo = 0.0
        self.tempo_passado = 0.0

        self.potencia = 0.45
        self.potencia_inicial = 0.45
        self.tempo_inicial = 1.0
        self.inicializando = True
        self.em_fase_parada = False

        self.erro_anterior = sp - posicao_inicial

        self.fuzzy = novo_controlador_fuzzy()

        self.historico_posicao = [posicao_inicial]
        self.historico_tempo = [0.0]

    def passo(self):
        if self.inicializando:
            sentido = self.k1_subida if self.sp > self.posicao_atual else self.k1_descida
            self.posicao_atual = sentido * self.posicao_atual * 0.998 + self.potencia_inicial * self.k2
            self.tempo_passado += self.Ts
            if self.tempo_passado >= self.tempo_inicial:
                self.inicializando = False
        else:
            erro = self.sp - self.posicao_atual
            delta_erro = erro - self.erro_anterior

            if abs(erro) < 0.0354 and abs(delta_erro) < 0.01:
                self.em_fase_parada = True

            if not self.em_fase_parada:
                erro = np.clip(erro, 0, 28)
                delta_erro = np.clip(delta_erro, -10, 10)
                self.fuzzy.input['Erro'] = erro
                self.fuzzy.input['DeltaErro'] = delta_erro
                self.fuzzy.compute()
                self.potencia = self.fuzzy.output['PotenciaMotor']
            else:
                self.potencia *= 0.85

            sentido = self.k1_subida if self.sp > self.posicao_atual else self.k1_descida
            self.posicao_atual = sentido * self.posicao_atual * 0.998 + self.potencia * self.k2
            self.erro_anterior = erro

        self.tempo += self.Ts
        self.historico_posicao.append(self.posicao_atual)
        self.historico_tempo.append(self.tempo)

        return not (self.em_fase_parada and self.potencia < 0.01)