import pickle  # Per salvare e caricare dati in formato binario
import os  # Per operazioni sul file system come controllo esistenza file/cartelle
import json  # Per leggere e scrivere dati JSON (usati per i punteggi)
from datetime import datetime  # Per registrare il timestamp dei salvataggi

SAVE_FILE = "savegame.pkl"  # File dove vengono salvati gli stati di gioco con pickle
SCORES_FILE = "data/scores.json"  # File JSON dove vengono salvati i punteggi

class SaveLoadManager:
    def __init__(self):
        # Dizionario che tiene i dati di salvataggio caricati o da salvare
        self.save_data = {}

    def save_level_state(self, level_name, data):
        # Se il file di salvataggio esiste, lo carico per aggiornare i dati
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'rb') as f:
                self.save_data = pickle.load(f)
        # Aggiorno o aggiungo i dati del livello specificato
        self.save_data[level_name] = data
        # Scrivo i dati aggiornati sul file in formato binario
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(self.save_data, f)

    def load_level_state(self, level_name):
        # Se il file esiste, lo apro e carico i dati
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'rb') as f:
                self.save_data = pickle.load(f)
            # Ritorno i dati specifici del livello, o dizionario vuoto se non esiste
            return self.save_data.get(level_name, {})
        # Se non c'è file, ritorno dizionario vuoto
        return {}

    def clear_level_state(self, level_name):
        # Cancella i dati di un livello specifico dal file di salvataggio
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'rb') as f:
                self.save_data = pickle.load(f)
            # Se il livello è presente, lo rimuovo
            if level_name in self.save_data:
                del self.save_data[level_name]
                # Riscrivo il file con i dati aggiornati
                with open(SAVE_FILE, 'wb') as f:
                    pickle.dump(self.save_data, f)

    def get_total_time(self):
        # Calcola il tempo totale sommando il campo 'time_taken' di tutti i livelli salvati
        total = 0
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'rb') as f:
                self.save_data = pickle.load(f)
            for level_data in self.save_data.values():
                total += level_data.get('time_taken', 0)
        return total

def reset_scores():
    # Reimposta la Hall of Fame cancellando tutti i punteggi (scrivendo lista vuota)
    os.makedirs('data', exist_ok=True)  # Crea cartella 'data' se non esiste
    with open(SCORES_FILE, 'w') as f:
        json.dump([], f)  # Scrive una lista vuota nel file punteggi

def saved_score(player_name, level_name, target_type, time_taken):
    # Salva un nuovo punteggio nella Hall of Fame solo se non esiste già per quel giocatore e livello
    os.makedirs('data', exist_ok=True)  # Assicura che la cartella esista
    # Crea il record punteggio con i dati forniti e timestamp attuale
    record = {
        'player_name': player_name,
        'level': level_name,
        'target_type': target_type,
        'time_taken': time_taken,
        'timestamp': datetime.now().isoformat()
    }
    try:
        # Prova a caricare i punteggi esistenti dal file JSON
        with open(SCORES_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        # Se il file non esiste ancora, inizializza una lista vuota
        data = []
    # Controlla se c'è già un punteggio per quel giocatore e livello
    already_exists = any(
        r['player_name'] == player_name and r['level'] == level_name
        for r in data
    )
    # Se non esiste già, aggiunge il nuovo punteggio e riscrive il file JSON
    if not already_exists:
        data.append(record)
        with open(SCORES_FILE, 'w') as f:
            json.dump(data, f, indent=2)  # Salva in formato leggibile con indentazione
