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
