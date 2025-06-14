import os
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Rotate
from math import radians, sin, cos

from projectiles.explosion import ExplosionEffect
from obstacles.perpetio import PerpetioGroup
from screens.congratulations import Congratulations
from functions.hall_of_fame import save_score
from functions.timer_widget import TimerWidget
from obstacles.mirror import Mirror

LASER_DIST = 60
LASER_IMPULSE = 1000 # Distanza massima che il laser può percorrere
LASER_VEL = 500

# Funzione per calcolare l'intersezione tra due segmenti
def line_intersect(a1, a2, b1, b2):
    """Restituisce True se il segmento a1-a2 interseca b1-b2."""
    def ccw(A,B,C):
        return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
    return (ccw(a1,b1,b2) != ccw(a2,b1,b2)) and (ccw(a1,a2,b1) != ccw(a1,a2,b2))

def find_perpetiogroups(widget):
    perpetios = []
    if isinstance(widget, PerpetioGroup):
        perpetios.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            perpetios.extend(find_perpetiogroups(child))
    return perpetios


def find_mirrors(widget):
    mirrors = []
    if isinstance(widget, Mirror):
        mirrors.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            mirrors.extend(find_mirrors(child))
    return mirrors


def find_wolves(widget):
    from kivy.uix.image import Image
    wolves = []
    if isinstance(widget, Image):
        filename = os.path.basename(widget.source).lower()
        if "wolf.png" in filename:
            wolves.append(widget)
    if hasattr(widget, 'children'):
        for child in widget.children:
            wolves.extend(find_wolves(child))
    return wolves


