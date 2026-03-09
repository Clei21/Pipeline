import json
import base64
import os


def salvar_imagem_base64(base64_str, nome_arquivo):
    if "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]

    try:
        img_data = base64.b64decode(base64_str)
    except Exception as e:
        print(f"Erro ao decodificar base64: {e}")
        return

    with open(nome_arquivo, "wb") as f:
        f.write(img_data)


def buscar_base64(data, pasta_saida, prefixo="img", contador=[0]):
    if isinstance(data, dict):
        for chave, valor in data.items():

            if chave.lower() == "imagem" and isinstance(valor, str):
                nome_img = os.path.join(
                    pasta_saida, f"{prefixo}_{contador[0]}.png"
                )
                salvar_imagem_base64(valor, nome_img)
                print(f"Imagem salva: {nome_img}")
                contador[0] += 1

            buscar_base64(valor, pasta_saida, prefixo, contador)

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            buscar_base64(item, pasta_saida, f"{prefixo}_{idx}", contador)


def extrair_imagens_do_json(caminho_json, pasta_saida="imagens_extraidas"):
    os.makedirs(pasta_saida, exist_ok=True)

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    buscar_base64(dados, pasta_saida)

    print("Processo finalizado.")


caminho_json = (
    r"C:/Users/cleid/OneDrive/Documentos/BaseDados/json_saida/"
    r"9- PCE-ENPP-3-135.json"
)
extrair_imagens_do_json(caminho_json)