from pathlib import Path

def format_decision(sequence):
    if sequence[0] == 0:
        command = "SETMODE 10"
    else:
        command = "SETMODE 12"
    return command


def write_decision(client_dir: str, sequence: list):
    command = format_decision(sequence)

    # Convertir client_dir en Path et construire le chemin vers decision.txt
    client_path = Path(client_dir)
    decision_file = client_path / "decisions.txt"

    # Écrire la commande dans le fichier
    decision_file.write_text(command, encoding="utf-8")