class Laser(Widget):
    angle = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    damage_radius = NumericProperty(LASER_DIST)
    impulse = NumericProperty(LASER_IMPULSE)
    parent_widget = ObjectProperty(None)

    def __init__(self, angle, parent_widget=None, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (None, None)
        self.laser_length = 250
        self.laser_width = 10
        self.size = (self.laser_length, self.laser_width)
        self.angle = angle
        self.parent_widget = parent_widget

        angle_rad = radians(angle)
        self.velocity_x = LASER_VEL * cos(angle_rad)
        self.velocity_y = LASER_VEL * sin(angle_rad)

        self._distance_travelled = 0
        self._max_distance = LASER_IMPULSE

        self.start_pos = self.pos  # Will be updated on move
        self.end_pos = self._calculate_end_pos()

        self.draw_laser()

        self.bind(pos=self.update_graphics, size=self.update_graphics, center=self.update_graphics)
        Clock.schedule_interval(self.move, 1 / 60)

    def _calculate_end_pos(self):
        angle_rad = radians(self.angle)
        x2 = self.x + self.laser_length * cos(angle_rad)
        y2 = self.y + self.laser_length * sin(angle_rad)
        return (x2, y2)

    def draw_laser(self):
        self.canvas.clear()
        angle_rad = radians(self.angle)
        # La linea parte dal centro del laser (che hai posizionato sulla bocca della canna)
        start_x, start_y = self.center
        end_x = start_x + self.laser_length * cos(angle_rad)
        end_y = start_y + self.laser_length * sin(angle_rad)
        with self.canvas:
            # Glow esterno
            Color(0.65, 0.42, 0.25, 0.6)
            Line(points=[start_x, start_y, end_x, end_y], width=8)
            # Raggio centrale
            Color(0.36, 0.25, 0.20, 0.95)
            Line(points=[start_x, start_y, end_x, end_y], width=4)
    
    def update_graphics(self, *args):
        self.draw_laser()

    def move(self, dt):
        dx = self.velocity_x * dt
        dy = self.velocity_y * dt
        self.x += dx
        self.y += dy
        self._distance_travelled += (dx**2 + dy**2) ** 0.5
        self.update_graphics()
        self.check_collision()
        if (self.y < 0 or self.x < 0 or self.x > Window.width or 
            self._distance_travelled >= self._max_distance):
            # Se il laser esce dallo schermo o ha raggiunto la distanza massima
            self.remove_laser()


    def check_collision(self):
        if not self.parent:
            return

        laser_start = self.center
        angle_rad = radians(self.angle)
        laser_end = (
            laser_start[0] + self.laser_length * cos(angle_rad),
            laser_start[1] + self.laser_length * sin(angle_rad)
        )

          # Collisione con Perpetio
        for perpetio_group in find_perpetiogroups(self.parent):
            for block in perpetio_group.children[:]:
                # Calcola la punta del laser (end point)
                angle_rad = radians(self.angle)
                laser_tip_x = self.center[0] + self.laser_length * cos(angle_rad)
                laser_tip_y = self.center[1] + self.laser_length * sin(angle_rad)
                laser_tip = (laser_tip_x, laser_tip_y)
                
                # Rendi le coordinate della punta globali
                laser_tip_global = self.to_window(*laser_tip)
                
                # Ottieni la posizione e dimensione del Perpetio (bounding box)
                block_x, block_y = block.to_window(block.x, block.y)
                block_w, block_h = block.size

                # Se la punta è dentro il bounding box, c'è collisione
                if (block_x <= laser_tip_global[0] <= block_x + block_w and
                    block_y <= laser_tip_global[1] <= block_y + block_h):
                    explosion = ExplosionEffect(center=self.center)
                    self.parent.add_widget(explosion)
                    self._save_score("Perpetio")
                    self.remove_laser()
                    return
                
        # Collisione con Mirror
        for mirror in find_mirrors(self.parent):
            # Calcola i due estremi della barra centrale del mirror
            mx, my = mirror.center
            l = mirror.width
            t = mirror.thickness

            # La barra dello specchio è lunga quanto il mirror.width, ruotata di mirror.angle
            m_angle_rad = radians(mirror.angle)
            dx = (l/2) * cos(m_angle_rad)
            dy = (l/2) * sin(m_angle_rad)

            mirror_p1 = (mx - dx, my - dy)
            mirror_p2 = (mx + dx, my + dy)

            if line_intersect(laser_start, laser_end, mirror_p1, mirror_p2):
                self.bounce_on_mirror(mirror)
                return

        # Collisione con Wolf
        for wolf in find_wolves(self.get_root_window()):
            wolf_center = wolf.to_window(*wolf.center)
            dx = laser_start[0] - wolf_center[0]
            dy = laser_start[1] - wolf_center[1]
            distance = (dx**2 + dy**2)**0.5

            if distance <= self.damage_radius:
                explosion = ExplosionEffect(center=wolf.center)
                self.parent.add_widget(explosion)
                if wolf.parent:
                    wolf.parent.remove_widget(wolf)

                timer_widget = self._find_timer_widget(self.get_root_window())
                if timer_widget:
                    timer_widget.level_completed()
                self._save_score("Wolf", timer_widget)

                popup = Congratulations()
                popup.open()
                #self.remove_laser()
                return

    def _find_timer_widget(self, widget):
        if isinstance(widget, TimerWidget):
            return widget
        if hasattr(widget, "children"):
            for child in widget.children:
                found = self._find_timer_widget(child)
                if found:
                    return found
        return None

    def _save_score(self, target_type, timer_widget=None):
        bullets_fired = 0
        time_taken = None

        if self.parent_widget and hasattr(self.parent_widget, "bullets_fired"):
            bullets_fired = self.parent_widget.bullets_fired

        if timer_widget and hasattr(timer_widget, 'time_elapsed'):
            time_taken = timer_widget.time_elapsed

        save_score("Player", target_type, time_taken, bullets_fired)

    def remove_laser(self):
        if self.parent:
            self.parent.remove_widget(self)
        Clock.unschedule(self.move)
    
    def bounce_on_mirror(self, mirror):
        # Angolo incidente rispetto all'orizzontale
        incidence = self.angle
        mirror_angle = mirror.angle
        # Calcola l'angolo riflesso
        reflected = 2 * mirror_angle - incidence
        self.angle = reflected
        angle_rad = radians(reflected)
        self.velocity_x = LASER_VEL * cos(angle_rad)
        self.velocity_y = LASER_VEL * sin(angle_rad)
        # Sposta il laser un po', così non collide subito di nuovo
        self.x += cos(angle_rad) * 10
        self.y += sin(angle_rad) * 10
        self.update_graphics()
