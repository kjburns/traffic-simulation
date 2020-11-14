from uuid import uuid4 as uuid
import unittest
from lxml import etree


class NetworkConstants:
    ROOT_TAG = 'network'
    LAYOUT_UNITS_ATTR = 'layout-units'
    SPEED_UNITS_ATTR = 'speed-limit-units'
    VERSION_ATTR = 'version'


class RoadConstants:
    COLLECTION_TAG = 'roads'
    TAG = 'road'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    BEHAVIOR_ATTR = 'behavior'
    SPEED_LIMIT_ATTR = 'speed-limit'
    CHAIN_TAG = 'chain'
    CHAIN_LENGTH_ATTR = 'length'
    CHAIN_POINTS_ATTR = 'points'
    LANES_COLLECTION_TAG = 'lanes'
    LANE_TAG = 'lane'
    LANE_ORDINAL_ATTR = 'ordinal'
    LANE_WIDTH_ATTR = 'width'
    LANE_MAY_MOVE_LEFT_ATTR = 'may-move-left'
    LANE_MAY_MOVE_RIGHT_ATTR = 'may-move-right'
    LANE_POLICY_TAG = 'policy'
    LANE_POLICY_ID_ATTR = 'id'
    LANE_POLICY_EXCEPT_TAG = 'except'
    LANE_POLICY_EXCEPT_POLICY_ATTR = 'policy'
    LANE_POLICY_EXCEPT_START_ATTR = 'start-time'
    LANE_POLICY_EXCEPT_END_ATTR = 'end-time'
    POCKETS_COLLECTION_TAG = 'pockets'
    POCKET_TAG = 'pocket'
    POCKET_SIDE_ATTR = 'side'
    POCKET_START_ORD_ATTR = 'start-ord'
    POCKET_END_ORD_ATTR = 'end-ord'
    POCKET_START_TAPER_ATTR = 'start-taper'
    POCKET_END_TAPER_ATTR = 'end-taper'
    POCKET_LANE_COUNT_ATTR = 'lane-count'


def create_clean_road_node() -> etree.ElementBase:
    node: etree.ElementBase = etree.Element(RoadConstants.TAG, {
        RoadConstants.UUID_ATTR: str(uuid()),
        RoadConstants.BEHAVIOR_ATTR: str(uuid()),
        RoadConstants.SPEED_LIMIT_ATTR: '35',
    })

    # hit all four quadrants
    etree.ElementBase = etree.SubElement(node, RoadConstants.CHAIN_TAG, {
        RoadConstants.CHAIN_LENGTH_ATTR: '300',
        RoadConstants.CHAIN_POINTS_ATTR: '-50.5,-50.5 -50.5,49.5 50,50 50,-50',
    })

    # let's do two lanes
    lane_policy_id: str = str(uuid())
    lanes_collection_node: etree.ElementBase = etree.SubElement(node, RoadConstants.LANES_COLLECTION_TAG)
    for ordinal in range(2):
        lane_element: etree.ElementBase = etree.SubElement(lanes_collection_node, RoadConstants.LANE_TAG, {
            RoadConstants.LANE_ORDINAL_ATTR: str(ordinal),
            RoadConstants.LANE_WIDTH_ATTR: '12',
        })
        etree.SubElement(lane_element, RoadConstants.LANE_POLICY_TAG, {
            RoadConstants.LANE_POLICY_ID_ATTR: lane_policy_id,
        })

    # no pockets
    etree.SubElement(node, RoadConstants.POCKETS_COLLECTION_TAG)

    return node


class CleanDocument:
    def __init__(self):
        ns_map = {"xsi": 'http://www.w3.org/2001/XMLSchema-instance'}

        self._document_root: etree.ElementBase = etree.Element(NetworkConstants.ROOT_TAG, {
            NetworkConstants.VERSION_ATTR: '1',
            '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation': '../network.xsd',
            NetworkConstants.LAYOUT_UNITS_ATTR: 'feet',
            NetworkConstants.SPEED_UNITS_ATTR: 'miles-per-hour'
        }, nsmap=ns_map)

        self._roads_node: etree.ElementBase = etree.SubElement(self._document_root, RoadConstants.COLLECTION_TAG)
        self._roads_node.append(create_clean_road_node())

    def print_document_to_console(self):
        print(etree.tostring(self._document_root,
                             xml_declaration=False, pretty_print=True, encoding='unicode'))

    def write_document_to_file(self, filename):
        fp = open(filename, 'w')
        fp.write(etree.tostring(self._document_root,
                                pretty_print=True, encoding='unicode'))
        fp.close()

    def validate(self) -> bool:
        xs_doc = etree.parse('../network.xsd')
        xsd = etree.XMLSchema(xs_doc)
        document = etree.ElementTree(self._document_root)
        return xsd.validate(document)

    def get_root_node(self):
        return self._document_root

    def get_roads_node(self):
        return self._roads_node


