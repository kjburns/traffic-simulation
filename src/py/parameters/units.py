from i18n_l10n.temporary_i18n_bridge import Localization


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


class LengthUnits:
    METERS = Unit('meters', 1.0)
    METRES = Unit('metres', 1.0)
    FEET = Unit('feet', 0.3048)

    DICTIONARY = {
        METRES.name: METRES,
        METERS.name: METERS,
        FEET.name: FEET,
    }


class DistanceUnits(LengthUnits):
    KILOMETERS = Unit('kilometers', 0.001)
    MILES = Unit('miles', 1.0 / 1609.344)

    DICTIONARY = {
        LengthUnits.METRES.name: LengthUnits.METRES,
        LengthUnits.METERS.name: LengthUnits.METERS,
        LengthUnits.FEET.name: LengthUnits.FEET,
        KILOMETERS.name: KILOMETERS,
        MILES.name: MILES
    }
