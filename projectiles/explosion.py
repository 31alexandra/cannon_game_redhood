from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Ellipse, Color
from random import uniform

class ExplosionEffect(Widget):
    def __init__(self, center, radius=30, **kwargs):
        super().__init__(**kwargs)
        self.center = center
        self.radius = radius
        self.particles = []
        self.lifetime = 0.5  # seconds

        with self.canvas:
            for _ in range(8):
                Color(1, uniform(0.2, 1), 0)
                particle = Ellipse(pos=(center[0] + uniform(-radius, radius),
                                        center[1] + uniform(-radius, radius)),
                                   size=(5, 5))
                self.particles.append(particle)

        Clock.schedule_once(self.remove_effect, self.lifetime)

    def remove_effect(self, *args):
        self.parent.remove_widget(self)
