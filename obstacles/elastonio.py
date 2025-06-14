from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Rotate


class ElastonioBar(Widget):
    thickness = NumericProperty(6)
    angle = NumericProperty(45)  # valore di default (ad esempio 45 gradi)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.redraw, size=self.redraw, thickness=self.redraw)
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 0, 1)  # giallo
            PushMatrix()
            Rotate(angle=self.angle, origin=self.center)
            # Disegniamo un rettangolo lungo quanto il widget, ma alto thickness
            Rectangle(pos=(self.x, self.center_y - self.thickness / 2),
                  size=(self.width, self.thickness))
            PopMatrix()
    
