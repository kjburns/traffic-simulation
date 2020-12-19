import unittest
from tempfile import NamedTemporaryFile
from lxml import etree
from simulator.default_xml_files import DefaultXmlFiles
from parameters.distributions import Distributions, DistributionXmlNames, T, DistributionSet, StringDistribution, \
    DistanceDistribution, ColorDistribution, AccelerationFunction
import os
from uuid import uuid4 as uuid
from parameters.units import DistanceUnits, SpeedUnits, AccelerationUnits
from simulator.xml_validation import XmlValidation
from typing import Callable, List, Tuple, Union
from simulator.simulator_logger import SimulatorLoggerWrapper
from logging import WARN, DEBUG
from parameters.vehicle_models import VehicleModelCollection


def create_test_document_with_default_values() -> etree.ElementBase:
    document: etree.ElementBase = etree.Element(DistributionXmlNames.ROOT_TAG, {})

    # item [0]
    connector_link_selection_behaviors_node: etree.ElementBase = \
        etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
            DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.ConnectorLinkSelectionBehaviors.TYPE,
        })
    # item [0][0]
    distribution_node: etree.ElementBase = \
        etree.SubElement(
            connector_link_selection_behaviors_node,
            DistributionXmlNames.ConnectorLinkSelectionBehaviors.TAG, {
                DistributionXmlNames.ConnectorLinkSelectionBehaviors.UUID_ATTR: str(uuid()),
            }
        )
    # item [0][0][0..3]
    for (index, value) in enumerate([
        DistributionXmlNames.ConnectorLinkSelectionBehaviors.NEAREST,
        DistributionXmlNames.ConnectorLinkSelectionBehaviors.FARTHEST,
        DistributionXmlNames.ConnectorLinkSelectionBehaviors.RANDOM,
        DistributionXmlNames.ConnectorLinkSelectionBehaviors.BEST,
    ]):
        etree.SubElement(distribution_node, DistributionXmlNames.EnumShares.SHARE_TAG, {
            DistributionXmlNames.EnumShares.SHARE_VALUE_ATTR: value,
            DistributionXmlNames.EnumShares.SHARE_OCCURRENCE_ATTR: str(10 * (index + 1)),
        })

    # item [1]
    connector_max_positioning_distances_node: etree.ElementBase = \
        etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
            DistributionXmlNames.DistributionSets.TYPE_ATTR:
                DistributionXmlNames.ConnectorMaximumPositioningDistances.TYPE,
        })
    # item [1][0]
    distribution_node = etree.SubElement(
        connector_max_positioning_distances_node, DistributionXmlNames.ConnectorMaximumPositioningDistances.TAG, {
            DistributionXmlNames.DistanceDistributions.UUID_ATTR: str(uuid()),
            DistributionXmlNames.DistanceDistributions.UNITS_ATTR: DistanceUnits.FEET.name,
        })
    # item [1][0][0]
    etree.SubElement(distribution_node, DistributionXmlNames.NormalDistributions.TAG, {
        DistributionXmlNames.NormalDistributions.MEAN_ATTR: '500.0',
        DistributionXmlNames.NormalDistributions.SD_ATTR: '100.0',
    })

    # item [2]
    vehicle_models_node: etree.ElementBase = \
        etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
            DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.VehicleModels.TYPE,
        })
    # item [2][0]
    model_node: etree.ElementBase = \
        etree.SubElement(vehicle_models_node, DistributionXmlNames.VehicleModels.TAG, {
            DistributionXmlNames.VehicleModels.UUID_ATTR: str(uuid()),
        })
    # item [2][0][0..2]
    for (i, vehicle_id) in enumerate([
        'd0a99208-5a31-4744-a08d-ca47af7eabaa',
        '7c9f0966-ac84-4f34-8583-bb88aea0fa03',
        '76450f0b-6b9f-413c-a7f1-adfc467e7c3f',
    ]):
        etree.SubElement(model_node, DistributionXmlNames.Shares.SHARE_TAG, {
            DistributionXmlNames.Shares.SHARE_VALUE_ATTR: vehicle_id,
            DistributionXmlNames.Shares.SHARE_OCCURRENCE_ATTR: str(100 * (i + 1)),
        })

    # item [3]
    colors_node: etree.ElementBase = etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
        DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.Colors.TYPE,
    })
    # item [3][0]
    color_distribution_node: etree.ElementBase = etree.SubElement(colors_node, DistributionXmlNames.Colors.TAG, {
        DistributionXmlNames.Colors.UUID_ATTR: str(uuid()),
    })
    # item [3][0][0..5]
    for color_str in ['#ff0000', '#ff8000', '#ffff00', '#00ff00', '#0000ff', '#00ffff', ]:
        etree.SubElement(color_distribution_node, DistributionXmlNames.Colors.SHARE_TAG, {
            DistributionXmlNames.Colors.SHARE_VALUE_ATTR: color_str,
            DistributionXmlNames.Colors.SHARE_OCCURRENCE_ATTR: '1',
        })

    # item [4]
    acceleration_functions_node: etree.ElementBase = \
        etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
            DistributionXmlNames.DistributionSets.TYPE_ATTR:
                DistributionXmlNames.AccelerationFunctions.TYPE,
        })

    # item [4][0]
    acceleration_distribution_node: etree.ElementBase = \
        etree.SubElement(acceleration_functions_node, DistributionXmlNames.AccelerationFunctions.TAG, {
            DistributionXmlNames.AccelerationFunctions.UUID_ATTR: str(uuid()),
            DistributionXmlNames.AccelerationFunctions.SPEED_UNIT_ATTR: SpeedUnits.MILES_PER_HOUR.name,
            DistributionXmlNames.AccelerationFunctions.ACCELERATION_UNIT_ATTR:
                AccelerationUnits.FEET_PER_SECOND_SQUARED.name,
        })

    # item [4][0][0..1]
    for (speed, mean, standard_deviation) in [
        (0, 10, 2),
        (100, 0, 0),
    ]:
        etree.SubElement(acceleration_distribution_node, DistributionXmlNames.AccelerationFunctions.DP_TAG, {
            DistributionXmlNames.AccelerationFunctions.DP_VELOCITY_ATTR: str(speed),
            DistributionXmlNames.AccelerationFunctions.DP_MEAN_ATTR: str(mean),
            DistributionXmlNames.AccelerationFunctions.DP_STANDARD_DEVIATION_ATTR: str(standard_deviation),
        })

    # item [5]
    maximum_decelerations_node: etree.ElementBase = \
        etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
            DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.DecelerationDistributions.TYPE,
        })
    # item [5][0]
    deceleration_distribution_node: etree.ElementBase = \
        etree.SubElement(maximum_decelerations_node, DistributionXmlNames.AccelerationDistributions.TAG, {
            DistributionXmlNames.AccelerationDistributions.UUID_ATTR: str(uuid()),
            DistributionXmlNames.AccelerationDistributions.UNITS_ATTR: AccelerationUnits.G.name,
        })
    # item [5][0][0]
    empirical_distribution_node: etree.ElementBase = \
        etree.SubElement(deceleration_distribution_node, DistributionXmlNames.EmpiricalDistributions.TAG, {})
    # items [5][0][0][0..3]
    for (probability, value) in [
        (0.0, 0.8),
        (0.15, 0.9),
        (0.85, 1.0),
        (1.0, 1.1),
    ]:
        etree.SubElement(empirical_distribution_node, DistributionXmlNames.EmpiricalDistributions.DATA_POINT_TAG, {
            DistributionXmlNames.EmpiricalDistributions.DATA_POINT_VALUE_ATTR: str(value),
            DistributionXmlNames.EmpiricalDistributions.DATA_POINT_PROBABILITY_ATTR: str(probability),
        })

    # item [6]
    desired_accelerations_node = etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
        DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.DesiredAccelerationDistributions.TYPE,
    })
    # item [6][0]
    distribution_node = \
        etree.SubElement(desired_accelerations_node, DistributionXmlNames.DesiredAccelerationDistributions.TAG, {
            DistributionXmlNames.DesiredAccelerationDistributions.UUID_ATTR: str(uuid()),
        })
    # item [6][0][0]
    etree.SubElement(distribution_node, DistributionXmlNames.NormalDistributions.TAG, {
        DistributionXmlNames.NormalDistributions.MEAN_ATTR: '0.80',
        DistributionXmlNames.NormalDistributions.SD_ATTR: '0.10',
        DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR: '0',
        DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR: '1',
    })

    # item [7]
    desired_decelerations_node = etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
        DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.DesiredDecelerationDistributions.TYPE,
    })
    # item [7][0]
    distribution_node = \
        etree.SubElement(desired_decelerations_node, DistributionXmlNames.DesiredDecelerationDistributions.TAG, {
            DistributionXmlNames.DesiredDecelerationDistributions.UUID_ATTR: str(uuid()),
        })
    # item [7][0][0]
    empirical_node = etree.SubElement(distribution_node, DistributionXmlNames.EmpiricalDistributions.TAG, {})
    # items [7][0][0][0..3]
    for (prob, val) in [
        (0, 0.5),
        (0.15, 0.65),
        (0.85, 0.85),
        (1, 1.0)
    ]:
        etree.SubElement(empirical_node, DistributionXmlNames.EmpiricalDistributions.DATA_POINT_TAG, {
            DistributionXmlNames.EmpiricalDistributions.DATA_POINT_PROBABILITY_ATTR: str(prob),
            DistributionXmlNames.EmpiricalDistributions.DATA_POINT_VALUE_ATTR: str(val),
        })

    # item [8]
    target_speeds_node: etree.ElementBase = etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
        DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.TargetSpeedDistributions.TYPE,
    })
    # item [8][0]
    distribution_node = etree.SubElement(target_speeds_node, DistributionXmlNames.TargetSpeedDistributions.TAG, {
        DistributionXmlNames.TargetSpeedDistributions.UUID_ATTR: str(uuid()),
        DistributionXmlNames.TargetSpeedDistributions.UNITS_ATTR: SpeedUnits.MILES_PER_HOUR.name,
    })
    # item [8][0][0]
    etree.SubElement(distribution_node, DistributionXmlNames.NormalDistributions.TAG, {
        DistributionXmlNames.NormalDistributions.MEAN_ATTR: '50',
        DistributionXmlNames.NormalDistributions.SD_ATTR: '10',
    })

    # item [9]
    speed_deviations_node: etree.ElementBase = etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
        DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.PostedSpeedDeviationDistributions.TYPE,
    })
    # item [9][0]
    distribution_node = \
        etree.SubElement(speed_deviations_node, DistributionXmlNames.PostedSpeedDeviationDistributions.TAG, {
            DistributionXmlNames.PostedSpeedDeviationDistributions.UUID_ATTR: str(uuid()),
            DistributionXmlNames.PostedSpeedDeviationDistributions.UNITS_ATTR: SpeedUnits.KILOMETERS_PER_HOUR.name,
        })
    # item [9][0][0]
    etree.SubElement(distribution_node, DistributionXmlNames.NormalDistributions.TAG, {
        DistributionXmlNames.NormalDistributions.MEAN_ATTR: '5',
        DistributionXmlNames.NormalDistributions.SD_ATTR: '4',
    })

    # item [10]
    non_transit_occupancy_node: etree.ElementBase = \
        etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
            DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.NonTransitOccupancyDistributions.TYPE,
        })
    # item [10][0]
    distribution_node = \
        etree.SubElement(non_transit_occupancy_node, DistributionXmlNames.NonTransitOccupancyDistributions.TAG, {
            DistributionXmlNames.NonTransitOccupancyDistributions.UUID_ATTR: str(uuid()),
        })
    # item [10][0][0]
    etree.SubElement(distribution_node, DistributionXmlNames.PoissonDistributions.ZERO_TRUNCATED_TAG, {
        DistributionXmlNames.PoissonDistributions.LAMBDA_ATTR: '0.5',
    })

    # item [11]
    transit_passengers_node: etree.ElementBase = \
        etree.SubElement(document, DistributionXmlNames.DistributionSets.TAG, {
            DistributionXmlNames.DistributionSets.TYPE_ATTR: DistributionXmlNames.TransitPassengerDistributions.TYPE,
        })
    # item [11][0]
    distribution_node = \
        etree.SubElement(transit_passengers_node, DistributionXmlNames.TransitPassengerDistributions.TAG, {
            DistributionXmlNames.TransitPassengerDistributions.UUID_ATTR: str(uuid()),
        })
    # item [11][0][0]
    etree.SubElement(distribution_node, DistributionXmlNames.PoissonDistributions.POISSON_TAG, {
        DistributionXmlNames.PoissonDistributions.LAMBDA_ATTR: '10',
    })

    return document


