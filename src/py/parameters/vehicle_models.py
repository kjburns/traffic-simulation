from lxml import etree
import abc
from simulator.SimulatorLoggerWrapper import SimulatorLoggerWrapper

unit_factors_dict: dict = {
    'meters': 1.0,
    'metres': 1.0,
    'feet': 0.3048,
}


class VehicleModelConstants:
    UNIT_NAME_ATTR = 'name'
    UNIT_LENGTH_ATTR = 'length'
    UNIT_WIDTH_ATTR = 'width'
    UNIT_ARTICULATION_POINT_ATTR = 'articulation-point'
    MODEL_TAG = 'vehicle-model'
    MODEL_UUID_ATTR = 'uuid'
    TRAILER_TAG = 'trailer'
    TRAILER_TOWING_POINT_ATTR = 'towing-point'


class _VehicleUnit(abc.ABC):
    def __init__(self, from_element: etree.ElementBase, units: str):
        conversion: float = unit_factors_dict[units]

        # load the attributes common to all unit types--required attributes here
        self._length: float = float(from_element.attrib[VehicleModelConstants.UNIT_LENGTH_ATTR]) / conversion
        self._width: float = float(from_element.attrib[VehicleModelConstants.UNIT_WIDTH_ATTR]) / conversion

        # optional attributes
        self._name: str = from_element.attrib[VehicleModelConstants.UNIT_NAME_ATTR] \
            if VehicleModelConstants.UNIT_NAME_ATTR in from_element.attrib \
            else ''
        self._articulation_point: float = \
            from_element.attrib[VehicleModelConstants.UNIT_ARTICULATION_POINT_ATTR] / conversion \
            if VehicleModelConstants.UNIT_ARTICULATION_POINT_ATTR in from_element.attrib \
            else None

        # optional trailer
        trailer_element = from_element.find(VehicleModelConstants.TRAILER_TAG)
        self._trailer: Trailer = Trailer(trailer_element, units) \
            if trailer_element is not None \
            else None

        # check that articulation point is supplied with trailer
        if (self._trailer is not None) and (self._articulation_point is None):
            self._articulation_point = self._length
            SimulatorLoggerWrapper.logger().warning(
                'Vehicle has trailer but no articulation point was provided. '
                'Articulation point assumed to be at back tip of vehicle.')

    @property
    def length(self) -> float:
        return self._length

    @property
    def width(self) -> float:
        return self._width

    @property
    def name(self) -> str:
        return self._name

    @property
    def articulation_point(self) -> float:
        return self._articulation_point

    @property
    def trailer(self):
        return self._trailer


class Trailer(_VehicleUnit):
    def __init__(self, from_element: etree.ElementBase, units: str):
        super().__init__(from_element, units)

        self._towing_point = \
            float(from_element.attrib[VehicleModelConstants.TRAILER_TOWING_POINT_ATTR]) / unit_factors_dict[units]

    @property
    def towing_point(self) -> float:
        return self._towing_point


class VehicleModel(_VehicleUnit):
    def __init__(self, from_element: etree.ElementBase, units: str):
        super().__init__(from_element, units)

        self._uuid = from_element.attrib[VehicleModelConstants.MODEL_UUID_ATTR]

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def total_length(self) -> float:
        length: float = 0
        active_unit: _VehicleUnit = self
        while active_unit is not None:
            trailer_of_active_unit: Trailer = active_unit.trailer
            length += active_unit.length if trailer_of_active_unit is None \
                else (active_unit.articulation_point - trailer_of_active_unit.towing_point)
            active_unit = trailer_of_active_unit

        return length

    @property
    def maximum_width(self) -> float:
        max_width: float = 0.0
        active_unit: _VehicleUnit = self
        while active_unit is not None:
            max_width = max(active_unit.width, max_width)
            active_unit = active_unit.trailer

        return max_width
