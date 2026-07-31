import serial
import serial.tools.list_ports
import time

def listar_portas_com():
    portas = serial.tools.list_ports.comports()
    if not portas:
        print("❌ Nenhuma porta COM encontrada!")
        return None
    
    print("\n--- PORTAS SERIAL ENCONTRADAS ---")
    for idx, porta in enumerate(portas):
        print(f"[{idx}] {porta.device} - {porta.description}")
    
    entrada = input("\nDigite o índice [ex: 0] ou a porta [ex: COM14]: ").strip().upper()
    if entrada.isdigit() and int(entrada) < len(portas):
        return portas[int(entrada)].device
    for porta in portas:
        if porta.device.upper() == entrada or porta.device.upper() == f"COM{entrada}":
            return porta.device
    return None

def calcular_checksum_xor(payload):
    """Calcula o Checksum exato da placa usando XOR (HEX 2 dígitos)"""
    xor_val = 0
    for char in payload:
        xor_val ^= ord(char)
    return f"{xor_val:02X}"

def criar_comando(endereco, comando, posicao):
    """Monta a string do protocolo: {104R000166}"""
    pos_str = f"{posicao:04d}"
    payload = f"{endereco}{comando}{pos_str}"
    chk = calcular_checksum_xor(payload)
    return f"{{{payload}{chk}}}"

def executar_extracao():
    porta_com = listar_portas_com()
    if not porta_com:
        return

    ser = serial.Serial(
        port=porta_com,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.5
    )

    endereco = "104"
    comando = "R"  # Comando de leitura de memória RAM
    posicao_inicial = 1
    posicao_final = 1200

    nome_arquivo = "abastecimentos_salvos.csv"
    print(f"\nConectado à {porta_com}. Extraindo registros {posicao_inicial} até {posicao_final}...\n")

    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("Posicao;Dados_Brutos\n")

        for pos in range(posicao_inicial, posicao_final + 1):
            cmd_str = criar_comando(endereco, comando, pos)
            ser.reset_input_buffer()
            ser.write(cmd_str.encode('ascii'))
            time.sleep(0.1)

            # Leitura delimitada pelo caractere de fechamento '}'
            resposta_bytes = ser.read_until(b'}')
            resposta_texto = resposta_bytes.decode('ascii', errors='ignore').strip()

            if not resposta_texto or "{" not in resposta_texto:
                print(f"⚠️ Posição {pos:04d}: Sem resposta/Corrompido. Ignorando...")
                f.write(f"{pos:04d};SEM_RESPOSTA\n")
            else:
                print(f"✅ Posição {pos:04d}: {resposta_texto}")
                f.write(f"{pos:04d};{resposta_texto}\n")

    ser.close()
    print(f"\n Processo finalizado! Dados brutos salvos em '{nome_arquivo}'.")

if __name__ == "__main__":
    executar_extracao()
