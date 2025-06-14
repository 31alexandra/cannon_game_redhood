# 1. Imposta prima la configurazione di Kivy 
from kivy.config import Config
from constants.screen_constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', str(SCREEN_WIDTH))
Config.set('graphics', 'height', str(SCREEN_HEIGHT))
Config.set('graphics', 'maxfps', str(FPS))
Config.write()

# 2. Ora importo Kivy e gli scrren
from kivy.app import App
from screens.screen_manager import ScreenManagement
from screens.story_screen import StoryScreen
from screens.start_screen import StartScreen
from functions.save_load import SaveLoadManager, reset_scores  


from screens.game_screen import GameScreen  


class RedhoodsBerryBlastApp(App):
    def build(self):
        reset_scores()  #Pulisce i vecchi punteggi all'avvio

        self.save_load = SaveLoadManager() 
        self.player_name = ""  # Aggiunto per memorizzare il nome del giocatore

        sm = ScreenManagement()

        sm.current = 'home'
        return sm

if __name__ == '__main__':
    RedhoodsBerryBlastApp().run()
