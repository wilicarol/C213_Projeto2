import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

erro_range = np.arange(0, 28.1, 0.1)
deltaerro_range = np.arange(-10, 10.1, 0.1)
potencia_range = np.arange(0, 1.01, 0.01)

Erro = ctrl.Antecedent(erro_range, 'Erro')
DeltaErro = ctrl.Antecedent(deltaerro_range, 'DeltaErro')
PotenciaMotor = ctrl.Consequent(potencia_range, 'PotenciaMotor')

Erro['P'] = fuzz.trapmf(Erro.universe, [0, 0, 4, 8])
Erro['M'] = fuzz.trimf(Erro.universe, [6, 14, 20])
Erro['G'] = fuzz.trapmf(Erro.universe, [18, 22, 28, 28])

DeltaErro['N'] = fuzz.trapmf(DeltaErro.universe, [-10, -10, -3, -1])
DeltaErro['ZE'] = fuzz.trimf(DeltaErro.universe, [-2, 0, 2])
DeltaErro['P'] = fuzz.trapmf(DeltaErro.universe, [1, 3, 10, 10])

PotenciaMotor['B'] = fuzz.trimf(PotenciaMotor.universe, [0.0, 0.15, 0.3])
PotenciaMotor['M'] = fuzz.trimf(PotenciaMotor.universe, [0.25, 0.5, 0.75])
PotenciaMotor['A'] = fuzz.trimf(PotenciaMotor.universe, [0.6, 0.85, 1.0])

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

def novo_controlador_fuzzy():
    sistema = ctrl.ControlSystem(regras)
    return ctrl.ControlSystemSimulation(sistema)
