from i18n_l10n.temporary_i18n_bridge import Localization
from abc import ABC, abstractmethod
from typing import Dict


class Unit:
    def __init__(self, name: str, conversion_factor_to_base_units: float):
        """
        Defines a new unit.
        Args:
            name: The name of the unit. The name may not be empty or whitespace-only.
            conversion_factor_to_base_units: The factor that this unit is multiplied by to get to SI Base Units.
        Examples:
            Unit('feet', 0.3048) defines feet in terms of the SI base unit (meters) because converting from feet
            to meters requires multiplying by 0.3048.
        """

        # check parameters
        if name.strip() == '':
            raise ValueError(Localization.get_message('D0001'))
        if conversion_factor_to_base_units == 0.0:
            raise ValueError(Localization.get_message('D0002'))

        # do assignments
        self._name: str = name
        self._factor: float = conversion_factor_to_base_units

    @property
    def name(self) -> str:
        return self._name

    def convert_to_base_units(self, value_in_this_unit: float) -> float:
        return value_in_this_unit * self._factor

    def convert_to_this_unit(self, value_in_base_units: float) -> float:
        return value_in_base_units / self._factor


class DimensionUnits(ABC):
    @classmethod
    @abstractmethod
    def DICTIONARY(cls) -> Dict[str, Unit]:
        pass


class LengthUnits(DimensionUnits):
    METERS = Unit('meters', 1.0)
    METRES = Unit('metres', 1.0)
    FEET = Unit('feet', 0.3048)

    @classmethod
    def DICTIONARY(cls) -> Dict[str, Unit]:
        return {
            cls.METRES.name: cls.METRES,
            cls.METERS.name: cls.METERS,
            cls.FEET.name: cls.FEET,
        }


class DistanceUnits(LengthUnits):
    KILOMETERS = Unit('kilometers', 1000.0)
    MILES = Unit('miles', 1609.344)

    @classmethod
    def DICTIONARY(cls) -> Dict[str, Unit]:
        return {
            cls.METRES.name: cls.METRES,
            cls.METERS.name: cls.METERS,
            cls.FEET.name: cls.FEET,
            cls.KILOMETERS.name: cls.KILOMETERS,
            cls.MILES.name: cls.MILES
        }


class TimeUnits(DimensionUnits):
    SECONDS = Unit('seconds', 1.0)
    MINUTES = Unit('minutes', 60.0)
    HOURS = Unit('hours', 3600.0)

    @classmethod
    def DICTIONARY(cls) -> Dict[str, Unit]:
        return {
            cls.SECONDS.name: cls.SECONDS,
            cls.MINUTES.name: cls.MINUTES,
            cls.HOURS.name: cls.HOURS,
        }


class SpeedUnits(DimensionUnits):
    MILES_PER_HOUR = Unit('miles-per-hour',
                          DistanceUnits.MILES.convert_to_base_units(1.0) /
                          TimeUnits.HOURS.convert_to_base_units(1.0))
    KILOMETERS_PER_HOUR = Unit('kilometers-per-hour',
                               DistanceUnits.KILOMETERS.convert_to_base_units(1.0) /
                               TimeUnits.HOURS.convert_to_base_units(1.0))
    METERS_PER_SECOND = Unit('meters-per-second', 1.0)
    FEET_PER_SECOND = Unit('feet-per-second', 0.3048)

    @classmethod
    def DICTIONARY(cls) -> Dict[str, Unit]:
        return {
            cls.MILES_PER_HOUR.name: cls.MILES_PER_HOUR,
            cls.KILOMETERS_PER_HOUR.name: cls.KILOMETERS_PER_HOUR,
            cls.METERS_PER_SECOND.name: cls.METERS_PER_SECOND,
            cls.FEET_PER_SECOND.name: cls.FEET_PER_SECOND
        }


class AccelerationUnits(DimensionUnits):
    METERS_PER_SECOND_SQUARED = Unit('meters-per-second-squared', 1.0)
    FEET_PER_SECOND_SQUARED = Unit('feet-per-second-squared', 0.3048)
    G = Unit('g', 9.80665)

    @classmethod
    def DICTIONARY(cls) -> Dict[str, Unit]:
        return {
            cls.METERS_PER_SECOND_SQUARED.name: cls.METERS_PER_SECOND_SQUARED,
            cls.FEET_PER_SECOND_SQUARED.name: cls.FEET_PER_SECOND_SQUARED,
            cls.G.name: cls.G
        }
