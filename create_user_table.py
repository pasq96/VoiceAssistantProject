# Inizialize user tables
import json
import os

os.chdir("Z:\Drive condivisi\Tesi\File progetto")

users = [
    {"username": "pasquale", "type": "admin"}, 
    {"username": "carmine", "type": "admin"},
    {"username": "nicola", "type": "user"}
]

with open('users.json', 'w') as fout:
    json.dump(users, fout)