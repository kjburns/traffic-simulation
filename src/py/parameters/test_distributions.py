import unittest
from tempfile import NamedTemporaryFile
from lxml import etree
from simulator.default_xml_files import DefaultXmlFiles
from parameters.distributions import Distributions, DistributionXmlNames, T, DistributionSet, StringDistribution
import os
from uuid import uuid4 as uuid
from parameters.units import DistanceUnits, SpeedUnits, AccelerationUnits
from simulator.xml_validation import XmlValidation
from typing import Callable, List, Tuple


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
            DistributionXmlNames.DistanceDistributions.UNITS_ATTR: DistanceUnits.METERS.name,
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

    def tearDown(self) -> None:
        Distributions.reset()


class TestsForDefaultValues(TestOnDocument):
    def setUp(self) -> None:
        Distributions.read_from_xml(self.default_doc_root, filename='testing generated file')

    def tests_for_connector_link_selection_behaviors(self):
        guid: str = self.default_doc_root[0][0].attrib[DistributionXmlNames.ConnectorLinkSelectionBehaviors.UUID_ATTR]
        self.assertEqual(Distributions.connector_link_selection_behaviors()[guid].name, '')


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


class TestsForMessages(TestOnDocument):
    def tests_for_connector_link_selection_behaviors(self):
        for share in self.default_doc_root[0][0]:
            share.attrib[DistributionXmlNames.Shares.SHARE_OCCURRENCE_ATTR] = '0'

        def thrower():
            Distributions.read_from_xml(self.default_doc_root, filename='test synthesized document')

        self.assertRaises(ValueError, thrower)


if __name__ == '__main__':
    unittest.main()
