from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty, ObjectProperty
from math import radians, sin, cos
from constants.physics_constants import LASER_VEL
from projectiles.laser import Laser

Builder.load_file("levels/cannon.kv")

class CannonWidget(Widget):
    angle = NumericProperty(0)
    projectile_cls = ObjectProperty(None)
    parent_widget = ObjectProperty(None)

    def __init__(self, projectile_cls, parent_widget, **kwargs):
        super().__init__(**kwargs)
        self.projectile_cls = projectile_cls
        self.parent_widget = parent_widget
        Window.bind(on_key_down=self.on_key_down)


    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        print("Tasto premuto:", key)
        if key == 273:  # Freccia su
            self.angle = min(self.angle + 5, 90)
        elif key == 274:  # Freccia giù
            self.angle = max(self.angle - 5, -90)
        elif key == 32:  # Spazio premuto, spara
            print("Projectile_cls:", self.projectile_cls, self.projectile_cls.__name__)
            # Calcolo della bocca della canna
            canna_base_x = self.x + 190
            canna_base_y = self.y + 57.5
            barrel_offset = 70  # Lunghezza della canna come da Rectangle: size: 70, 20
            angle_rad = radians(self.angle)

            bullet_x = canna_base_x + barrel_offset * cos(angle_rad)
            bullet_y = canna_base_y + barrel_offset * sin(angle_rad)

            projectile = self.projectile_cls(angle=self.angle, parent_widget=self.parent_widget)
            projectile.center = (bullet_x, bullet_y)
            print("Centro laser:", projectile.center, "Posizione:", projectile.pos)

            # Solo per proiettili diversi dal Laser, aggiorna la velocity
            if hasattr(projectile, 'velocity') and self.projectile_cls.__name__ != "Laser":
                direction_x = cos(angle_rad)
                direction_y = sin(angle_rad)
                projectile.velocity = projectile.velocity * direction_x, projectile.velocity * direction_y

            self.parent_widget.add_widget(projectile)
            print("Laser aggiunto al parent:", self.parent_widget)

            if hasattr(self.parent_widget, "bullets_fired"):
                self.parent_widget.bullets_fired += 1

