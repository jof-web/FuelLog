Este repositório contém uma solução em Python desenvolvida para **recuperar e reconstruir dados operacionais críticos** de um concentrador/controlador de abastecimento industrial através de comunicação serial direta (RS-232/RS-485).

A solução foi projetada para resolver um cenário de falha física onde o software proprietário do fabricante travava ao tentar ler posições de memória RAM corrompidas na placa do dispositivo.

---

## 📌 O Problema e o Cenário Operacional

Durante a operação de uma planta industrial de combustível, a placa controladora acumulou mais de 1.000 registros de transações de abastecimento na memória RAM interna. Devido a uma instabilidade de hardware e oscilação de tensão, blocos específicos da memória foram corrompidos física/logicamente.

### Riscos e Desafios:

1. **Travamento de Software:** O software oficial de gestão do equipamento dependia de uma comunicação serial perfeita. Ao atingir o registro corrompido, o programa recebia ruído (*lixo serial*) e entrava em *loop/crash*, interrompendo a extração.
2. **Inacessibilidade dos Dados:** Impossibilidade de descarregar os relatórios operacionais pelos meios convencionais.
3. **Risco Financeiro:** A perda desses registros significava uma inconsistência contábil e de estoque superior a **R$ 15.000**, além dos custos e prazos de substituição física da placa pela assistência técnica.

---

## 🔬 A Investigação e Engenharia Reversa do Protocolo

Para contornar o software proprietário e comunicar diretamente com a porta COM do dispositivo, a estrutura de quadros de transmissão (frames ASCII) foi analisada no nível de pacote.

### 1. Estrutura da Mensagem (Payload Serial)

O protocolo opera em texto ASCII encapsulado por marcadores de bloco:

$$\text{\{HHHCMMMMCC\}}$$

* **`{` e `}**`: Delimitadores de início e fim da transmissão (*Start/End of Frame*).
* **`HHH`**: Endereço físico do nó concentrador na rede (ex: `104`).
* **`C`**: Instrução de comando (`R` para descarregar bloco de memória RAM).
* **`MMMM`**: Endereço de memória solicitado com 4 dígitos numéricos decimais (`0001` a `1200`).
* **`CC`**: *Checksum* de verificação de integridade de 2 dígitos em hexadecimal.

### 2. Validação por Checksum XOR

Diferente da soma de bytes convencional, o algoritmo de validação da placa utiliza **XOR (Ou Exclusivo)** sobre os valores ASCII de todos os caracteres contidos dentro das chaves do pacote:

$$\text{Checksum} = \bigoplus_{i=1}^{n} \text{ord}(\text{char}_i) \pmod{256}$$

### 3. Falhas do Protocolo Padrão vs. Solução

* **Delimitação de Linha:** O protocolo encerra as mensagens com `}` e não com quebras de linha padrão (`\n` ou `\r\n`). O uso de métodos padrões de leitura serial (`readline()`) causava *timeouts* constantes.
* **Leitura com Tolerância a Falhas:** A solução exigia o uso do método `read_until(b'}')` combinado com blocos `try/except` para ignorar os bytes corrompidos e prosseguir para os registros seguintes sem interromper o *batch loop*.

---

## ⚙️ A Solução (O Método)

A solução foi estruturada em dois scripts Python modulares:

### Pipeline da Solução:

```
[Placa Controladora] ──(RS-232 / 9600 8N1)──> [extrair_memoria.py] ──> (abastecimentos_salvos.csv)
                                                                               │
                                                                               ▼
[Relatório Excel + Tag RFID] <── (abastecimentos_corrigidos.csv) <── [traduzir_dados.py]

```

1. **`extrair_memoria.py`**: Conecta-se à porta COM ativa, gera dinamicamente as requisições com *Checksum XOR* correto, trata pacotes corrompidos sem derrubar o processo e salva os registros brutos em disco.
2. **`traduzir_dados.py`**: Processa a string bruta utilizando **Expressões Regulares (Regex) com Ancoragem Dupla** (`ro` e `a`), corrigindo o alinhamento de bytes e descompactando os dados em colunas estruturadas.

> **Achado Técnico Extra:** Além de recuperar 100% das posições válidas, o fatiamento por Regex permitiu extrair o **ID Hexadecimal da Tag/Cartão RFID (8 dígitos)** gravado na memória, um dado crítico que o software oficial do fabricante ocultava na interface do usuário.

---

## 💻 Código-Fonte

### 1. Extrator de Memória Serial (`extrair_memoria.py`)
### 2. Parser e Decodificador com RegEx Ancorado (`traduzir_dados.py`)

## 📈 Resultados e Impacto

* **Taxa de Recuperação de Dados:** 100% dos dados válidos recuperados com sucesso sem interromper a execução no bloco danificado.
* **Mitigação de Impacto:** Prevenção do prejuízo de R$ 15.000 em perdas operacionais/contábeis.
* **Enriquecimento de Dados:** Obtenção do ID da Tag RFID Hexadecimal diretamente do payload serial, permitindo rastreabilidade que a interface GUI original não entregava.

---

## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.12+
* **Comunicação Serial:** `pyserial`
* **Processamento e RegEx:** Módulos nativos `re` e `csv`
* **Protocolos:** RS-232 / RS-485 ASCII

---
