from lxml import etree
import abc
from simulator.simulator_logger import SimulatorLoggerWrapper
from parameters.units import Unit, LengthUnits
from i18n_l10n.temporary_i18n_bridge import Localization
from typing import Dict, List
from simulator.xml_validation import XmlValidation


class VehicleModelConstants:
    ROOT_TAG = 'vehicle-models'
    COLLECTION_UNITS_ATTR = 'units'
    COLLECTION_VERSION_ATTR = 'version'
    UNIT_NAME_ATTR = 'name'
    UNIT_LENGTH_ATTR = 'length'
    UNIT_WIDTH_ATTR = 'width'
    UNIT_ARTICULATION_POINT_ATTR = 'articulation-point'
    MODEL_TAG = 'vehicle-model'
    MODEL_UUID_ATTR = 'uuid'
    TRAILER_TAG = 'trailer'
    TRAILER_TOWING_POINT_ATTR = 'towing-point'


class _VehicleUnit(abc.ABC):
    def __init__(self, from_element: etree.ElementBase, working_unit: Unit):
        # load the attributes common to all unit types--required attributes here
        self._length: float = working_unit.convert_to_base_units(
            float(from_element.attrib[VehicleModelConstants.UNIT_LENGTH_ATTR]))
        self._width: float = working_unit.convert_to_base_units(
            float(from_element.attrib[VehicleModelConstants.UNIT_WIDTH_ATTR]))

        # optional attributes
        self._name: str = from_element.attrib[VehicleModelConstants.UNIT_NAME_ATTR] \
            if VehicleModelConstants.UNIT_NAME_ATTR in from_element.attrib \
            else ''
        self._articulation_point: float = \
            working_unit.convert_to_base_units(
                float(from_element.attrib[VehicleModelConstants.UNIT_ARTICULATION_POINT_ATTR])) \
            if VehicleModelConstants.UNIT_ARTICULATION_POINT_ATTR in from_element.attrib \
            else None

        # optional trailer
        trailer_element = from_element.find(VehicleModelConstants.TRAILER_TAG)
        self._trailer: Trailer = Trailer(trailer_element, working_unit) \
            if trailer_element is not None \
            else None

        # check that articulation point is supplied with trailer
        if (self._trailer is not None) and (self._articulation_point is None):
            self._articulation_point = self._length
            SimulatorLoggerWrapper.logger().warning(Localization.get_message('W0001'))

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
    def __init__(self, from_element: etree.ElementBase, working_units: Unit):
        super().__init__(from_element, working_units)

        self._towing_point = working_units.convert_to_base_units(
            float(from_element.attrib[VehicleModelConstants.TRAILER_TOWING_POINT_ATTR]))

    @property
    def towing_point(self) -> float:
        return self._towing_point


class VehicleModel(_VehicleUnit):
    def __init__(self, from_element: etree.ElementBase, working_unit: Unit):
        super().__init__(from_element, working_unit)

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


class VehicleModelCollection:
    _instance: Dict[str, VehicleModel] = dict()

    @classmethod
    def read_from_xml(cls, xml: etree.ElementBase) -> None:
        version_number: int = int(xml.attrib[VehicleModelConstants.COLLECTION_VERSION_ATTR])
        if version_number == 1:
            units_text: str = xml.attrib[VehicleModelConstants.COLLECTION_UNITS_ATTR]
            units: Unit = LengthUnits.DICTIONARY()[units_text]

            for model_element in xml.iter(VehicleModelConstants.MODEL_TAG):
                model: VehicleModel = VehicleModel(model_element, units)
                cls._instance[model.uuid] = model

    @classmethod
    def __class_getitem__(cls, key: str) -> VehicleModel:
        if key not in cls._instance:
            raise KeyError(Localization.get_message('E0001', key))

        return VehicleModelCollection._instance[key]

    @classmethod
    def keys(cls) -> List[str]:
        return list(cls._instance.keys())

    @classmethod
    def reset(cls):
        """
        Removes all data from this collection. Generally intended for testing purposes.

        Returns:
            nothing
        """
        cls._instance.clear()


def process_file(filename) -> None:
    tree: etree.ElementTree = etree.parse(filename)
    xsd_tree: etree.XMLSchema = etree.XMLSchema(etree.parse(XmlValidation.VEHICLE_MODELS_XSD))
    if not xsd_tree.validate(tree):
        # validation failed
        raise RuntimeError(Localization.get_message('E0002', filename))

    VehicleModelCollection.read_from_xml(tree.getroot())
