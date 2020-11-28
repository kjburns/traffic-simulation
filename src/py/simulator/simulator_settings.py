import isodate
from lxml import etree
from datetime import time, timezone, timedelta
from simulator import xml_validation
from simulator.default_xml_files import DefaultXmlFiles
from i18n_l10n.temporary_i18n_bridge import Localization
from parameters.vehicle_models import VehicleModelCollection
from typing import Callable, Tuple, List, Type, final
from zipfile import ZipFile
from py7zr import py7zr
from abc import ABC, abstractmethod
from tempfile import TemporaryDirectory
import os
from pathlib import Path


class ArchiveProcessor(ABC):
    @classmethod
    @abstractmethod
    def open_archive(cls, path: str) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_xml(cls, name_fragment: str) -> etree.ElementBase:
        pass

    @classmethod
    @abstractmethod
    def close_archive(cls) -> None:
        pass


class ZipProcessor(ArchiveProcessor):
    _zipfile: ZipFile = None

    @classmethod
    def open_archive(cls, path: str) -> None:
        cls._zipfile = ZipFile(path)

    @classmethod
    def get_xml(cls, name_fragment: str) -> etree.ElementBase:
        candidates: List[str] = list(filter(lambda filename: name_fragment in filename, cls._zipfile.namelist()))
        if len(candidates) != 1:
            raise ValueError(Localization.get_message('E0003', name_fragment))
        with cls._zipfile.open(candidates[0], 'r') as fp:
            return etree.parse(fp).getroot()

    @classmethod
    def close_archive(cls) -> None:
        if cls._zipfile is not None:
            cls._zipfile.close()
            cls._zipfile = None


class SevenZipProcessor(ArchiveProcessor):
    _temp_directory: TemporaryDirectory = None
    _file_list: List[str] = []

    @classmethod
    def open_archive(cls, path: str) -> None:
        cls._temp_directory = TemporaryDirectory()
        with py7zr.SevenZipFile as archive:
            archive.extractall(cls._temp_directory.name)

        cls._file_list = os.listdir(cls._temp_directory.name)

    @classmethod
    def get_xml(cls, name_fragment: str) -> etree.ElementBase:
        candidates: List[str] = list(filter(lambda filename: name_fragment in filename, cls._file_list))
        if len(candidates) != 1:
            raise ValueError('E0003', name_fragment)
        xml_file: Path = Path(cls._temp_directory.name) / Path(candidates[0])
        return_element: etree.ElementBase = etree.parse(xml_file).getroot()

        return return_element

    @classmethod
    def close_archive(cls) -> None:
        if cls._temp_directory is not None:
            cls._temp_directory.cleanup()
            cls._temp_directory = None


class SimulationSettingsXmlNames:
    ROOT_TAG = 'simulation-settings'
    VERSION_ATTR = 'version'
    RUN_COUNT_ATTR = 'run-count'
    FILES_TAG = 'files'
    ARCHIVE_TAG = 'archive'
    ARCHIVE_PATH_ATTR = 'path'
    ARCHIVE_TYPE_ATTR = 'type'
    SIM_TIMES_TAG = 'simulation-times'
    SIM_START_ATTR = 'simulation-start-time'
    SIM_TIMEZONE_ATTR = 'utc-offset'
    SIM_EVALUATION_LENGTH_ATTR = 'evaluation-length'
    SIM_SEED_LENGTH_ATTR = 'seed-length'
    SIM_TIME_STEPS_ATTR = 'time-steps-per-second'
    SEEDING_TAG = 'seeding'
    SEEDING_FIRST_SEED_ATTR = 'random-seed-first-run'
    SEEDING_SEED_INCREMENT_ATTR = 'random-seed-increment'