dummy_string_value: str = 'a string to fill the blank'


def create_test_document_with_custom_values() -> etree.ElementBase:
    # start with default values, then make more specific
    document: etree.ElementBase = create_test_document_with_default_values()

    document[0][0].attrib[DistributionXmlNames.ConnectorLinkSelectionBehaviors.NAME_ATTR] = dummy_string_value
    document[1][0].attrib[DistributionXmlNames.ConnectorMaximumPositioningDistances.NAME_ATTR] = dummy_string_value

    return document


class TestsForDistributions(unittest.TestCase):
    def test_that_invalid_document_raises_exception(self):
        temp_file_path: str

        with NamedTemporaryFile(delete=False) as fp:
            document_root: etree.ElementBase = etree.parse(DefaultXmlFiles.DISTRIBUTIONS_FILE).getroot()
            first_child: etree.ElementBase = document_root[0]
            document_root.remove(first_child)
            fp.write(etree.tostring(document_root))
            temp_file_path = fp.name
            fp.close()

        def thrower():
            Distributions.process_file(temp_file_path)

        try:
            self.assertRaises(RuntimeError, thrower)
        finally:
            os.remove(temp_file_path)

    def test_that_mock_documents_validate(self):
        default_doc: etree.ElementBase = create_test_document_with_default_values()
        custom_doc: etree.ElementBase = create_test_document_with_custom_values()
        schema: etree.XMLSchema = etree.XMLSchema(etree.parse(XmlValidation.DISTRIBUTIONS_XSD))

        self.assertTrue(schema.validate(default_doc))
        self.assertTrue(schema.validate(custom_doc))


