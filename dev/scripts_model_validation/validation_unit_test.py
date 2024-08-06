"""
Script de test de validité d'une seule instance de box avec le modèle pydantic

Usage: python3 validation_unit_test.py <filename>
"""

import sys

from hermes.mongodb.models import Box

if len(sys.argv) != 2:
    print("Veuillez fournir un nom de fichier en argument.")
    print("Usage: python3 validation_unit_test.py <filename>")
    sys.exit(1)

filename = sys.argv[1]
try:
    with open(filename, "r", encoding="utf-8") as f:
        data = f.read()
        Box.model_validate_json(data)
    print(f"Le fichier {filename} contient une instance valide de box.")
except FileNotFoundError:
    print(f"Le fichier {filename} n'existe pas.")
except Exception as e:
    print(f"Erreur lors de la validation de l'instance contenue dans {filename}: {e}")
