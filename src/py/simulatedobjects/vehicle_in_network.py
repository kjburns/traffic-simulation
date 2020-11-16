class VehicleInNetwork:
    """
    Representation of a vehicle in the network during simulation.

    Vehicles are views of numpy/cupy arrays. Each vehicle is assigned a vehicle id,
    which is in turn generated by a unique id generator.
    """
    _next_unique_id_value: int = 0
    _simulation_state_dictionary: dict = None

    @classmethod
    def set_simulation_state_dictionary(cls, ssd: dict) -> None:
        cls._simulation_state_dictionary = ssd

    @classmethod
    def _generate_unique_id(cls) -> int:
        ret = cls._next_unique_id_value
        cls._next_unique_id_value = cls._next_unique_id_value + 1

        return ret

    def __init__(self):
        self._id: int = VehicleInNetwork._generate_unique_id()

    @property
    def id(self) -> int:
        """
        Returns the vehicle's id.
        """
        return self._id
