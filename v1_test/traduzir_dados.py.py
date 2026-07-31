import csv
import re

def traduzir_linha_controltech(texto_bruto):
    if "SEM_RESPOSTA" in texto_bruto or not texto_bruto:
        return None

    # Ancoragem estrita nas marcas do protocolo (ro...a...) para evitar descolamento de bytes
    padrao = r'ro(\d{4})a(\d{4})(\d{2})(\d{6})(\d{6})(\d)(\d)(\d)(\d{10})(\d{10})(\d{8})(\d{8})([A-Z0-9]{8})'
    
    match = re.search(padrao, texto_bruto, re.IGNORECASE)
    if not match:
        return None

    (pos, seq, bico, hora, data, vir_pu, vir_lt, preco, vol_str, tot_str, enc_str, enc_ini, tag) = match.groups()

    # Formatação de campos
    data_fmt = f"{data[0:2]}/{data[2:4]}/20{data[4:6]}"
    hora_fmt = f"{hora[0:2]}:{hora[2:4]}:{hora[4:6]}"
    
    vol_num = int(vol_str) / 1000.0
    tot_num = int(tot_str) / 100.0
    enc_num = int(enc_str) / 100.0

    return {
        "Posicao": int(pos),
        "Bico": int(bico),
        "Data_Hora": f"{data_fmt} {hora_fmt}",
        "Vir_PU": vir_pu,
        "Vir_LT": vir_lt,
        "Preco": preco,
        "Volume_L": f"{vol_num:.3f}".replace('.', ','),
        "Total_R$": f"{tot_num:.2f}".replace('.', ','),
        "Encerrante": f"{enc_num:.2f}".replace('.', ','),
        "ID_Cartao_Tag": tag,
        "String_Bruta": texto_bruto
    }

def processar_csv():
    arquivo_entrada = "abastecimentos_salvos.csv"
    arquivo_saida = "abastecimentos_corrigidos.csv"

    dados_processados = []

    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f_in:
            leitor = csv.reader(f_in, delimiter=";")
            next(leitor, None)

            for linha in leitor:
                if len(linha) >= 2:
                    res = traduzir_linha_controltech(linha[1])
                    if res:
                        dados_processados.append(res)

        colunas = [
            "Posicao", "Bico", "Data_Hora", "Vir_PU", "Vir_LT", 
            "Preco", "Volume_L", "Total_R$", "Encerrante", "ID_Cartao_Tag", "String_Bruta"
        ]

        with open(arquivo_saida, "w", encoding="utf-8-sig", newline="") as f_out:
            escritor = csv.DictWriter(f_out, fieldnames=colunas, delimiter=";")
            escritor.writeheader()
            escritor.writerows(dados_processados)

        print(f"✅ Processamento concluído! Arquivo gerado: '{arquivo_saida}'")

    except FileNotFoundError:
        print(f"❌ Arquivo '{arquivo_entrada}' não encontrado.")

if __name__ == "__main__":
    processar_csv()
