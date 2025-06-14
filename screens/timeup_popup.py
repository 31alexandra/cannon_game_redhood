# screens/timeup_popup.py

from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.app import App

Builder.load_file("screens/timeup_popup.kv")

class TimeUpPopup(Popup):
    manager = ObjectProperty(None)  # Reference to the screen manager
    
    def __init__(self, level_name, **kwargs):
        super().__init__(**kwargs)
        self.level_name = level_name
        self.title = f"Level {level_name[-1]} Complete!"
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = False

    def on_replay(self):
        if self.manager:
            level_screen = self.manager.get_screen(self.level_name)
            if level_screen:
                level_screen.reset_level()
        self.dismiss()
        
    def on_menu(self):
        self.dismiss()
        if self.manager:
            self.manager.current = 'menu'