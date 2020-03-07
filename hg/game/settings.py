class Settings:

    def __init__(self, **settings):
        self.physics_time_step = settings.get('physics_time_step', 0.015)
        self.gravity_force = settings.get('gravity_force', 98)
