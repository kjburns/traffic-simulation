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
        self.doc = CleanDocument()

    def check_effect_of_removing_field(self, element: etree.ElementBase,
                                       attr_name: str, expected_validation_result: bool) -> None:
        if attr_name in element.attrib:
            element.attrib.pop(attr_name)
        self.assertEqual(self.doc.validate(), expected_validation_result)

    def check_value_of_uuid_field(self, element: etree.ElementBase, attr_name: str):
        test_tuples = [
            ('', False),
            ('a45a7f03-ae05-44f7-aa68-0f3e7b15cebe', True),
            ('a45a7f03-ae05-44f7-aa68-0f3e7b15gage', False),
        ]

        for (value, expected_result) in test_tuples:
            element.attrib[attr_name] = value
            self.assertEqual(self.doc.validate(), expected_result)


class TestsForNetworkDocument(TestHelper):
    def setUp(self) -> None:
        super().setUp()
        self._target_node = self.doc.get_root_node()

    def test_that_clean_document_validates(self):
        self.assertTrue(self.doc.validate())

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
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(self._target_node, NetworkConstants.VERSION_ATTR, False)

    def test_speed_unit_attr(self):
        acceptable_values = ['miles-per-hour', 'kilometers-per-hour']
        for value in acceptable_values:
            self._target_node.attrib[NetworkConstants.SPEED_UNITS_ATTR] = value
            self.assertTrue(self.doc.validate())

        unacceptable_values = ['', 'mph', 'km/h']
        for value in unacceptable_values:
            self._target_node.attrib[NetworkConstants.LAYOUT_UNITS_ATTR] = value
            self.assertFalse(self.doc.validate())

    def test_layout_unit_attr(self):
        acceptable_values = ['feet', 'meters']
        for value in acceptable_values:
            self._target_node.attrib[NetworkConstants.LAYOUT_UNITS_ATTR] = value
            self.assertTrue(self.doc.validate())

        unacceptable_values = ['', 'metres', 'inches']
        for value in unacceptable_values:
            self._target_node.attrib[NetworkConstants.LAYOUT_UNITS_ATTR] = value
            self.assertFalse(self.doc.validate())

    def test_that_roads_node_is_required(self):
        self.doc.get_root_node().remove(self.doc.get_roads_node())
        self.assertFalse(self.doc.validate())


