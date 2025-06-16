#  Simulador de Elevador com Controle Fuzzy PD 🛗  
**Disciplina: Sistemas Embarcados**

Este projeto simula o comportamento de um elevador real utilizando controle fuzzy PD e comunicação MQTT. Inclui uma interface gráfica interativa inspirada em painéis reais e modelagem física baseada em dados de um elevador comercial.

---

##  Estrutura do Edifício 🧱

- **Total de andares:** 11  
- **Altura total:** 36 m  

| Tipo de Andar        | Quantidade | Altura por andar | Observações                    |
|----------------------|------------|------------------|--------------------------------|
| Subsolo              | 1          | 4 m              | Acesso restrito com senha      |
| Térreo (recepção)    | 1          | 4 m              | Acesso geral                   |
| Andares habitáveis   | 8          | 3 m              | Do 1º ao 8º andar              |
| Último andar (técnico)| 1         | 4 m              | -                               |

> Moradores têm acesso permitido **apenas do térreo ao 8º andar**.

---

##  Especificações do Elevador 🔢

- **Modelo:** Villarta Standard COMPAQ Slim  
- **Capacidade:** 13 passageiros (975 kg máx.)  

| Velocidade (m/s) | Potência (%) | Percurso Máximo (m) |
|------------------|--------------|----------------------|
| 0.35             | 31.5         | 9                    |
| 0.50             | 45.0         | 15                   |
| 1.00             | 90.0         | 21                   |

- A velocidade é **diretamente proporcional à potência aplicada no motor**.
- O motor possui uma **fase de inicialização linear de 2 segundos**, atingindo 31.5% da potência nominal.

---

##  Modelo Matemático 🧾

### Modelo de recursão (inicialização):
```
posiçãoAtual = k1 * posiçãoAtual * 0.999 + potenciaMotor * 0.251287
```

### Modelo de controle fuzzy (com defuzzificação):
```
posiçãoAtual = k1 * posiçãoAtual * 0.9995 +  potenciaMotor * 0.212312
```

- `k1` = +1 (subida) ou −1 (descida)  
- `potenciaMotor` ∈ [0, 1]  
- Valores baseados em ajuste experimental com `k2` ≈ 0.212312  

---

##  Controle Fuzzy PD 🎯

Sistema **MISO** (Multiple Input, Single Output), com:

- **Entradas:**
  - `erro` → diferença entre posição desejada (setpoint) e atual
  - `deltaErro` → variação do erro em cada ciclo

- **Saída:**
  - `potenciaMotor` → potência aplicada ao motor

---