class TestHelper(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanDocument()

    def check_effect_of_removing_field(self, element: etree.ElementBase,
                                       attr_name: str, expected_validation_result: bool) -> None:
        if attr_name in element.attrib:
            element.attrib.pop(attr_name)
        self.assertEqual(self._doc.validate(), expected_validation_result)

    def check_value_of_uuid_field(self, element: etree.ElementBase, attr_name: str):
        test_tuples = [
            ('', False),
            ('a45a7f03-ae05-44f7-aa68-0f3e7b15cebe', True),
            ('a45a7f03-ae05-44f7-aa68-0f3e7b15gage', False),
        ]

        for (value, expected_result) in test_tuples:
            element.attrib[attr_name] = value
            self.assertEqual(self._doc.validate(), expected_result)


class TestsForNetworkDocument(TestHelper):
    def setUp(self) -> None:
        super().setUp()
        self._target_node = self._doc.get_root_node()

    def test_that_clean_document_validates(self):
        self.assertTrue(self._doc.validate())

    def test_version_attr(self):
        test_tuples = [
            (1, True),
            (0, False),
            (2, False),
            ('', False),
            ('not a number', False),
        ]
        for (value, expected_result) in test_tuples:
            self._target_node.attrib[NetworkConstants.VERSION_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

        self.check_effect_of_removing_field(self._target_node, NetworkConstants.VERSION_ATTR, False)

    def test_speed_unit_attr(self):
        acceptable_values = ['miles-per-hour', 'kilometers-per-hour']
        for value in acceptable_values:
            self._target_node.attrib[NetworkConstants.SPEED_UNITS_ATTR] = value
            self.assertTrue(self._doc.validate())

        unacceptable_values = ['', 'mph', 'km/h']
        for value in unacceptable_values:
            self._target_node.attrib[NetworkConstants.LAYOUT_UNITS_ATTR] = value
            self.assertFalse(self._doc.validate())

    def test_layout_unit_attr(self):
        acceptable_values = ['feet', 'meters']
        for value in acceptable_values:
            self._target_node.attrib[NetworkConstants.LAYOUT_UNITS_ATTR] = value
            self.assertTrue(self._doc.validate())

        unacceptable_values = ['', 'metres', 'inches']
        for value in unacceptable_values:
            self._target_node.attrib[NetworkConstants.LAYOUT_UNITS_ATTR] = value
            self.assertFalse(self._doc.validate())

    def test_that_roads_node_is_required(self):
        self._doc.get_root_node().remove(self._doc.get_roads_node())
        self.assertFalse(self._doc.validate())


class TestsForRoads(TestHelper):
    def setUp(self) -> None:
        super().setUp()
        self._target_node = self._doc.get_roads_node()

    def test_instance_count(self):
        test_tuples = [
            (0, False),
            (1, True),
            (100, True),
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = [create_clean_road_node() for _ in range(count)]
            self.assertEqual(self._doc.validate(), expected_result)

    def test_road_name_attr(self):
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        self.check_effect_of_removing_field(node, RoadConstants.NAME_ATTR, True)

        acceptable_names = ['', 'Main Street', '0012']
        for name in acceptable_names:
            node.attrib[RoadConstants.NAME_ATTR] = name
            self.assertTrue(self._doc.validate())

    def test_road_uuid_attr(self):
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        self.check_value_of_uuid_field(node, RoadConstants.UUID_ATTR)
        self.check_effect_of_removing_field(node, RoadConstants.UUID_ATTR, False)

    def test_road_behavior_attr(self):
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        self.check_value_of_uuid_field(node, RoadConstants.BEHAVIOR_ATTR)
        self.check_effect_of_removing_field(node, RoadConstants.BEHAVIOR_ATTR, False)

    def test_road_speed_limit_attr(self):
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        test_tuples = [
            (-1, False),
            (0, False),
            (5, True),
            (55, True),
            (100, True),
            (160, True),
        ]
        for (value, expected_result) in test_tuples:
            node.attrib[RoadConstants.SPEED_LIMIT_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

        self.check_effect_of_removing_field(node, RoadConstants.SPEED_LIMIT_ATTR, False)


if __name__ == '__main__':
    unittest.main()
