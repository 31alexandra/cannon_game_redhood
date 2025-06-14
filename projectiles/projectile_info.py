from constants import physics_constants


def get_bullet_mass():
    return physics_constants.BULLET_MASS

def set_bullet_mass(value):
    physics_constants.BULLET_MASS = float(value)

def get_bullet_radius():
    return physics_constants.BULLET_RADIUS

def set_bullet_radius(value):
    physics_constants.BULLET_RADIUS = float(value)


def get_bombshell_mass():
    return physics_constants.BOMB_MASS

def set_bombshell_mass(value):
    physics_constants.BOMB_MASS = float(value)

def get_bombshell_radius():
    return physics_constants.BOMB_RADIUS

def set_bombshell_radius(value):
    physics_constants.BOMB_RADIUS = float(value)