class TestOnDocument(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.default_doc_root: etree.ElementBase = create_test_document_with_default_values()
        cls.custom_doc_root: etree.ElementBase = create_test_document_with_custom_values()
        VehicleModelCollection.read_from_xml(etree.parse(DefaultXmlFiles.VEHICLE_MODELS_FILE).getroot())

    def tearDown(self) -> None:
        Distributions.reset()


class TestsForDefaultValues(TestOnDocument):
    def setUp(self) -> None:
        Distributions.read_from_xml(self.default_doc_root, filename='testing generated file')

    def tests_for_connector_link_selection_behaviors(self):
        guid: str = self.default_doc_root[0][0].attrib[DistributionXmlNames.ConnectorLinkSelectionBehaviors.UUID_ATTR]
        self.assertEqual(Distributions.connector_link_selection_behaviors()[guid].name, '')

    def tests_for_connector_max_positioning_distances(self):
        guid: str = self.default_doc_root[1][0].attrib[
            DistributionXmlNames.ConnectorMaximumPositioningDistances.UUID_ATTR
        ]
        self.assertEqual(Distributions.connector_max_positioning_distances()[guid].name, '')

    def tests_for_vehicle_model_distributions(self):
        guid: str = self.default_doc_root[2][0].attrib[
            DistributionXmlNames.VehicleModels.UUID_ATTR
        ]
        vehicle_model = Distributions.vehicle_models()[guid]
        self.assertEqual(vehicle_model.uuid, guid)
        self.assertEqual(vehicle_model.name, '')

    def tests_for_color_distributions(self):
        guid: str = self.default_doc_root[3][0].attrib[DistributionXmlNames.Colors.UUID_ATTR]
        color_distribution = Distributions.colors()[guid]
        self.assertEqual(color_distribution.uuid, guid)
        self.assertEqual(color_distribution.name, '')

    def tests_for_acceleration_functions(self):
        guid: str = self.default_doc_root[4][0].attrib[DistributionXmlNames.AccelerationFunctions.UUID_ATTR]
        acceleration_function = Distributions.max_acceleration_functions()[guid]
        self.assertEqual(acceleration_function.uuid, guid)
        self.assertEqual(acceleration_function.name, '')


class TestsForSpecifiedValues(TestOnDocument):
    def setUp(self) -> None:
        Distributions.read_from_xml(self.custom_doc_root, filename='testing generated file')

    def check_uuid_is_correct(self, collection_getter: Callable[[], DistributionSet[T]], collection_index: int) -> str:
        guid: str = self.custom_doc_root[collection_index][0].attrib[DistributionXmlNames.GenericNames.UUID_ATTR]
        self.assertEqual(collection_getter()[guid].uuid, guid)
        return guid

    def tests_for_connector_link_selection_behaviors(self):
        guid: str = self.check_uuid_is_correct(Distributions.connector_link_selection_behaviors, 0)
        distribution: StringDistribution = Distributions.connector_link_selection_behaviors()[guid]
        all_shares: List[StringDistribution.ShareCollection.ShareViewer] = \
            distribution.get_share_collection().get_all_shares()
        expected_shares: List[Tuple[str, float]] = [
            (DistributionXmlNames.ConnectorLinkSelectionBehaviors.NEAREST, 10),
            (DistributionXmlNames.ConnectorLinkSelectionBehaviors.FARTHEST, 20),
            (DistributionXmlNames.ConnectorLinkSelectionBehaviors.RANDOM, 30),
            (DistributionXmlNames.ConnectorLinkSelectionBehaviors.BEST, 40),
        ]
        for (value, occurrence) in expected_shares:
            self.assertEqual(occurrence, list(filter(lambda share: share.value == value, all_shares))[0].occurrence)

        expected_values: List[Tuple[float, str]] = [
            (0.0000, DistributionXmlNames.ConnectorLinkSelectionBehaviors.BEST),
            (0.3999, DistributionXmlNames.ConnectorLinkSelectionBehaviors.BEST),
            (0.4001, DistributionXmlNames.ConnectorLinkSelectionBehaviors.FARTHEST),
            (0.5999, DistributionXmlNames.ConnectorLinkSelectionBehaviors.FARTHEST),
            (0.6001, DistributionXmlNames.ConnectorLinkSelectionBehaviors.NEAREST),
            (0.6999, DistributionXmlNames.ConnectorLinkSelectionBehaviors.NEAREST),
            (0.7001, DistributionXmlNames.ConnectorLinkSelectionBehaviors.RANDOM),
            (1.0000, DistributionXmlNames.ConnectorLinkSelectionBehaviors.RANDOM),
        ]
        for (parameter, value) in expected_values:
            self.assertEqual(Distributions.connector_link_selection_behaviors()[guid].get_value(parameter), value)

        self.assertEqual(distribution.name, dummy_string_value)

    def get_CMPD_uuid(self) -> str:
        return self.custom_doc_root[1][0].attrib[DistributionXmlNames.ConnectorMaximumPositioningDistances.UUID_ATTR]

    def test_that_CMPD_units_are_correct(self) -> None:
        guid: str = self.get_CMPD_uuid()
        dist: DistanceDistribution = Distributions.connector_max_positioning_distances()[guid]
        self.assertEqual(dist.units, DistanceUnits.FEET)

    def test_that_vehicle_model_name_is_correct(self):
        guid: str = self.custom_doc_root[2][0].attrib[DistributionXmlNames.VehicleModels.UUID_ATTR]
        self.custom_doc_root[2][0].attrib[DistributionXmlNames.VehicleModels.NAME_ATTR] = dummy_string_value
        Distributions.read_from_xml(self.custom_doc_root)
        self.assertEqual(Distributions.vehicle_models()[guid].name, dummy_string_value)

    def test_that_vehicle_model_value_is_correct(self):
        guid: str = self.custom_doc_root[2][0].attrib[DistributionXmlNames.VehicleModels.UUID_ATTR]

        # 76450f0b-6b9f-413c-a7f1-adfc467e7c3f: 300 = [0.0, 0.5]
        # 7c9f0966-ac84-4f34-8583-bb88aea0fa03: 200 = [0.5, 0.8333]
        # d0a99208-5a31-4744-a08d-ca47af7eabaa: 100 = [0.8333, 1.0]
        test_tuples = [
            (0.1, '76450f0b-6b9f-413c-a7f1-adfc467e7c3f'),
            (0.4999, '76450f0b-6b9f-413c-a7f1-adfc467e7c3f'),
            (0.5001, '7c9f0966-ac84-4f34-8583-bb88aea0fa03'),
            (0.8333, '7c9f0966-ac84-4f34-8583-bb88aea0fa03'),
            (0.8334, 'd0a99208-5a31-4744-a08d-ca47af7eabaa'),
            (0.99, 'd0a99208-5a31-4744-a08d-ca47af7eabaa'),
        ]
        for (parameter, expected_value) in test_tuples:
            self.assertEqual(Distributions.vehicle_models()[guid].get_value(parameter), expected_value)

    def add_distribution_with_all_zero_shares(self,
                                              distribution_set_index: int,
                                              template_index: int) -> etree.ElementBase:
        distribution_original: etree.ElementBase = self.custom_doc_root[distribution_set_index][template_index]
        distribution_copy: etree.ElementBase = etree.fromstring(etree.tostring(distribution_original))
        for share in distribution_copy.iterfind(DistributionXmlNames.EnumShares.SHARE_TAG):
            share.attrib[DistributionXmlNames.EnumShares.SHARE_OCCURRENCE_ATTR] = '0'

        self.custom_doc_root[distribution_set_index].append(distribution_copy)

        return distribution_copy

    def test_that_empty_vehicle_model_distribution_raises_exception(self):
        distribution_copy: etree.ElementBase = self.add_distribution_with_all_zero_shares(2, 0)

        def thrower():
            Distributions.read_from_xml(self.custom_doc_root)

        try:
            self.assertRaises(ValueError, thrower)
        finally:
            self.custom_doc_root[2].remove(distribution_copy)

    def test_color_name(self):
        self.custom_doc_root[3][0].attrib[DistributionXmlNames.Colors.NAME_ATTR] = dummy_string_value
        Distributions.read_from_xml(self.custom_doc_root)
        guid: str = self.get_color_guid()
        self.assertEqual(Distributions.colors()[guid].name, dummy_string_value)

    def test_that_empty_color_distribution_raises_exception(self):
        distribution_copy: etree.ElementBase = self.add_distribution_with_all_zero_shares(3, 0)

        def thrower():
            Distributions.read_from_xml(self.custom_doc_root)

        try:
            self.assertRaises(ValueError, thrower)
        finally:
            self.custom_doc_root[3].remove(distribution_copy)

    def get_color_guid(self) -> str:
        return self.custom_doc_root[3][0].attrib[DistributionXmlNames.Colors.UUID_ATTR]

    def test_color_values(self):
        colors: List[str] = ['#0000ff', '#00ff00', '#00ffff', '#ff0000', '#ff8000', '#ffff00']  # equally weighted
        distribution: ColorDistribution = Distributions.colors()[self.get_color_guid()]
        for (index, color) in enumerate(colors):
            bin_middle_point: float = (2.0 * index + 1.0) / 12.0
            self.assertEqual(distribution.get_value(bin_middle_point - 0.08), color)
            self.assertEqual(distribution.get_value(bin_middle_point + 0.08), color)

    def get_max_acceleration_guid(self) -> str:
        return self.custom_doc_root[4][0].attrib[DistributionXmlNames.AccelerationFunctions.UUID_ATTR]

    def test_max_acceleration_name_reads_correctly(self):
        try:
            self.custom_doc_root[4][0].attrib[DistributionXmlNames.AccelerationFunctions.NAME_ATTR] = dummy_string_value
            Distributions.read_from_xml(self.custom_doc_root)
            guid: str = self.get_max_acceleration_guid()
            self.assertEqual(Distributions.max_acceleration_functions()[guid].name, dummy_string_value)
        finally:
            self.custom_doc_root[4][0].attrib.pop(DistributionXmlNames.AccelerationFunctions.NAME_ATTR)

    def test_max_acceleration_values(self):
        guid: str = self.get_max_acceleration_guid()
        distribution: AccelerationFunction = Distributions.max_acceleration_functions()[guid]
        test_tuples: List[Tuple[float, float, float]] = [
            (0.10, 0.0, 7.44),  # (pure, mph, ft/s^2)
            (0.80, 0.0, 11.68),
            (0.22, 20.0, 6.76),
            (0.91, 40.0, 7.61),
            (0.69, 80.0, 2.20)
        ]
        for (parameter, speed, expected_result) in test_tuples:
            self.assertAlmostEqual(
                AccelerationUnits.FEET_PER_SECOND_SQUARED.convert_to_this_unit(
                    distribution.get_value(
                        parameter,
                        SpeedUnits.MILES_PER_HOUR.convert_to_base_units(speed)
                    )
                ),
                expected_result,
                2
            )

    def test_that_non_monotonic_decreasing_max_acceleration_warns(self):
        test_doc: etree.ElementBase = create_test_document_with_custom_values()
        distribution_element: etree.ElementBase = etree.SubElement(
            test_doc[4],
            DistributionXmlNames.AccelerationFunctions.TAG, {
                DistributionXmlNames.AccelerationFunctions.ACCELERATION_UNIT_ATTR:
                    AccelerationUnits.FEET_PER_SECOND_SQUARED.name,
                DistributionXmlNames.AccelerationFunctions.UUID_ATTR: str(uuid()),
                DistributionXmlNames.AccelerationFunctions.SPEED_UNIT_ATTR: SpeedUnits.MILES_PER_HOUR.name,
            }
        )
        data_points: List[Tuple[float, float, float]] = [
            (0, 10, 2),
            (30, 7, 2),
            (40, 8, 2),
            (100, 0, 0),
        ]
        for (speed, mean_acceleration, sd_acceleration) in data_points:
            etree.SubElement(distribution_element, DistributionXmlNames.AccelerationFunctions.DP_TAG, {
                DistributionXmlNames.AccelerationFunctions.DP_VELOCITY_ATTR: str(speed),
                DistributionXmlNames.AccelerationFunctions.DP_MEAN_ATTR: str(mean_acceleration),
                DistributionXmlNames.AccelerationFunctions.DP_STANDARD_DEVIATION_ATTR: str(sd_acceleration)
            })

        with self.assertLogs(SimulatorLoggerWrapper.logger(), WARN):
            Distributions.read_from_xml(test_doc)

    def test_that_unequal_domains_of_mean_and_sd_parameters_raises_error(self): pass


class TestsForMessages(TestOnDocument):
    def tests_for_connector_link_selection_behaviors(self):
        for share in self.default_doc_root[0][0]:
            share.attrib[DistributionXmlNames.Shares.SHARE_OCCURRENCE_ATTR] = '0'

        def thrower():
            Distributions.read_from_xml(self.default_doc_root, filename='test synthesized document')

        self.assertRaises(ValueError, thrower)

    def test_that_CMPD_illogical_extrema_raises_error(self):
        self.default_doc_root[1][0][0].attrib[DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR] = '400'
        self.default_doc_root[1][0][0].attrib[DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR] = '300'

        def thrower():
            Distributions.read_from_xml(self.default_doc_root, filename='test synthesized document')

        self.assertRaises(ValueError, thrower)

    def test_that_CMPD_emits_warning(self):
        def set_and_test_extrema(min_value: Union[float, None],
                                 max_value: Union[float, None],
                                 logging_expected: bool):
            def remove_attribute(attr_name: str) -> None:
                if attr_name in distribution_under_test.attrib:
                    distribution_under_test.attrib.pop(attr_name)

            def set_attribute(attr_name: str, value: float) -> None:
                distribution_under_test.attrib[attr_name] = str(value)

            if min_value is None:
                remove_attribute(DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR)
            else:
                set_attribute(DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR, min_value)

            if max_value is None:
                remove_attribute(DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR)
            else:
                set_attribute(DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR, max_value)

            if logging_expected:
                with self.assertLogs(SimulatorLoggerWrapper.logger(), WARN):
                    Distributions.read_from_xml(self.default_doc_root)
            else:
                with self.assertLogs(SimulatorLoggerWrapper.logger(), DEBUG) as cm:
                    Distributions.read_from_xml(self.default_doc_root)
                    # if this is not true, we can't just assume item 0 below
                    self.assertEqual(len(cm.records), 1)
                    # if it's warn we have a problem
                    self.assertEqual(cm.records[0].levelno, DEBUG)

        distribution_under_test: etree.ElementBase = self.default_doc_root[1][0][0]

        # for when min_value is specified, max_value is not specified, and
        # the resulting restrictions eliminate more a quarter of the distribution
        set_and_test_extrema(432.865, None, True)
        set_and_test_extrema(432.5, None, False)

        # for when min_value is not specified, max_value is specified, and
        # the resulting restrictions eliminate more a quarter of the distribution
        set_and_test_extrema(None, 567.4, True)
        set_and_test_extrema(None, 567.5, False)

        # for when both min_value and max_value are specified, and
        # the resulting restrictions eliminate more half of the distribution
        set_and_test_extrema(432.865, 567.4, True)
        set_and_test_extrema(432.5, 567.5, False)
        set_and_test_extrema(294.63, 505.01, True)
        set_and_test_extrema(294.62, 505.02, False)


class TestsForNormalDistributions(TestOnDocument):
    def test_that_CMPD_values_are_correct(self) -> None:
        Distributions.read_from_xml(self.custom_doc_root, filename='testing generated file')
        guid: str = self.custom_doc_root[1][0].attrib[
            DistributionXmlNames.ConnectorMaximumPositioningDistances.UUID_ATTR
        ]
        dist: DistanceDistribution = Distributions.connector_max_positioning_distances()[guid]
        test_tuples = [
            (0.10, DistanceUnits.FEET.convert_to_base_units(371.85)),
            (0.50, DistanceUnits.FEET.convert_to_base_units(500)),
            (0.80, DistanceUnits.FEET.convert_to_base_units(584.15)),
        ]
        for (probability, value) in test_tuples:
            self.assertAlmostEqual(dist.get_value(probability), value, 2)

    def _reset_CMPD_extrema(self):
        to_modify: etree.ElementBase = self.default_doc_root[1][0][0]
        if DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR in to_modify.attrib:
            to_modify.attrib.pop(DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR)
        if DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR in to_modify.attrib:
            to_modify.attrib.pop(DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR)
        if DistributionXmlNames.NormalDistributions.REVERSE_ATTR in to_modify.attrib:
            to_modify.attrib.pop(DistributionXmlNames.NormalDistributions.REVERSE_ATTR)

    def test_that_CMPD_truncated_min_values_are_correct(self) -> None:
        self._reset_CMPD_extrema()
        self.default_doc_root[1][0][0].attrib[DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR] = '400'
        Distributions.read_from_xml(self.default_doc_root)

        guid: str = self.default_doc_root[1][0].attrib[
            DistributionXmlNames.ConnectorMaximumPositioningDistances.UUID_ATTR
        ]
        dist: DistanceDistribution = Distributions.connector_max_positioning_distances()[guid]
        test_tuples = [
            (0.10, DistanceUnits.FEET.convert_to_base_units(400)),
            (0.50, DistanceUnits.FEET.convert_to_base_units(500)),
            (0.80, DistanceUnits.FEET.convert_to_base_units(584.15)),
        ]
        for (probability, value) in test_tuples:
            self.assertAlmostEqual(dist.get_value(probability), value, 2)

    def test_that_CMPD_truncated_max_values_are_correct(self):
        self._reset_CMPD_extrema()
        self.default_doc_root[1][0][0].attrib[DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR] = '575'
        Distributions.read_from_xml(self.default_doc_root)

        guid: str = self.default_doc_root[1][0].attrib[
            DistributionXmlNames.ConnectorMaximumPositioningDistances.UUID_ATTR
        ]
        dist: DistanceDistribution = Distributions.connector_max_positioning_distances()[guid]
        test_tuples = [
            (0.10, DistanceUnits.FEET.convert_to_base_units(371.85)),
            (0.50, DistanceUnits.FEET.convert_to_base_units(500)),
            (0.80, DistanceUnits.FEET.convert_to_base_units(575)),
        ]
        for (probability, value) in test_tuples:
            self.assertAlmostEqual(dist.get_value(probability), value, 2)

    def test_that_CMPD_two_way_truncation_values_are_correct(self):
        self._reset_CMPD_extrema()
        self.default_doc_root[1][0][0].attrib[DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR] = '400'
        self.default_doc_root[1][0][0].attrib[DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR] = '575'
        Distributions.read_from_xml(self.default_doc_root)

        guid: str = self.default_doc_root[1][0].attrib[
            DistributionXmlNames.ConnectorMaximumPositioningDistances.UUID_ATTR
        ]
        dist: DistanceDistribution = Distributions.connector_max_positioning_distances()[guid]
        test_tuples = [
            (0.10, DistanceUnits.FEET.convert_to_base_units(400)),
            (0.50, DistanceUnits.FEET.convert_to_base_units(500)),
            (0.80, DistanceUnits.FEET.convert_to_base_units(575)),
        ]
        for (probability, value) in test_tuples:
            self.assertAlmostEqual(dist.get_value(probability), value, 2)

    def test_that_reversed_normal_distribution_works(self):
        self._reset_CMPD_extrema()
        self.default_doc_root[1][0][0].attrib[DistributionXmlNames.NormalDistributions.REVERSE_ATTR] = 'true'
        Distributions.read_from_xml(self.default_doc_root)

        guid: str = self.default_doc_root[1][0].attrib[
            DistributionXmlNames.ConnectorMaximumPositioningDistances.UUID_ATTR
        ]
        dist: DistanceDistribution = Distributions.connector_max_positioning_distances()[guid]
        test_tuples = [
            (0.10, DistanceUnits.FEET.convert_to_base_units(628.16)),
            (0.50, DistanceUnits.FEET.convert_to_base_units(500)),
            (0.80, DistanceUnits.FEET.convert_to_base_units(415.84)),
        ]
        for (probability, value) in test_tuples:
            self.assertAlmostEqual(dist.get_value(probability), value, 2)


if __name__ == '__main__':
    unittest.main()
