from pathlib import Path

def format_decision(sequence):
    if sequence[0] == 0:
        command = "SETMODE 10"
    else:
        command = "SETMODE 12"
    return command