class SimulatorSettings:
    _run_count: int
    _simulation_start_time: time
    _time_zone: timezone
    _evaluation_length: timedelta
    _seed_length: timedelta
    _time_steps_per_second: int
    _seed_first_run: int
    _seed_subsequent_runs: int

    @classmethod
    def process_file(cls, sim_settings_file_path: str):
        root_element: etree.ElementBase = etree.parse(sim_settings_file_path).getroot()

        # check validation
        xsd = etree.XMLSchema(etree.parse(xml_validation.XmlValidation.SIMULATION_SETTINGS_XSD))
        if not xsd.validate(root_element):
            raise RuntimeError(Localization.get_message('E0002', sim_settings_file_path))

        version_number: int = int(root_element.attrib[SimulationSettingsXmlNames.VERSION_ATTR])

        # changes in future versions go here, newest at top

        if version_number >= 1:
            if SimulationSettingsXmlNames.RUN_COUNT_ATTR in root_element.attrib:
                cls._run_count = int(root_element.attrib[SimulationSettingsXmlNames.RUN_COUNT_ATTR])
            else:
                cls._run_count = 1

            simulation_times_node: etree.ElementBase = root_element.find(SimulationSettingsXmlNames.SIM_TIMES_TAG)
            cls._simulation_start_time = isodate.isotime.parse_time(
                simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_START_ATTR])

            if SimulationSettingsXmlNames.SIM_TIMEZONE_ATTR in simulation_times_node.attrib:
                cls._time_zone = timezone(
                    offset=timedelta(
                        hours=int(simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_TIMEZONE_ATTR])
                    )
                )
            else:
                cls._time_zone = timezone(offset=timedelta(hours=0))

            cls._evaluation_length = isodate.parse_duration(
                simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_EVALUATION_LENGTH_ATTR]
            )
            cls._seed_length = isodate.parse_duration(
                simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_SEED_LENGTH_ATTR]
            )

            if SimulationSettingsXmlNames.SIM_TIME_STEPS_ATTR in simulation_times_node.attrib:
                cls._time_steps_per_second = int(
                    simulation_times_node.attrib[SimulationSettingsXmlNames.SIM_TIME_STEPS_ATTR]
                )
            else:
                cls._time_steps_per_second = 10

            seeding_node: etree.ElementBase = root_element.find(SimulationSettingsXmlNames.SEEDING_TAG)
            if SimulationSettingsXmlNames.SEEDING_FIRST_SEED_ATTR in seeding_node.attrib:
                cls._seed_first_run = int(seeding_node.attrib[SimulationSettingsXmlNames.SEEDING_FIRST_SEED_ATTR])
            else:
                cls._seed_first_run = 73110

            if SimulationSettingsXmlNames.SEEDING_SEED_INCREMENT_ATTR in seeding_node.attrib:
                cls._seed_subsequent_runs = \
                    int(seeding_node.attrib[SimulationSettingsXmlNames.SEEDING_SEED_INCREMENT_ATTR])
            else:
                cls._seed_subsequent_runs = 10

            archive_element: etree.ElementBase = root_element.find(SimulationSettingsXmlNames.ARCHIVE_TAG)
            cls._handle_archive(archive_element)

            files_element: etree.ElementBase = root_element.find(SimulationSettingsXmlNames.FILES_TAG)
            cls._handle_files(files_element)

    @classmethod
    def run_count(cls) -> int:
        return cls._run_count

    @classmethod
    def simulation_start_time(cls) -> time:
        return cls._simulation_start_time

    @classmethod
    def time_zone(cls) -> timezone:
        return cls._time_zone

    @classmethod
    def evaluation_length(cls) -> timedelta:
        return cls._evaluation_length

    @classmethod
    def seed_length(cls) -> timedelta:
        return cls._seed_length

    @classmethod
    def time_steps_per_second(cls) -> int:
        return cls._time_steps_per_second

    @classmethod
    def seed_for_run_number(cls, run_number: int) -> int:
        return cls._seed_first_run + (run_number - 1) * cls._seed_subsequent_runs

    @classmethod
    def _handle_archive(cls, archive_element: etree.ElementBase) -> None:
        if archive_element is None:
            return

        file_type: str = archive_element.attrib[SimulationSettingsXmlNames.ARCHIVE_TYPE_ATTR]
        path_name: str = archive_element.attrib[SimulationSettingsXmlNames.ARCHIVE_PATH_ATTR]
        getter: Type[ArchiveProcessor]

        if file_type == _ArchiveFormats.ZIP:
            getter = ZipProcessor
        else:  # file_type == _ArchiveFormats.SEVEN_Z
            getter = SevenZipProcessor

        getter.open_archive(path_name)

        fragment_processor_tuples: List[Tuple[str, Callable[[etree.ElementBase], None]]] = [
            ('vehicle-models', VehicleModelCollection.read_from_xml),
            # TODO fill these in
        ]
        try:
            for (fragment, processor) in fragment_processor_tuples:
                xml: etree.ElementBase = getter.get_xml(fragment)
                processor(xml)
        except (FileNotFoundError, ValueError):
            raise
        finally:
            getter.close_archive()

    @classmethod
    def _handle_files(cls, files_element: etree.ElementBase) -> None:
        if files_element is None:
            return

        vehicle_models_attr: str = 'vehicle-models'
        vehicle_models_path: str
        if vehicle_models_attr in files_element.attrib:
            vehicle_models_path = files_element.attrib[vehicle_models_attr]
        else:
            vehicle_models_path = DefaultXmlFiles.VEHICLE_MODELS_FILE
        vehicle_models_file: etree.ElementBase = etree.parse(vehicle_models_path).getroot()
        VehicleModelCollection.read_from_xml(vehicle_models_file)

        distributions_attr: str = 'distributions'
        distributions_path: str
        if distributions_attr in files_element.attrib:
            distributions_path = files_element.attrib[distributions_attr]
        else:
            distributions_path = DefaultXmlFiles.DISTRIBUTIONS_FILE
        distributions_node: etree.ElementBase = etree.parse(distributions_path).getroot()
        # TODO process distributions file

        vehicle_types_attr: str = 'vehicle-types'
        vehicle_types_path: str
        if vehicle_types_attr in files_element.attrib:
            vehicle_types_path = files_element.attrib[vehicle_types_attr]
        else:
            vehicle_types_path = DefaultXmlFiles.VEHICLE_TYPES_FILE
        vehicle_types_node: etree.ElementBase = etree.parse(vehicle_types_path).getroot()
        # TODO process vehicle types file

        behaviors_attr: str = 'behavior'
        behaviors_path: str
        if behaviors_attr in files_element.attrib:
            behaviors_path = files_element.attrib[behaviors_attr]
        else:
            behaviors_path = DefaultXmlFiles.BEHAVIOR_FILE
        behavior_node: etree.ElementBase = etree.parse(behaviors_path).getroot()
        # TODO process behaviors file

        lane_usage_attr: str = 'lane-usage'
        lane_usage_path: str
        if lane_usage_attr in files_element.attrib:
            lane_usage_path = files_element.attrib[lane_usage_attr]
        else:
            lane_usage_path = DefaultXmlFiles.LANE_USAGE_FILE
        lane_usage_node: etree.ElementBase = etree.parse(lane_usage_path).getroot()
        # TODO process lane usage file

        network_attr: str = 'network'
        network_path: str = files_element.attrib[network_attr]
        network_node: etree.ElementBase = etree.parse(network_path).getroot()
        # TODO process network file

        evaluations_attr: str = 'evaluation'
        # TODO complete evaluations later


class _ArchiveFormats:
    ZIP: str = 'zip'
    SEVEN_Z: str = '7z'
