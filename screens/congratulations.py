from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from functions.hall_of_fame import HallOfFamePopup 

Builder.load_file('screens/congratulations.kv')

class Congratulations(Popup):
    time_taken = NumericProperty(0)
    bullets_fired = NumericProperty(0)
    player_name = StringProperty("")

    def __init__(self, time_taken=0, bullets_fired=0, player_name="", **kwargs):
        super().__init__(**kwargs)
        self.time_taken = time_taken
        self.bullets_fired = bullets_fired
        self.player_name = player_name

    def on_next_level(self):
        App.get_running_app().root.current = 'game'  # Cambia schermata
        self.dismiss()  # Chiude il popup

    def on_hall_of_fame(self):
        popup = HallOfFamePopup()
        popup.populate_scores()
        popup.open()
