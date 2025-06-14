import sys 
import os 

from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder

from kivy.uix.label import Label
from kivy.uix.button import Button

from levels.cannon import CannonWidget
from projectiles.bullet import Bullet
from ui.projectile_settings import ProjectileSettingsBar
from functions.save_load import SaveLoadManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from functions.timer_widget import TimerWidget
from screens.timeup_popup import TimeUpPopup
from screens.congratulations import Congratulations
from datetime import datetime
from functions.save_load import saved_score

Builder.load_file("levels/level_1.kv")

class Level1Screen(Screen):
    def on_enter(self):
        self.timer = self.ids.timer_widget
        self.timer.on_timer_end_callback = self.on_timer_end  # IMPORTANTE!
        self.timer.level_name = "level_1"
        self.timer.target_type = "Crow"
        self.bullets_fired = 0
        self.timer.start()
        self.start_time = datetime.now()

        game_screen = self.manager.get_screen("game")
        game_screen.current_level = 1
        
        cannon = CannonWidget(pos=(100, 100), projectile_cls=Bullet, parent_widget=self)
        self.add_widget(cannon)
        cannon.parent_widget = self  # riferimento esplicito per restart 

        settings_bar = ProjectileSettingsBar(pos=(10, self.height - 130))
        self.add_widget(settings_bar)

        Clock.schedule_once(self.animate_crow_hover, 1)
    
    def animate_crow_hover(self, *args):
        crow = self.ids.crow
        original_y = crow.y
        anim = Animation(y=original_y + 15, duration=1) + Animation(y=original_y, duration=1)
        anim.repeat = True
        anim.start(crow)
    
    def on_help(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Image(source="resources/images/help_info.jpg"))

        popup = Popup(
            title="Help",
            content=layout,
            size_hint=(0.9, 0.9),
            auto_dismiss=True
        )
        popup.open()

    def update_timer(self, dt):
        self.current_time -= 1
        self.timer_label.text = f"Time: {int(self.current_time)}"
        if self.current_time <= 0:
            Clock.unschedule(self.timer_event)
            self.timer_label.text = "Time: 0"
            self.level_finished_popup()

    def level_finished_popup(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        replay_btn = Button(text="Replay", size_hint_y=None, height=40)
        menu_btn = Button(text="Menu", size_hint_y=None, height=40)

        layout.add_widget(replay_btn)
        layout.add_widget(menu_btn)

        popup = Popup(title="Time's Up!",
                      content=layout,
                      size_hint=(0.5, 0.4),
                      auto_dismiss=False)

        replay_btn.bind(on_release=lambda *args: self.replay_level(popup))
        menu_btn.bind(on_release=lambda *args: self.go_to_menu(popup))

        popup.open()

    def on_timer_end(self):
        time_taken = 60 - self.timer.current_time
        saved_score("level_1", "Crow", time_taken, self.bullets_fired)

        popup = TimeUpPopup(level_name="level1")
        popup.manager = self.manager
        popup.open()
    
    def reset_level(self):
        #Logica per rimuovere oggetti creati, ripristinare lo stato iniziale
        self.clear_widgets()
        self.bullets_fired = 0
        self.__init__()  
        self.on_enter()