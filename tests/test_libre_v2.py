import os
from dotenv import load_dotenv

from pylibrelinkup import PyLibreLinkUp  # classe correta da lib


def print_separator(title: str):
    print("\n" + "=" * 20 + f" {title} " + "=" * 20 + "\n")


def main():
    load_dotenv()
    email = os.getenv("LIBRE_EMAIL")
    password = os.getenv("LIBRE_PASSWORD")

    if not email or not password:
        print("ERRO: configure LIBRE_EMAIL e LIBRE_PASSWORD no .env")
        return

    print_separator("Login no LibreLinkUp")
    client = PyLibreLinkUp(email=email, password=password)
    client.authenticate()
    print("✅ Autenticado com sucesso.\n")

    print_separator("Lista de pacientes")
    patients = client.get_patients()
    print(f"Qtd de pacientes retornados: {len(patients)}")
    print("Lista bruta (repr):")
    for i, p in enumerate(patients):
        print(f"{i}: {p!r}")

    if not patients:
        print("Nenhum paciente encontrado.")
        return

    patient = patients[0]

    print_separator("Inspecionando o primeiro paciente")
    print("type(patient):", type(patient))
    # tentar inspecionar atributos "não mágicos"
    attrs = {}
    for name in dir(patient):
        if name.startswith("_"):
            continue
        try:
            value = getattr(patient, name)
        except Exception:
            continue
        if callable(value):
            continue
        attrs[name] = value

    print("Atributos do paciente (nome -> valor):")
    for k, v in attrs.items():
        print(f" - {k}: {v!r}")

    # Vamos tentar adivinhar um identificador estável (uuid)
    possible_keys = ["id", "identifier", "patient_id", "patientId", "uuid"]
    patient_id_value = None
    for key in possible_keys:
        if key in attrs:
            patient_id_value = attrs[key]
            break

    print("\nPossível identificador (uuid) do paciente:", repr(patient_id_value))

    print_separator("Última glicemia (latest)")
    latest = client.latest(patient_identifier=patient)
    # latest normalmente também é um objeto (Measurement)
    print("type(latest):", type(latest))
    latest_attrs = {}
    for name in dir(latest):
        if name.startswith("_"):
            continue
        try:
            value = getattr(latest, name)
        except Exception:
            continue
        if callable(value):
            continue
        latest_attrs[name] = value

    print("Atributos da última leitura:")
    for k, v in latest_attrs.items():
        print(f" - {k}: {v!r}")

    print_separator("Histórico recente (graph)")
    graph_data = client.graph(patient_identifier=patient)
    print(f"Total de medições no graph: {len(graph_data)}")

    if graph_data:
        print("\nPrimeiras 5 medições (campos principais):")
        for m in graph_data[:5]:
            # pegar atributos comuns
            try:
                value = getattr(m, "value", None)
                timestamp = getattr(m, "timestamp", None)
                factory_ts = getattr(m, "factory_timestamp", None)
            except Exception:
                value = timestamp = factory_ts = None

            print(f"- value={value!r} | timestamp={timestamp!r} | factory_timestamp={factory_ts!r}")

        # se quiser ver os atributos crus da primeira medição:
        m0 = graph_data[0]
        print_separator("Atributos completos da primeira medição (graph[0])")
        m0_attrs = {}
        for name in dir(m0):
            if name.startswith("_"):
                continue
            try:
                value = getattr(m0, name)
            except Exception:
                continue
            if callable(value):
                continue
            m0_attrs[name] = value

        for k, v in m0_attrs.items():
            print(f" - {k}: {v!r}")
    else:
        print("Nenhuma medição retornada em graph().")


if __name__ == "__main__":
    main()