from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.lang import Builder
from functions.hall_of_fame import save_score
from kivy.properties import StringProperty
from functions.save_load import SaveLoadManager
from functions.save_load import saved_score
from kivy.app import App
Builder.load_file('functions/timer_widget.kv')

class TimerWidget(BoxLayout):
    current_time = NumericProperty(60)
    running = BooleanProperty(False)
    level_name = StringProperty("")
    target_type = StringProperty("")
    on_timer_end_callback = None 

    def start(self):
        self.current_time = 60
        self.running = True
        Clock.schedule_interval(self.update_time, 1)

    def stop(self):
        self.running = False
        Clock.unschedule(self.update_time)

    def update_time(self, dt):
        if self.running:
            self.current_time -= 1
            if self.current_time <= 0:
                self.stop()
                if self.on_timer_end_callback:
                    self.on_timer_end_callback()

    def level_completed(self):
        self.stop()
        time_taken = 60 - self.current_time
        player_name = getattr(App.get_running_app(), 'player_name', 'Unknown')
        if self.level_name and self.target_type and player_name:
            saved_score(player_name, self.level_name, self.target_type, time_taken)
        SaveLoadManager().save_level_state(self.level_name, {
            "time_taken": round(time_taken, 2),
            "target": self.target_type
        })
    
    @property
    def time_elapsed (self):
        return 60 - self.current_time
