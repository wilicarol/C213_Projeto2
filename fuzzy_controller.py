import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Universo das variáveis
erro_range = np.arange(0, 28.1, 0.1)         # Erro entre 0 e 28 metros (sem negativos)
deltaerro_range = np.arange(-10, 10.1, 0.1)  # DeltaErro com variação positiva/negativa
potencia_range = np.arange(0, 1.01, 0.01)    # Potência normalizada

# Entradas
Erro = ctrl.Antecedent(erro_range, 'Erro')
DeltaErro = ctrl.Antecedent(deltaerro_range, 'DeltaErro')

# Saída
PotenciaMotor = ctrl.Consequent(potencia_range, 'PotenciaMotor')

# Funções de pertinência do Erro (somente positivo, como o professor orientou)
Erro['PEQ'] = fuzz.trapmf(Erro.universe, [0, 0, 4, 8])
Erro['MED'] = fuzz.trimf(Erro.universe, [6, 14, 20])
Erro['GRD'] = fuzz.trapmf(Erro.universe, [18, 22, 28, 28])

# Funções de pertinência do DeltaErro (variação pequena, média ou alta)
DeltaErro['NEG'] = fuzz.trapmf(DeltaErro.universe, [-10, -10, -3, -1])
DeltaErro['ZER'] = fuzz.trimf(DeltaErro.universe, [-2, 0, 2])
DeltaErro['POS'] = fuzz.trapmf(DeltaErro.universe, [1, 3, 10, 10])

# Funções de pertinência da saída: Potência do motor
PotenciaMotor['BAIXA'] = fuzz.trimf(PotenciaMotor.universe, [0.0, 0.15, 0.3])
PotenciaMotor['MEDIA'] = fuzz.trimf(PotenciaMotor.universe, [0.25, 0.5, 0.75])
PotenciaMotor['ALTA'] = fuzz.trimf(PotenciaMotor.universe, [0.6, 0.85, 1.0])

# Regras do sistema fuzzy
regras = [
    ctrl.Rule(Erro['PEQ'] & DeltaErro['NEG'], PotenciaMotor['MEDIA']),
    ctrl.Rule(Erro['PEQ'] & DeltaErro['ZER'], PotenciaMotor['BAIXA']),
    ctrl.Rule(Erro['PEQ'] & DeltaErro['POS'], PotenciaMotor['BAIXA']),

    ctrl.Rule(Erro['MED'] & DeltaErro['NEG'], PotenciaMotor['ALTA']),
    ctrl.Rule(Erro['MED'] & DeltaErro['ZER'], PotenciaMotor['MEDIA']),
    ctrl.Rule(Erro['MED'] & DeltaErro['POS'], PotenciaMotor['BAIXA']),

    ctrl.Rule(Erro['GRD'] & DeltaErro['NEG'], PotenciaMotor['ALTA']),
    ctrl.Rule(Erro['GRD'] & DeltaErro['ZER'], PotenciaMotor['MEDIA']),
    ctrl.Rule(Erro['GRD'] & DeltaErro['POS'], PotenciaMotor['MEDIA']),
]

# Criando o sistema fuzzy
sistema_controle = ctrl.ControlSystem(regras)
controle_fuzzy = ctrl.ControlSystemSimulation(sistema_controle)
