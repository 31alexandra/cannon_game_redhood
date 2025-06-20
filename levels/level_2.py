from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.clock import Clock
from ui.projectile_settings import ProjectileSettingsBar

from kivy.lang import Builder
from kivy.uix.button import Button

from functions.save_load import SaveLoadManager

from functions.timer_widget import TimerWidget
from screens.timeup_popup import TimeUpPopup

from levels.cannon import CannonWidget
from datetime import datetime
from obstacles.elastonio import ElastonioBar
from projectiles.bombshell import Bombshell
from functions.save_load import saved_score

Builder.load_file("levels/level_2.kv")

class Level2Screen(Screen):

    

    def on_enter(self):
        self.timer = self.ids.timer_widget
        self.timer.on_timer_end_callback = self.on_timer_end  # IMPORTANTE!
        self.timer.level_name = "level2"
        self.timer.target_type = "Snake"
        self.bullets_fired = 0
        self.timer.start()
        self.start_time = datetime.now()
        game_screen = self.manager.get_screen("game")
        game_screen.current_level = 2 
        
        # Aggiungi il cannone nella scena
        cannon = CannonWidget(pos=(100, 100), projectile_cls=Bombshell, parent_widget=self)
        self.add_widget(cannon)
        cannon.parent_widget = self # salva riferimento esplicito per quando devo fare il restart 
        
        # Aggiungi barra dei controlli
        settings_bar = ProjectileSettingsBar(pos=(10, self.height - 130))
        self.add_widget(settings_bar)

        # Avvia animazione del serpente 
        Clock.schedule_once(self.animate_snake_hover, 1)

            
    def animate_snake_hover(self, *args):
        snake = self.ids.snake
        original_x = snake.x
        self.snake_anim = Animation(x=original_x + 30, duration=1) + Animation(x=original_x, duration=1)
        self.snake_anim.repeat = True
        self.snake_anim.start(snake)
    
    def on_help(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Image(source="resources/images/help_info2.jpg"))

        popup = Popup(
            title="Help",
            content=layout,
            size_hint=(0.9, 0.9),
            auto_dismiss=True
        )
        popup.open()

    def setup_level(self):
        elastonio = ElastonioBar()
        elastonio.pos = (100, 100)  # posizione nel livello
        self.add_widget(elastonio)

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
        saved_score("level_2", "Snake", time_taken, self.bullets_fired)
        #SaveLoadManager().save_level_state("level2", {"time_taken": time_taken})
        
        popup = TimeUpPopup(level_name="level2")
        popup.manager = self.manager
        popup.open()

    def reset_level(self):
        #Logica per rimuovere oggetti creati, ripristinare lo stato iniziale
        self.clear_widgets()
        self.__init__()  
        self.on_enter()