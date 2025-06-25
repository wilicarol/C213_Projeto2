import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
import skfuzzy.control as ctrl

# Definição dos universos de discurso
erro_range = np.arange(0, 32.1, 0.1)
deltaerro_range = np.arange(-1, 1.01, 0.01)
potencia_range = np.arange(0, 1.01, 0.01)

# Variáveis fuzzy
Erro = ctrl.Antecedent(erro_range, 'Erro')
DeltaErro = ctrl.Antecedent(deltaerro_range, 'DeltaErro')
PotenciaMotor = ctrl.Consequent(potencia_range, 'PotenciaMotor')

# Unidades e labels
Erro.unit = 'm'; Erro.membershipA = 'E'
DeltaErro.unit = 'm'; DeltaErro.membershipA = 'ΔE'
PotenciaMotor.unit = '%'; PotenciaMotor.membershipA = 'PM'

# Funções de pertinência - Erro
Erro['P'] = fuzz.trapmf(Erro.universe, [0, 0, 4, 12])      
Erro['M'] = fuzz.trimf(Erro.universe, [8, 16, 24])         
Erro['G'] = fuzz.trapmf(Erro.universe, [20, 28, 32, 32]) 

# DeltaErro
DeltaErro['N'] = fuzz.trapmf(DeltaErro.universe, [-1, -1, -0.3, -0.05])
DeltaErro['ZE'] = fuzz.trimf(DeltaErro.universe, [-0.1, 0.0, 0.1])
DeltaErro['P'] = fuzz.trapmf(DeltaErro.universe, [0.05, 0.3, 1.0, 1.0])

# PotênciaMotor
PotenciaMotor['B'] = fuzz.trimf(PotenciaMotor.universe, [0.0, 0.15, 0.3])
PotenciaMotor['M'] = fuzz.trimf(PotenciaMotor.universe, [0.25, 0.5, 0.75])
PotenciaMotor['A'] = fuzz.trimf(PotenciaMotor.universe, [0.6, 0.85, 1.0])

# Regras fuzzy baseadas na tabela fornecida
regras = [
    ctrl.Rule(Erro['P'] & DeltaErro['N'], PotenciaMotor['M']),
    ctrl.Rule(Erro['P'] & DeltaErro['ZE'], PotenciaMotor['B']),
    ctrl.Rule(Erro['P'] & DeltaErro['P'], PotenciaMotor['B']),
    ctrl.Rule(Erro['M'] & DeltaErro['N'], PotenciaMotor['A']),
    ctrl.Rule(Erro['M'] & DeltaErro['ZE'], PotenciaMotor['M']),
    ctrl.Rule(Erro['M'] & DeltaErro['P'], PotenciaMotor['B']),
    ctrl.Rule(Erro['G'] & DeltaErro['N'], PotenciaMotor['A']),
    ctrl.Rule(Erro['G'] & DeltaErro['ZE'], PotenciaMotor['M']),
    ctrl.Rule(Erro['G'] & DeltaErro['P'], PotenciaMotor['M']),
]

# Função de criação do controlador
def novo_controlador_fuzzy():
    sistema = ctrl.ControlSystem(regras)
    return ctrl.ControlSystemSimulation(sistema)

# Plotagem
if __name__ == "__main__":
    fig, axs = plt.subplots(3, 1, figsize=(8, 8))

    for label in Erro.terms:
        axs[0].plot(Erro.universe, Erro[label].mf, label=label)
    axs[0].set_title("Erro [m]")
    axs[0].set_ylabel("Pertinência")
    axs[0].legend(loc="upper right")

    for label in DeltaErro.terms:
        axs[1].plot(DeltaErro.universe, DeltaErro[label].mf, label=label)
    axs[1].set_title("DeltaErro [m]")
    axs[1].set_ylabel("Pertinência")
    axs[1].legend(loc="upper right")

    for label in PotenciaMotor.terms:
        axs[2].plot(PotenciaMotor.universe, PotenciaMotor[label].mf, label=label)
    axs[2].set_title("Potência do Motor [%]")
    axs[2].set_ylabel("Pertinência")
    axs[2].set_xlabel("Valor")
    axs[2].legend(loc="upper right")

    plt.tight_layout()
    plt.show()