class TestsForRoads(TestHelper):
    def setUp(self) -> None:
        super().setUp()
        self._target_node = self.doc.get_roads_node()

    def test_instance_count(self):
        test_tuples = [
            (0, False),
            (1, True),
            (100, True),
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = [create_clean_road_node() for _ in range(count)]
            self.assertEqual(self.doc.validate(), expected_result)

    def test_road_name_attr(self):
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        self.check_effect_of_removing_field(node, RoadConstants.NAME_ATTR, True)

        acceptable_names = ['', 'Main Street', '0012']
        for name in acceptable_names:
            node.attrib[RoadConstants.NAME_ATTR] = name
            self.assertTrue(self.doc.validate())

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
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(node, RoadConstants.SPEED_LIMIT_ATTR, False)

    def test_that_sub_elements_are_required(self):
        collections = [
            RoadConstants.LANES_COLLECTION_TAG,
            RoadConstants.POCKETS_COLLECTION_TAG,
            RoadConstants.CHAIN_TAG,
        ]
        for collection in collections:
            self.doc.get_roads_node()[:] = []
            node: etree.ElementBase = create_clean_road_node()
            self.doc.get_roads_node().append(node)
            collection_node: etree.ElementBase = node.find(collection)
            node.remove(collection_node)
            self.assertFalse(self.doc.validate())

    @staticmethod
    def create_lane_element(ordinal: int) -> etree.ElementBase:
        node: etree._ElementBase = etree.Element(RoadConstants.LANE_TAG, {
            RoadConstants.LANE_ORDINAL_ATTR: str(ordinal),
            RoadConstants.LANE_WIDTH_ATTR: '12',
        })
        etree.SubElement(node, RoadConstants.LANE_POLICY_TAG, {
            RoadConstants.LANE_POLICY_ID_ATTR: str(uuid()),
        })

        return node

    def test_lane_counts(self):
        road: etree.ElementBase = create_clean_road_node()
        self._target_node.append(road)
        lanes_collection = road.find(RoadConstants.LANES_COLLECTION_TAG)
        test_tuples = [
            (0, False),
            (1, True),
            (2, True),
            (9, True),
        ]
        for (count, expected_value) in test_tuples:
            lanes_collection[:] = [TestsForRoads.create_lane_element(i) for i in range(count)]
            self.assertEqual(self.doc.validate(), expected_value)

    def test_lane_ordinal_attr(self):
        road: etree.ElementBase = create_clean_road_node()
        self._target_node.append(road)
        lane: etree.ElementBase = self.create_lane_element(0)
        road.find(RoadConstants.LANES_COLLECTION_TAG)[:] = [lane]
        test_tuples = [
            (0, True),
            (4, True),
            (-2, False),
        ]
        for (value, expected_result) in test_tuples:
            lane.attrib[RoadConstants.LANE_ORDINAL_ATTR] = str(value)
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(lane, RoadConstants.LANE_ORDINAL_ATTR, False)

    def test_lane_width_attr(self):
        road: etree.ElementBase = create_clean_road_node()
        self._target_node.append(road)
        lane: etree.ElementBase = self.create_lane_element(0)
        road.find(RoadConstants.LANES_COLLECTION_TAG)[:] = [lane]
        test_tuples = [
            (0, False),
            (4, True),
            (-2, False),
            (12, True),
        ]
        for (value, expected_result) in test_tuples:
            lane.attrib[RoadConstants.LANE_WIDTH_ATTR] = str(value)
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(lane, RoadConstants.LANE_WIDTH_ATTR, False)

    def test_lane_change_restrictions(self):
        road: etree.ElementBase = create_clean_road_node()
        self._target_node.append(road)
        lane: etree.ElementBase = self.create_lane_element(0)
        road.find(RoadConstants.LANES_COLLECTION_TAG)[:] = [lane]

        for attr in [RoadConstants.LANE_MAY_MOVE_LEFT_ATTR, RoadConstants.LANE_MAY_MOVE_RIGHT_ATTR]:
            self.check_effect_of_removing_field(lane, attr, True)

            test_tuples = [
                (0, True),
                (1, True),
                ('true', True),
                ('false', True),
                ('', False),
            ]
            for (value, expected_result) in test_tuples:
                lane.attrib[attr] = str(value)
                self.assertEqual(self.doc.validate(), expected_result)
            lane.attrib.pop(attr)

    def test_lane_policy_element(self):
        road: etree.ElementBase = create_clean_road_node()
        self._target_node.append(road)
        lane: etree.ElementBase = self.create_lane_element(0)
        road.find(RoadConstants.LANES_COLLECTION_TAG)[:] = [lane]
        policy_element: etree.ElementBase = lane.find(RoadConstants.LANE_POLICY_TAG)

        self.check_value_of_uuid_field(policy_element, RoadConstants.LANE_POLICY_ID_ATTR)
        self.check_effect_of_removing_field(policy_element, RoadConstants.LANE_POLICY_ID_ATTR, False)

        lane.remove(policy_element)
        self.assertFalse(self.doc.validate())

    def test_lane_policy_exceptions(self):
        def create_policy_exception():
            return etree.Element(RoadConstants.LANE_POLICY_EXCEPT_TAG, {
                RoadConstants.LANE_POLICY_EXCEPT_POLICY_ATTR: str(uuid()),
                RoadConstants.LANE_POLICY_EXCEPT_START_ATTR: '13:00:00-05:00',
                RoadConstants.LANE_POLICY_EXCEPT_END_ATTR: '18:00:00-05:00',
            })

        road: etree.ElementBase = create_clean_road_node()
        self._target_node.append(road)
        lane: etree.ElementBase = self.create_lane_element(0)
        road.find(RoadConstants.LANES_COLLECTION_TAG)[:] = [lane]
        policy_element: etree.ElementBase = lane.find(RoadConstants.LANE_POLICY_TAG)

        test_tuples = [
            (0, True),
            (1, True),
            (5, True),
        ]
        for (count, expected_result) in test_tuples:
            policy_element[:] = [create_policy_exception() for _ in range(count)]
            self.assertEqual(self.doc.validate(), expected_result)

        policy_exception = create_policy_exception()
        policy_element[:] = [policy_exception]
        self.check_value_of_uuid_field(policy_exception, RoadConstants.LANE_POLICY_EXCEPT_POLICY_ATTR)
        self.check_effect_of_removing_field(policy_exception, RoadConstants.LANE_POLICY_EXCEPT_POLICY_ATTR, False)

        for attr in [RoadConstants.LANE_POLICY_EXCEPT_START_ATTR, RoadConstants.LANE_POLICY_EXCEPT_END_ATTR]:
            policy_exception = create_policy_exception()
            policy_element[:] = [policy_exception]
            tuples = [
                ('', False),
                ('T13:00:00', False),
                ('13:00:00', True),
                ('13:00', False),
                ('13:00:00-06:00', True)
            ]
            for (value, expected_result) in tuples:
                policy_exception.attrib[attr] = value
                self.assertEqual(self.doc.validate(), expected_result)

            self.check_effect_of_removing_field(policy_exception, attr, False)

    def test_chain_counts(self):
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        chains_element: etree.ElementBase = node.find(RoadConstants.CHAIN_TAG)
        existing_chain_index: int = node.index(chains_element)
        second_chain: etree.ElementBase = etree.Element(RoadConstants.CHAIN_TAG, {
            RoadConstants.CHAIN_POINTS_ATTR: '100,100 110,200'
        })
        node.insert(existing_chain_index + 1, second_chain)
        self.assertFalse(self.doc.validate())

    def test_chain_points_attr(self):
        test_tuples = [
            ('', False),
            ('100,100', False),
            ('100,100 150,150', True),
            ('path', False),
        ]
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        chains_element: etree.ElementBase = node.find(RoadConstants.CHAIN_TAG)
        for (value, expected_result) in test_tuples:
            chains_element.attrib[RoadConstants.CHAIN_POINTS_ATTR] = value
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(chains_element, RoadConstants.CHAIN_POINTS_ATTR, False)

    def test_chain_length_attr(self):
        test_tuples = [
            ('', False),
            ('0', False),
            ('1', True),
            ('-22', False),
            ('44.22', True),
        ]

        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        chains_element: etree.ElementBase = node.find(RoadConstants.CHAIN_TAG)
        for (value, expected_result) in test_tuples:
            chains_element.attrib[RoadConstants.CHAIN_LENGTH_ATTR] = value
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(chains_element, RoadConstants.CHAIN_LENGTH_ATTR, True)

    @staticmethod
    def create_pocket_element():
        node: etree.ElementBase = etree.Element(RoadConstants.POCKET_TAG, {
            RoadConstants.POCKET_SIDE_ATTR: 'left',
            RoadConstants.POCKET_LANE_COUNT_ATTR: '2',
            RoadConstants.POCKET_START_ORD_ATTR: '20',
            RoadConstants.POCKET_END_ORD_ATTR: 'b',
            RoadConstants.POCKET_START_TAPER_ATTR: '50',
            RoadConstants.POCKET_END_TAPER_ATTR: 'none',
        })
        return node

    def test_pocket_counts(self):
        acceptable_counts = [0, 1, 2, 30]
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        pockets_element: etree.ElementBase = node.find(RoadConstants.POCKETS_COLLECTION_TAG)
        for count in acceptable_counts:
            pockets_element[:] = [self.create_pocket_element() for _ in range(count)]
            self.assertTrue(self.doc.validate())

    def test_pocket_side_attr(self):
        test_tuples = [
            ('left', True),
            ('right', True),
            ('', False),
            ('LEFT', False)
        ]
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        pockets_element: etree.ElementBase = node.find(RoadConstants.POCKETS_COLLECTION_TAG)
        pocket_node: etree.ElementBase = self.create_pocket_element()
        pockets_element.append(pocket_node)
        for (value, expected_result) in test_tuples:
            pocket_node.attrib[RoadConstants.POCKET_SIDE_ATTR] = value
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(pocket_node, RoadConstants.POCKET_SIDE_ATTR, False)

    def test_pocket_lane_count_attr(self):
        test_tuples = [
            (0, False),
            (1, True),
            (2, True),
            (9, True),
        ]
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        pockets_element: etree.ElementBase = node.find(RoadConstants.POCKETS_COLLECTION_TAG)
        pocket_node: etree.ElementBase = self.create_pocket_element()
        pockets_element.append(pocket_node)
        for (value, expected_result) in test_tuples:
            pocket_node.attrib[RoadConstants.POCKET_LANE_COUNT_ATTR] = str(value)
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(pocket_node, RoadConstants.POCKET_LANE_COUNT_ATTR, True)

    def check_ordinates(self, attr_name: str):
        test_tuples = [
            (0, True),
            (10.5, True),
            (-2.6, False),
            ('a', True),
            ('b', True),
            ('A', False),
        ]
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        pockets_element: etree.ElementBase = node.find(RoadConstants.POCKETS_COLLECTION_TAG)
        pocket_node: etree.ElementBase = self.create_pocket_element()
        pockets_element.append(pocket_node)
        for (value, expected_result) in test_tuples:
            pocket_node.attrib[attr_name] = str(value)
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(pocket_node, attr_name, False)

    def test_pocket_start_ordinate_attr(self):
        self.check_ordinates(RoadConstants.POCKET_START_ORD_ATTR)

    def test_pocket_end_ordinate_attr(self):
        self.check_ordinates(RoadConstants.POCKET_END_ORD_ATTR)

    def check_taper_lengths(self, attr_name: str):
        test_tuples = [
            (0, False),
            (10.5, True),
            (-2.6, False),
            ('none', True),
            ('NONE', False),
            ('None', False),
        ]
        node: etree.ElementBase = create_clean_road_node()
        self._target_node.append(node)

        pockets_element: etree.ElementBase = node.find(RoadConstants.POCKETS_COLLECTION_TAG)
        pocket_node: etree.ElementBase = self.create_pocket_element()
        pockets_element.append(pocket_node)
        for (value, expected_result) in test_tuples:
            pocket_node.attrib[attr_name] = str(value)
            self.assertEqual(self.doc.validate(), expected_result)

        self.check_effect_of_removing_field(pocket_node, attr_name, True)

    def test_pocket_start_taper_attr(self):
        self.check_taper_lengths(RoadConstants.POCKET_START_TAPER_ATTR)

    def test_pocket_end_taper_attr(self):
        self.check_taper_lengths(RoadConstants.POCKET_END_TAPER_ATTR)


if __name__ == '__main__':
    unittest.main()
