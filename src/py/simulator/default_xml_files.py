import os
from pathlib import Path


def _generateFullPath(filename: str) -> str:
    full_path: str = os.path.realpath(__file__)
    dir_path: Path = Path(os.path.dirname(full_path))
    root_path: Path = dir_path.parent.parent.parent
    xsd_path: Path = root_path / 'default-files' / filename
    return str(xsd_path)


class DefaultXmlFiles:
    BEHAVIOR_FILE: str = _generateFullPath('default.behaviors.xml')
    DISTRIBUTIONS_FILE: str = _generateFullPath('default.distributions.xml')
    LANE_USAGE_FILE: str = _generateFullPath('default.lane-usage.xml')
    VEHICLE_MODELS_FILE: str = _generateFullPath('default.vehicle-models.xml')
    VEHICLE_TYPES_FILE: str = _generateFullPath('default.vehicle-types.xml')
