import os  
import json
from datetime import datetime
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock 

Builder.load_file("functions/hall_of_fame.kv") 

def save_score(level_name, target_type, time_taken,  bullets_fired=0):
    if bullets_fired != 1:
        # Non salvare se non è il primo colpo
        return
     
    player_name = getattr(App.get_running_app(), 'player_name', 'Unknown')

    # Convert time_taken a string se non è numero
    if not isinstance(time_taken, (int, float)):
        time_taken = str(time_taken)

    record = {
        'player_name': player_name,
        'level': level_name,
        'target_type': target_type,
        'time_taken': time_taken,
        'timestamp': datetime.now().isoformat(),
        'bullets_fired': bullets_fired
    }

    if not os.path.exists('data'):
        os.makedirs('data')

    try:
        with open('data/scores.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(record)

    with open('data/scores.json', 'w') as f:
        json.dump(data, f, indent=2)

class HallOfFamePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Hall of Fame"
        self.size_hint = (0.8, 0.8)
        #box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        #self.content = box
        Clock.schedule_once(lambda dt: self.populate_scores(), 0)
        
    def populate_scores(self):
        scores_box = self.ids.scores_box
        scores_box.clear_widgets()

        try:
            with open('data/scores.json', 'r') as f:
                scores = json.load(f)
        except FileNotFoundError:
            scores = []

        # Filtra record che hanno almeno 'player_name' per sicurezza
        scores = [record for record in scores if 'player_name' in record]
        

        if not scores:
            scores_box.add_widget(Label(text="No scores yet!"))
        else:
            scores_sorted = sorted(scores, key=lambda x: (x['level'], x['time_taken']))
            for record in scores_sorted:
                text = (
                    f"Player: {record.get('player_name', 'Unknown')} — "
                    f"Level: {record.get('level', 'Unknown')} — "
                    f"Target: {record.get('target_type', 'Unknown')} — "
                    f"Time: {record.get('time_taken', 'Unknown')}s"
                )
                scores_box.add_widget(Label(
                    text=text,
                    size_hint_y=None,
                    height=30,
                    halign='center',
                    valign='middle',
                    text_size=(self.width, None)
                ))
def reset_scores():
    #Cancella il contenuto dei punteggi ogni volta che il gioco parte.
    if os.path.exists('data/scores.json'):
        with open('data/scores.json', 'w') as f:
            json.dump([], f) 