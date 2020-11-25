import os
from pathlib import Path


def _generateFullPath(xsd_name: str) -> str:
    full_path: str = os.path.realpath(__file__)
    dir_path: Path = Path(os.path.dirname(full_path))
    root_path: Path = dir_path.parent.parent.parent
    xsd_path: Path = root_path / 'xml' / xsd_name
    return str(xsd_path)


class XmlValidation:
    BEHAVIOR_XSD: str = _generateFullPath('behavior.xsd')
    DISTRIBUTIONS_XSD: str = _generateFullPath('distributions.xsd')
    LANE_USAGE_XSD: str = _generateFullPath('lane-usage.xsd')
    NETWORK_XSD: str = _generateFullPath('network.xsd')
    SIMULATION_SETTINGS_XSD: str = _generateFullPath('simulation-settings.xsd')
    VEHICLE_MODELS_XSD: str = _generateFullPath('vehicle-models.xsd')
    VEHICLE_TYPES_XSD: str = _generateFullPath('vehicle-types.xsd')
