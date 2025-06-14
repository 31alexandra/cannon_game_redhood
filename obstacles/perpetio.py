from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.lang import Builder

# Carica il file KV associato
Builder.load_file("obstacles/perpetio.kv")

class SinglePerpetio(Image):
    pass

class PerpetioGroup(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_pyramid()

    def build_pyramid(self):
        """
        Crea una piramide di blocchi perpetio con 4 livelli (totale 10 blocchi).
        Posizionata con base in basso e vertice in alto, centrata orizzontalmente.
        """
        size = 30  # Dimensione di ogni blocco
        spacing = 1  # Spazio tra i blocchi
        levels = 6  # Numero di livelli nella piramide

        total_height = levels * (size + spacing)
        width_pyramid = levels * (size + spacing)

        for row in range(levels):
            for col in range(row + 1):
                block = SinglePerpetio()
                block.size_hint = (None, None)
                block.size = (size, size)

                # Posizionamento orizzontale centrato
                x_offset = (width_pyramid - (row + 1) * (size + spacing)) / 2 + col * (size + spacing)
                # Posizionamento verticale dal basso verso l’alto
                y_offset = total_height - (row + 1) * (size + spacing)

                block.pos = (x_offset, y_offset)
                self.add_widget(block)

    def handle_bullet_collision(self, bullet_center, damage_radius):
        for child in self.children:
            if self.collide_point(*bullet_center):
                self.parent.remove_widget(self)  # rimuovi il proiettile dal game_area
