import os
import json
from datetime import datetime

from dotenv import load_dotenv

# IMPORTANTE: o nome pode ser LibreLinkUpClient ou similar.
# Se der ImportError, manda o erro que a gente ajusta.
from pylibrelinkup import PyLibreLinkUp


def pretty_print(title, data, max_chars=800):
    print(f"\n=== {title} ===")
    text = json.dumps(data, indent=2, ensure_ascii=False, default=str)
    if len(text) > max_chars:
        print(text[:max_chars] + "\n... [truncado]")
    else:
        print(text)


def main():
    # 1) carregar variáveis do .env
    load_dotenv()
    email = os.getenv("LIBRE_EMAIL")
    password = os.getenv("LIBRE_PASSWORD")

    if not email or not password:
        print("ERRO: configure LIBRE_EMAIL e LIBRE_PASSWORD no arquivo .env")
        return

    print("Iniciando login no LibreLinkUp...")
    client = PyLibreLinkUp(email=email, password=password)
    client.authenticate()
    print("✅ Login realizado com sucesso.\n")

    # 2) listar pacientes / conexões
    print("Buscando pacientes/conexões visíveis para esta conta...")
    patients = client.get_patients()
    pretty_print("RAW patients response", patients)

    if not patients:
        print("\nNenhum paciente encontrado. Confere no app se essa conta enxerga alguém.")
        return

    # 3) escolher o primeiro paciente
    first = patients[0]
    print("\nPrimeiro paciente retornado:")

    # aqui não sabemos ainda o formato exato, vamos imprimir:
    pretty_print("Primeiro paciente (detalhado)", first, max_chars=1200)

    # tentar adivinhar o ID que será usado nas próximas chamadas
    possible_keys = ["id", "patientId", "patientId", "patId", "deviceId"]
    libre_patient_id = None
    for key in possible_keys:
        if key in first:
            libre_patient_id = first[key]
            break

    print(f"\nTentando descobrir ID do paciente. Possível ID encontrado: {libre_patient_id!r}")

    if not libre_patient_id:
        print("❌ Não consegui identificar o campo de ID do paciente. Vamos precisar olhar o JSON e decidir juntos.")
        return

    # 4) buscar dados de glicose deste paciente
    print(f"\nBuscando dados de glicose para o paciente ID={libre_patient_id} ...")

    # NOME DO MÉTODO: isso varia de versão pra versão.
    # Vamos tentar alguns nomes comuns:
    readings = None
    errors = []

    for method_name in [
        "get_patient_glucose_data",
        "get_patient_readings",
        "get_graph_data",
        "get_patient_measurements",
    ]:
        try:
            method = getattr(client, method_name, None)
            if method is None:
                continue
            print(f"Tentando método: client.{method_name}({libre_patient_id!r})")
            result = method(libre_patient_id)
            readings = result
            print(f"✅ Método {method_name} funcionou.")
            break
        except Exception as e:
            errors.append(f"{method_name}: {e}")

    if readings is None:
        print("\n❌ Nenhum dos métodos testados funcionou. Erros:")
        for e in errors:
            print(" -", e)
        print("\nPrecisamos olhar a documentação ou o código da lib para ver qual é o método correto.")
        return

    pretty_print("RAW glucose readings", readings, max_chars=2000)

    # Se for uma lista de leituras, mostrar só as primeiras 3 de forma mais amigável
    if isinstance(readings, list) and readings:
        print("\nAlgumas leituras simplificadas:")
        for item in readings[:3]:
            ts = item.get("timestamp") or item.get("DeviceTimestamp") or item.get("ValueInSeconds")
            val = item.get("value") or item.get("Value") or item.get("GlucoseValue")
            print(f"- ts={ts} | glucose={val}")
    else:
        print("\nLeituras não estão em formato de lista, ver JSON completo acima.")


if __name__ == "__main__":
    main()