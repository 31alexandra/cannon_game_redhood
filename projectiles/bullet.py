import os
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from random import choice
from math import sin, cos, radians

from projectiles.explosion import ExplosionEffect
from projectiles.projectile_info import get_bullet_mass, get_bullet_radius

from screens.congratulations import Congratulations
from obstacles.rock import RockGroup
from obstacles.perpetio import PerpetioGroup
from functions.hall_of_fame import save_score
from datetime import datetime


def find_rockgroups(widget):
    rockgroups = []
    if isinstance(widget, RockGroup):
        rockgroups.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            rockgroups.extend(find_rockgroups(child))
    return rockgroups


def find_perpetiogroups(widget):
    perpetios = []
    if isinstance(widget, PerpetioGroup):
        perpetios.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            perpetios.extend(find_perpetiogroups(child))
    return perpetios


def find_crows(widget):
    crows = []
    if isinstance(widget, Image):
        filename = os.path.basename(widget.source).lower()
        if "crow.png" in filename:
            crows.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            crows.extend(find_crows(child))
    return crows


class Bullet(Image):
    angle = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    gravity = NumericProperty(-50)
    damage_radius = NumericProperty(0)
    source = StringProperty("")

    def __init__(self, angle, parent_widget=None, **kwargs):
        super().__init__(**kwargs)
        
        self.angle = angle
        self.parent_widget = parent_widget  # per conteggio bullets_fired
        
        self.source = choice([
            "resources/images/redberry.png",
            "resources/images/blueberry.png"
        ])
        self.size_hint = (None, None)
        self.size = (25, 25)

        mass = get_bullet_mass()
        initial_speed = 80 + (mass - 1) * 60
        angle_rad = radians(angle)

        self.velocity_x = initial_speed * cos(angle_rad)
        self.velocity_y = initial_speed * sin(angle_rad)

        self.damage_radius = get_bullet_radius()

        # Incrementa il conteggio proiettili sparati
        #if self.parent_widget and hasattr(self.parent_widget, "bullets_fired"):
        #   self.parent_widget.bullets_fired += 1

        Clock.schedule_interval(self.move, 1 / 60)
    
    def move(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += self.gravity * dt

        self.check_collision()

        if self.y < 0 or self.x < 0 or self.x > Window.width:
            self.remove_bullet()

    def check_collision(self):
        if not self.parent:
            return

        bullet_center_global = self.to_window(*self.center)

        # Collisione con RockGroup
        for rockgroup in find_rockgroups(self.parent):
            for rock in rockgroup.children[:]:
                rock_center = rock.to_window(*rock.center)
                dx = bullet_center_global[0] - rock_center[0]
                dy = bullet_center_global[1] - rock_center[1]
                distance = (dx**2 + dy**2)**0.5

                if distance <= self.damage_radius:
                    explosion = ExplosionEffect(center=self.center)
                    self.parent.add_widget(explosion)
                    rockgroup.remove_widget(rock)
                    # Salva punteggio
                    self._save_score("RockGroup")
                    self.remove_bullet()
                    return

        # Collisione con Crow
        for crow in find_crows(self.get_root_window()):
            crow_center = crow.to_window(*crow.center)
            dx = bullet_center_global[0] - crow_center[0]
            dy = bullet_center_global[1] - crow_center[1]
            distance = (dx**2 + dy**2)**0.5

            if distance <= self.damage_radius:
                print("→ CROW COLPITO!")
                explosion = ExplosionEffect(center=crow.center)
                self.parent.add_widget(explosion)

                if crow.parent:
                    crow.parent.remove_widget(crow)

                from functions.timer_widget import TimerWidget
                def find_timer_widget(widget):
                    if isinstance(widget, TimerWidget):
                        return widget
                    if hasattr(widget, "children"):
                        for child in widget.children:
                            found = find_timer_widget(child)
                            if found:
                                return found
                    return None

                timer_widget = find_timer_widget(self.get_root_window())
                if timer_widget:
                    timer_widget.level_completed()

                # Salva punteggio e tempo in Hall of Fame
                self._save_score("Crow", timer_widget)

                popup = Congratulations()
                popup.open()
                self.remove_bullet()
                return

        # Collisione con Perpetio
        for perpetio_group in find_perpetiogroups(self.parent):
            for block in perpetio_group.children[:]:
                block_center = block.to_window(*block.center)
                dx = bullet_center_global[0] - block_center[0]
                dy = bullet_center_global[1] - block_center[1]
                distance = (dx**2 + dy**2)**0.5

                if distance <= self.damage_radius:
                    explosion = ExplosionEffect(center=self.center)
                    self.parent.add_widget(explosion)
                    # Salva punteggio
                    self._save_score("Perpetio")
                    self.remove_bullet()
                    return

    def _save_score(self, target_type, timer_widget=None):
        if target_type == "RockGroup":
            return  # Non salvare i colpi sulle rocce!
        bullets_fired = 0
        time_taken = None

        if self.parent_widget and hasattr(self.parent_widget, "bullets_fired"):
            bullets_fired = self.parent_widget.bullets_fired

        if timer_widget and hasattr(timer_widget, 'time_elapsed'):
            time_taken = timer_widget.time_elapsed

        save_score("Player", target_type, time_taken, bullets_fired)

    def remove_bullet(self):
        if self.parent:
            self.parent.remove_widget(self)
        Clock.unschedule(self.move)
