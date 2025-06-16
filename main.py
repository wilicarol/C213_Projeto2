import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# erro
Erro = ctrl.Antecedent(np.arange(-12.0, 12.1, 0.1), label='Erro')
Erro.membershipA = 'E'
Erro.unit = 'm'

Erro['N'] = fuzz.trapmf(Erro.universe, [-12, -12, -4, -2])
Erro['ZE'] = fuzz.trimf(Erro.universe, [-3, 0, 3])
Erro['P'] = fuzz.trapmf(Erro.universe, [2, 4, 12, 12])

Erro.view()
[plt.gca().lines[i].set_linewidth(2) for i in range(len(plt.gca().lines))]
fig = plt.gcf(); axes = fig.gca(); fig.set_size_inches(6, 2)
axes.set_xlabel(xlabel=f'{Erro.label} [{Erro.unit}]')
axes.set_ylabel(ylabel=f'Pertinência $\mu_{Erro.membershipA}$')
axes.set_xticks(np.arange(-12, 13, 2))
plt.legend(loc='upper right')
plt.show()

# delta erro
DeltaErro = ctrl.Antecedent(np.arange(-1.0, 1.01, 0.01), label='DeltaErro')
DeltaErro.membershipA = 'DE'
DeltaErro.unit = 'm'

DeltaErro['N'] = fuzz.trapmf(DeltaErro.universe, [-1.0, -1.0, -0.3, -0.1]) #negativo
DeltaErro['ZE'] = fuzz.trimf(DeltaErro.universe, [-0.2, 0, 0.2]) #zero
DeltaErro['P'] = fuzz.trapmf(DeltaErro.universe, [0.1, 0.3, 1.0, 1.0]) #positivo

DeltaErro.view()
[plt.gca().lines[i].set_linewidth(2) for i in range(len(plt.gca().lines))]
fig = plt.gcf(); axes = fig.gca(); fig.set_size_inches(6, 2)
axes.set_xlabel(xlabel=f'{DeltaErro.label} [{DeltaErro.unit}]')
axes.set_ylabel(ylabel=f'Pertinência $\mu_{DeltaErro.membershipA}$')
axes.set_xticks(np.arange(-1, 1.1, 0.2))
plt.legend(loc='upper right')
plt.show()

# potencia motor
PotenciaMotor = ctrl.Consequent(np.arange(0, 1.01, 0.01), label='PotenciaMotor')
PotenciaMotor.membershipA = 'PM'
PotenciaMotor.unit = '%'

PotenciaMotor['inicial'] = fuzz.trimf(PotenciaMotor.universe, [0.30, 0.315, 0.33])
PotenciaMotor['baixa']   = fuzz.trimf(PotenciaMotor.universe, [0.20, 0.30, 0.40])
PotenciaMotor['media']   = fuzz.trimf(PotenciaMotor.universe, [0.40, 0.60, 0.75])
PotenciaMotor['alta']    = fuzz.trimf(PotenciaMotor.universe, [0.70, 0.85, 1.00])

PotenciaMotor.view()
[plt.gca().lines[i].set_linewidth(2) for i in range(len(plt.gca().lines))]
fig = plt.gcf(); axes = fig.gca(); fig.set_size_inches(6, 2)
axes.set_xlabel(xlabel=f'{PotenciaMotor.label} [{PotenciaMotor.unit}]')
axes.set_ylabel(ylabel=f'Pertinência $\mu_{PotenciaMotor.membershipA}$')
plt.legend(loc='upper right')
plt.show()
