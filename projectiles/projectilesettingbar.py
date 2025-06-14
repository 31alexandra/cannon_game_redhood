from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from projectiles.projectile_info import (
    get_bullet_mass, set_bullet_mass,
    get_bullet_radius, set_bullet_radius
)

MAX_MASS = 10
MIN_MASS = 0.1

class ProjectileSettingsBar(BoxLayout):
    # Questi valori servono per mostrare nella UI lo stato attuale
    mass_value = NumericProperty(get_bullet_mass())
    radius_value = NumericProperty(get_bullet_radius())

    def on_mass_slider_change(self, value):
        # Invertiamo correttamente: destra (value alto) → massa bassa
        inverted_value = MIN_MASS + (MAX_MASS - value)
        # Aggiorniamo visualizzazione e logica
        self.mass_value = value  # valore mostrato nello slider (non invertito!)
        set_bullet_mass(inverted_value)

        print(f"[Slider MASS] Valore slider: {value:.2f} → Massa effettiva usata: {inverted_value:.2f}")

    def on_radius_slider_change(self, value):
        self.radius_value = value
        set_bullet_radius(value)
        print(f"[Slider RADIUS] Raggio aggiornato: {value:.2f}")
