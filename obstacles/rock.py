from kivy.uix.relativelayout import RelativeLayout 
from kivy.uix.image import Image
from kivy.lang import Builder

Builder.load_file("obstacles/rock.kv")

class SingleRock(Image):
    pass

class RockGroup(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_square()

    def build_square(self):
        size = 30
        spacing = 1
        self.rows = 4
        self.cols = 4

        for row in range(self.rows):
            for col in range(self.cols):
                rock = SingleRock()
                rock.size_hint = (None, None)
                rock.size = (size, size)
                x_offset = col * (size + spacing)
                y_offset = row * (size + spacing)
                rock.pos = (x_offset, y_offset)
                self.add_widget(rock)

    # Funzione che rimuove i blocchi entro il raggio della collisione
    def handle_bullet_collision(self, bullet_center, radius):
        to_remove = []
        for rock in self.children[:]:
            global_x, global_y = rock.to_window(*rock.center)
            dx = global_x - bullet_center[0]
            dy = global_y - bullet_center[1]
            distance = (dx**2 + dy**2)**0.5
            if distance <= radius:
                to_remove.append(rock)

        for rock in to_remove:
            self.remove_widget(rock)

