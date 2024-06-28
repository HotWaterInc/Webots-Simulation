from enum import Enum


class TeleportType(Enum):
    TELEPORT8x8 = 1
    TELEPORT15x15 = 2


class Movement:
    __instance = None

    @staticmethod
    def get_instance():
        if Movement.__instance is None:
            Movement()
        return Movement.__instance

    def __init__(self):
        if Movement.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Movement.__instance = self
            self.teleport_type = None
            self.teleport_total_width = None
            self.teleport_total_height = None
            self.teleport_width = None
            self.teleport_height = None
            self.generator = self._create_generator()

    def set_teleport_type(self, teleport_type: TeleportType, teleport_width: int, teleport_height: int) -> None:
        self.teleport_type = teleport_type
        self.teleport_total_width = teleport_width
        self.teleport_total_height = teleport_height

        if teleport_type == TeleportType.TELEPORT8x8:
            self.teleport_width = self.teleport_total_width / 8
            self.teleport_height = self.teleport_total_height / 8
        elif teleport_type == TeleportType.TELEPORT15x15:
            self.teleport_width = self.teleport_total_width / 15
            self.teleport_height = self.teleport_total_height / 15

    def get_teleport_coords(self, x, y):
        row, col = x, y;

        x_coord = col * self.teleport_width
        y_coord = row * self.teleport_height

        return x_coord, y_coord

    # generator function returning next coords

    def _create_generator(self):
        if self.teleport_type == TeleportType.TELEPORT8x8:
            for x in range(8):
                for y in range(8):
                    yield x, y
        elif self.teleport_type == TeleportType.TELEPORT15x15:
            for x in range(15):
                for y in range(15):
                    yield x, y
        else:
            raise Exception("Teleport type not set")

    def get_teleport_indices(self):
        try:
            return next(self.generator)
        except Exception:
            print("entered exception")
            return None  # or raise an exception, or reset the generator
