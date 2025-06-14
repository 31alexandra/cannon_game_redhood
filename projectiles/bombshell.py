import os
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from random import choice
from math import hypot,sin, cos, radians
from kivy.app import App

from projectiles.explosion import ExplosionEffect
from projectiles.projectile_info import get_bullet_mass, get_bullet_radius

from obstacles.rock import RockGroup
from obstacles.elastonio import ElastonioBar
from screens.congratulations import Congratulations
from functions.hall_of_fame import  HallOfFamePopup, save_score
from functions.timer_widget import TimerWidget


def point_segment_distance(px, py, x1, y1, x2, y2):
    l2 = (x2 - x1)**2 + (y2 - y1)**2
    if l2 == 0:
        return hypot(px - x1, py - y1)
    t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2
    t = max(0, min(1, t))
    proj_x = x1 + t * (x2 - x1)
    proj_y = y1 + t * (y2 - y1)
    return hypot(px - proj_x, py - proj_y)

def find_rockgroups(widget):
    rockgroups = []
    if isinstance(widget, RockGroup):
        rockgroups.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            rockgroups.extend(find_rockgroups(child))
    return rockgroups

def find_elastonios(widget):
    elastonios = []
    if isinstance(widget, ElastonioBar):
        elastonios.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            elastonios.extend(find_elastonios(child))
    return elastonios


def find_snakes(widget):
    snakes = []
    if isinstance(widget, Image):
        filename = os.path.basename(widget.source).lower()
        if "snake.png" in filename:
            snakes.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            snakes.extend(find_snakes(child))
    return snakes


class Bombshell(Image):
    angle = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    gravity = NumericProperty(-50)
    damage_radius = NumericProperty(0)
    source = StringProperty("")

    def __init__(self, angle, parent_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.angle = angle
        self.parent_widget = parent_widget

        self.source = choice([
            "resources/images/cupcake.png"
        ])
        self.size_hint = (None, None)
        self.size = (25, 25)

        mass = get_bullet_mass()
        initial_speed = 80 + (mass - 1) * 60
        angle_rad = radians(angle)

        self.velocity_x = initial_speed * cos(angle_rad)
        self.velocity_y = initial_speed * sin(angle_rad)

        self.damage_radius = get_bullet_radius()

        if self.parent_widget and hasattr(self.parent_widget, "bullets_fired"):
            self.parent_widget.bullets_fired += 1

        #Clock.schedule_interval(self.move, 1 / 60)
        self._move_event = Clock.schedule_interval(self.move, 1 / 60)

    def move(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += self.gravity * dt

        self.check_collision()

        if self.y < 0 or self.x < 0 or self.x > Window.width:
            self.remove_bombshell()

    def check_collision(self):
        if not self.parent:
            return

        bomb_center = self.center
        # Se vuoi la posizione GLOBALE:
        bomb_center_global = self.to_window(*bomb_center)
        bomb_radius = self.width / 2  # se quadrato/circolare

        # Collisione con RockGroup
        for rockgroup in find_rockgroups(self.parent):
            for rock in rockgroup.children[:]:
                rock_center = rock.to_window(*rock.center)
                dx = bomb_center_global[0] - rock_center[0]
                dy = bomb_center_global[1] - rock_center[1]
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance <= self.damage_radius:
                    explosion = ExplosionEffect(center=self.center)
                    self.parent.add_widget(explosion)
                    rockgroup.remove_widget(rock)
                    self._save_score("RockGroup")
                    self.remove_bombshell()
                    return

        # Collisione con Snake (bersaglio)
        for snake in find_snakes(self.get_root_window()):
            snake_center = snake.to_window(*snake.center)
            dx = bomb_center_global[0] - snake_center[0]
            dy = bomb_center_global[1] - snake_center[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= self.damage_radius:
                print("→ SNAKE COLPITO!")
                explosion = ExplosionEffect(center=snake.center)
                self.parent.add_widget(explosion)

                if snake.parent:
                    snake.parent.remove_widget(snake)

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
                self._save_score("Snake", timer_widget)

                popup = Congratulations()
                popup.open()
                self.remove_bombshell()
                return 


        # Collisione con Elastonio (rimbalzo)
        for elastonio in find_elastonios(self.parent):
             # Calcola estremi della barra centrale dell'elastonio
            ex, ey = elastonio.center
            l = elastonio.width
            angle_rad = radians(getattr(elastonio, 'angle', 0))
            dx = (l/2) * cos(angle_rad)
            dy = (l/2) * sin(angle_rad)
            elastonio_p1 = self.parent.to_window(ex - dx, ey - dy)
            elastonio_p2 = self.parent.to_window(ex + dx, ey + dy)

            # Calcola la distanza tra centro bombshell e barra elastonio
            distance = point_segment_distance(
                bomb_center_global[0], bomb_center_global[1],
                elastonio_p1[0], elastonio_p1[1],
                elastonio_p2[0], elastonio_p2[1]
            )
            if distance <= bomb_radius:
                self.bounce_back()
                return
            
    def _save_score(self, target_type, timer_widget=None):
        bullets_fired = 0
        time_taken = None

        if self.parent_widget and hasattr(self.parent_widget, "bullets_fired"):
            bullets_fired = self.parent_widget.bullets_fired

        if timer_widget and hasattr(timer_widget, 'time_elapsed'):
            time_taken = timer_widget.time_elapsed

        save_score("Player", target_type, time_taken, bullets_fired)

    def _find_timer_widget(self, widget):
        if isinstance(widget, TimerWidget):
            return widget
        if hasattr(widget, "children"):
            for child in widget.children:
                found = self._find_timer_widget(child)
                if found:
                    return found
        return None


    def remove_bombshell(self):
        if self.parent:
            self.parent.remove_widget(self)
        Clock.unschedule(self.move)

    def bounce_back(self):
        self.velocity_x = -self.velocity_x
        self.velocity_y = -self.velocity_y
