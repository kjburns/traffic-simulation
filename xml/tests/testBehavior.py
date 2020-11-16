import unittest
from uuid import uuid4 as uuid
from lxml import etree
from typing import List, Tuple


class BehaviorRootConstants:
    TAG = 'behaviors'
    VERSION_ATTR = 'version'


class FollowingBehaviorConstants:
    COLLECTION_TAG = 'car-following'


class FritzscheConstants:
    TAG = 'fritzsche'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    STANDSTILL_DISTANCE_ATTR = 'ssd'
    DESIRED_GAP_ATTR = 't-desired'
    SAFE_GAP_ATTR = 't-safe'
    RISKY_GAP_ATTR = 't-risky'
    F_X_ATTR = 'f-x'
    K_PT_POSITIVE_ATTR = 'k-ptp'
    K_PT_NEGATIVE_ATTR = 'k-ptn'
    B_NULL_ATTR = 'b-null'


class LaneChangeBehaviorConstants:
    COLLECTION_TAG = 'lane-change'


class HidasLCConstants:
    TAG = 'hidas'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    MINIMUM_GAP_ATTR = 'g_min'
    LANE_CHANGE_TIME_ATTR = 'Dt'
    CALIBRATION_FOLLOWER_ATTR = 'c_f'
    CALIBRATION_LEADER_ATTR = 'c_l'
    FORCE_WINDOW_DURATION_ATTR = 't_fm'
    BRAKING_FRACTION_ATTR = 'f_braking'


class SpeedSelectionConstants:
    COLLECTION_TAG = 'speed'
    TAG = 'speed-behavior'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    FRICTION_FS_MEAN_ATTR = 'friction-fs-reduction-factor-mean'
    FRICTION_FS_STDEV_ATTR = 'friction-fs-reduction-factor-stdev'


class DrivingBehaviorConstants:
    COLLECTION_TAG = 'driving-behaviors'
    TAG = 'driving-behavior'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    FOLLOWING_MODEL_ATTR = 'following'
    LANE_CHANGE_MODEL_ATTR = 'lane-change'
    SPEED_SELECTION_MODEL_ATTR = 'speed-selection'


class RoadBehaviorConstants:
    COLLECTION_TAG = 'road-behaviors'
    TAG = 'road-behavior'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    DEFAULT_BEHAVIOR_ATTR = 'default-behavior'
    EXCEPT_TAG = 'except'
    EXCEPT_BEHAVIOR_ATTR = 'behavior'
    EXCEPT_GROUP_TAG = 'group'
    EXCEPT_GROUP_ID_ATTR = 'id'


def create_and_add_clean_fritzsche(attach_to: etree.ElementBase) -> etree.ElementBase:
    node: etree.ElementBase = etree.SubElement(attach_to, FritzscheConstants.TAG, {
        FritzscheConstants.NAME_ATTR: 'A behavior set',
        FritzscheConstants.UUID_ATTR: str(uuid()),
    })

    return node


def create_and_add_clean_hidas_lc(attach_to: etree.ElementBase) -> etree.ElementBase:
    node: etree.ElementBase = etree.SubElement(attach_to, HidasLCConstants.TAG, {
        HidasLCConstants.NAME_ATTR: 'A lane change behavior',
        HidasLCConstants.UUID_ATTR: str(uuid()),
    })

    return node


def create_and_add_clean_speed_selection(attach_to: etree.ElementBase) -> etree.ElementBase:
    node: etree.ElementBase = etree.SubElement(attach_to, SpeedSelectionConstants.TAG, {
        SpeedSelectionConstants.NAME_ATTR: 'A speed selection behavior',
        SpeedSelectionConstants.UUID_ATTR: str(uuid()),
        SpeedSelectionConstants.FRICTION_FS_MEAN_ATTR: '0.95',
        SpeedSelectionConstants.FRICTION_FS_STDEV_ATTR: '0.05',
    })

    return node


def create_and_add_driving_behavior(attach_to: etree.ElementBase, following_id: str, lane_change_id: str,
                                    speed_selection_id: str, name: str = 'A following behavior'):
    node: etree.ElementBase = etree.SubElement(attach_to, DrivingBehaviorConstants.TAG, {
        DrivingBehaviorConstants.NAME_ATTR: name,
        DrivingBehaviorConstants.UUID_ATTR: str(uuid()),
        DrivingBehaviorConstants.FOLLOWING_MODEL_ATTR: following_id,
        DrivingBehaviorConstants.LANE_CHANGE_MODEL_ATTR: lane_change_id,
        DrivingBehaviorConstants.SPEED_SELECTION_MODEL_ATTR: speed_selection_id,
    })

    return node


def create_and_add_clean_driving_behavior(attach_to: etree.ElementBase) -> etree.ElementBase:
    node = create_and_add_driving_behavior(attach_to, str(uuid()), str(uuid()), str(uuid()))

    return node


def create_add_add_road_behavior(attach_to: etree.ElementBase, default_behavior_id: str,
                                 exception_tuples: List[Tuple[str, List[str]]], name: str = '') -> etree.ElementBase:
    node = etree.SubElement(attach_to, RoadBehaviorConstants.TAG, {
        RoadBehaviorConstants.NAME_ATTR: name,
        RoadBehaviorConstants.UUID_ATTR: str(uuid()),
        RoadBehaviorConstants.DEFAULT_BEHAVIOR_ATTR: default_behavior_id,
    })
    for (alternate_behavior, group_list) in exception_tuples:
        sub_node = etree.SubElement(node, RoadBehaviorConstants.EXCEPT_TAG, {
            RoadBehaviorConstants.EXCEPT_BEHAVIOR_ATTR: alternate_behavior,
        })
        for group in group_list:
            etree.SubElement(sub_node, RoadBehaviorConstants.EXCEPT_GROUP_TAG, {
                RoadBehaviorConstants.EXCEPT_GROUP_ID_ATTR: group,
            })

    return node


def create_and_add_clean_road_behavior(attach_to: etree.ElementBase) -> etree.ElementBase:
    return create_add_add_road_behavior(attach_to, str(uuid()), [
        (str(uuid()), [
            str(uuid()),
            str(uuid()),
        ]),
    ])


class CleanDocument:
    def __init__(self):
        ns_map = {"xsi": 'http://www.w3.org/2001/XMLSchema-instance'}

        self._document_root = etree.Element(BehaviorRootConstants.TAG, {
            BehaviorRootConstants.VERSION_ATTR: '1',
            '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation': '../behavior.xsd',
        }, nsmap=ns_map)

        self._following_behaviors_node = etree.SubElement(
            self._document_root, FollowingBehaviorConstants.COLLECTION_TAG)
        following_node = create_and_add_clean_fritzsche(self._following_behaviors_node)

        self._lane_change_behaviors_node = etree.SubElement(
            self._document_root, LaneChangeBehaviorConstants.COLLECTION_TAG
        )
        lane_change_node = create_and_add_clean_hidas_lc(self._lane_change_behaviors_node)

        self._speed_selection_behaviors_node = etree.SubElement(
            self._document_root, SpeedSelectionConstants.COLLECTION_TAG
        )
        speed_selection_node = create_and_add_clean_speed_selection(self._speed_selection_behaviors_node)

        self._driving_behaviors_node = etree.SubElement(
            self._document_root, DrivingBehaviorConstants.COLLECTION_TAG
        )
        create_and_add_driving_behavior(
            self._driving_behaviors_node,
            following_node.attrib[FritzscheConstants.UUID_ATTR],
            lane_change_node.attrib[HidasLCConstants.UUID_ATTR],
            speed_selection_node.attrib[SpeedSelectionConstants.UUID_ATTR]
        )

        self._road_behaviors_node = etree.SubElement(
            self._document_root, RoadBehaviorConstants.COLLECTION_TAG
        )
        create_and_add_clean_road_behavior(self._road_behaviors_node)

    def print_document_to_console(self):
        print(etree.tostring(self._document_root,
                             xml_declaration=False, pretty_print=True, encoding='unicode'))

    def write_document_to_file(self, filename):
        fp = open(filename, 'w')
        fp.write(etree.tostring(self._document_root,
                                pretty_print=True, encoding='unicode'))
        fp.close()

    def validate(self) -> bool:
        xs_doc = etree.parse('../behavior.xsd')
        xsd = etree.XMLSchema(xs_doc)
        document = etree.ElementTree(self._document_root)
        return xsd.validate(document)

    def get_root_node(self):
        return self._document_root

    def get_following_behaviors_node(self):
        return self._following_behaviors_node

    def get_lane_change_behaviors_node(self):
        return self._lane_change_behaviors_node

    def get_speed_selection_behaviors_node(self):
        return self._speed_selection_behaviors_node

    def get_driving_behaviors_node(self):
        return self._driving_behaviors_node

    def get_road_behaviors_node(self):
        return self._road_behaviors_node


class TestsForFritzscheModel(unittest.TestCase):
    def setUp(self) -> None:
        self._doc: CleanDocument = CleanDocument()
        self._target_node = self._doc.get_following_behaviors_node()

    def check_effect_of_deleting_attribute(self, attribute: str, expected_result: bool):
        node: etree.ElementBase = create_and_add_clean_fritzsche(self._target_node)
        node.attrib.pop(attribute)
        self.assertEqual(self._doc.validate(), expected_result)

    def test_that_clean_document_validates(self):
        self.assertTrue(self._doc.validate())

    def test_that_collection_is_required(self):
        remaining_nodes: List[etree.ElementBase] = list(filter(
            lambda node: node.tag != FollowingBehaviorConstants.COLLECTION_TAG,
            self._doc.get_root_node()
        ))
        self._doc.get_root_node()[:] = remaining_nodes
        self.assertFalse(self._doc.validate())

    def test_instance_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (4, True),
            (100, True)
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = []
            for _ in range(count):
                create_and_add_clean_fritzsche(self._target_node)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_name_is_optional(self):
        self.check_effect_of_deleting_attribute(FritzscheConstants.NAME_ATTR, True)

    def test_name_values(self):
        test_tuples: List[Tuple[str, bool]] = [
            ('', True),
            ('name', True),
            ('2202', True),
        ]
        node: etree.ElementBase = create_and_add_clean_fritzsche(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[FritzscheConstants.NAME_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_uuid_is_required(self):
        self.check_effect_of_deleting_attribute(FritzscheConstants.UUID_ATTR, False)

    def test_uuid_values(self):
        test_tuples: List[Tuple[str, bool]] = [
            ('', False),
            ('de5e513a-5469-4778-ab61-30e5da4bcf4a', True),
            ('de5e513a-5469-4778-ab61-30e5da4bcg4a', False)
        ]
        node: etree.ElementBase = create_and_add_clean_fritzsche(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[FritzscheConstants.UUID_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_attribute_values(self):
        attributes: List[str] = [
            FritzscheConstants.B_NULL_ATTR,
            FritzscheConstants.DESIRED_GAP_ATTR,
            FritzscheConstants.F_X_ATTR,
            FritzscheConstants.K_PT_NEGATIVE_ATTR,
            FritzscheConstants.K_PT_POSITIVE_ATTR,
            FritzscheConstants.RISKY_GAP_ATTR,
            FritzscheConstants.SAFE_GAP_ATTR,
            FritzscheConstants.STANDSTILL_DISTANCE_ATTR,
        ]
        test_tuples: List[tuple] = [
            ('0', False),
            ('1', True),
            ('55', True),
            ('-1', False),
        ]
        for attr in attributes:
            for (value, expected_result) in test_tuples:
                self._target_node[:] = []
                fritzsche: etree.ElementBase = create_and_add_clean_fritzsche(self._target_node)
                fritzsche.attrib[attr] = value
                self.assertEqual(self._doc.validate(), expected_result)

    def test_that_other_attributes_are_allowable(self):
        node: etree.ElementBase = create_and_add_clean_fritzsche(self._target_node)
        node.attrib['other-attribute'] = 'attribute value'
        self.assertTrue(self._doc.validate())


class TestsForHidasLaneChangeModel(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanDocument()
        self._target_node = self._doc.get_lane_change_behaviors_node()

    def check_effect_of_deleting_attribute(self, attribute: str, expected_result: bool):
        node: etree.ElementBase = create_and_add_clean_hidas_lc(self._target_node)
        node.attrib.pop(attribute)
        self.assertEqual(self._doc.validate(), expected_result)

    def test_that_collection_is_required(self):
        remaining_nodes: List[etree.ElementBase] = list(filter(
            lambda node: node.tag != LaneChangeBehaviorConstants.COLLECTION_TAG,
            self._doc.get_root_node()
        ))
        self._doc.get_root_node()[:] = remaining_nodes
        self.assertFalse(self._doc.validate())

    def test_instance_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (4, True),
            (100, True)
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = []
            for _ in range(count):
                create_and_add_clean_hidas_lc(self._target_node)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_name_is_optional(self):
        self.check_effect_of_deleting_attribute(HidasLCConstants.NAME_ATTR, True)

    def test_name_values(self):
        test_tuples = [
            ('', True),
            ('name', True),
            ('1102', True),
        ]
        node = create_and_add_clean_hidas_lc(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[HidasLCConstants.NAME_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_uuid_is_required(self):
        self.check_effect_of_deleting_attribute(HidasLCConstants.UUID_ATTR, False)

    def test_uuid_values(self):
        test_tuples: List[Tuple[str, bool]] = [
            ('', False),
            ('de5e513a-5469-4778-ab61-30e5da4bcf4a', True),
            ('de5e513a-5469-4778-ab61-30e5da4bcg4a', False)
        ]
        node: etree.ElementBase = create_and_add_clean_hidas_lc(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[HidasLCConstants.UUID_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_attribute_values(self):
        attributes: List[str] = [
            HidasLCConstants.CALIBRATION_FOLLOWER_ATTR,
            HidasLCConstants.CALIBRATION_LEADER_ATTR,
            HidasLCConstants.FORCE_WINDOW_DURATION_ATTR,
            HidasLCConstants.LANE_CHANGE_TIME_ATTR,
            HidasLCConstants.MINIMUM_GAP_ATTR,
        ]
        test_tuples = [
            (0.0, False),
            (0.5, True),
            (1.2, True),
            (223.1, True),
            (-0.5, False),
            (-2, False),
        ]

        for attr in attributes:
            self._target_node[:] = []
            node: etree.ElementBase = create_and_add_clean_hidas_lc(self._target_node)

            for (value, expected_result) in test_tuples:
                node.attrib[attr] = str(value)
                self.assertEqual(self._doc.validate(), expected_result)

        test_tuples = [
            (-0.1, False),
            (0, False),
            (0.5, True),
            (1.0, True),
            (1.1, False),
        ]

        self._target_node[:] = []
        node: etree.ElementBase = create_and_add_clean_hidas_lc(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[HidasLCConstants.BRAKING_FRACTION_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_other_attributes_are_allowable(self):
        node: etree.ElementBase = create_and_add_clean_hidas_lc(self._target_node)
        node.attrib['another-attribute'] = 'another value'
        self.assertTrue(self._doc.validate())


class TestsForSpeedSelectionBehaviors(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanDocument()
        self._target_node = self._doc.get_speed_selection_behaviors_node()

    def check_effect_of_deleting_attribute(self, attribute: str, expected_result: bool):
        node: etree.ElementBase = create_and_add_clean_speed_selection(self._target_node)
        node.attrib.pop(attribute)
        self.assertEqual(self._doc.validate(), expected_result)

    def test_that_collection_is_required(self):
        remaining_nodes: List[etree.ElementBase] = list(filter(
            lambda node: node.tag != SpeedSelectionConstants.COLLECTION_TAG,
            self._doc.get_root_node()
        ))
        self._doc.get_root_node()[:] = remaining_nodes
        self.assertFalse(self._doc.validate())

    def test_behavior_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (100, True),
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = []
            for _ in range(count):
                create_and_add_clean_speed_selection(self._target_node)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_name_is_optional(self):
        self.check_effect_of_deleting_attribute(SpeedSelectionConstants.NAME_ATTR, True)

    def test_name_values(self):
        test_tuples = [
            ('', True),
            ('Speed selection behavior name', True),
            ('002', True)
        ]
        node: etree.ElementBase = create_and_add_clean_speed_selection(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[SpeedSelectionConstants.NAME_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_uuid_is_required(self):
        self.check_effect_of_deleting_attribute(SpeedSelectionConstants.UUID_ATTR, False)

    def test_uuid_value(self):
        test_tuples: List[Tuple[str, bool]] = [
            ('', False),
            ('de5e513a-5469-4778-ab61-30e5da4bcf4a', True),
            ('de5e513a-5469-4778-ab61-30e5da4bcg4a', False)
        ]
        node: etree.ElementBase = create_and_add_clean_speed_selection(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[SpeedSelectionConstants.UUID_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_friction_mean_is_required(self):
        self.check_effect_of_deleting_attribute(SpeedSelectionConstants.FRICTION_FS_MEAN_ATTR, False)

    def test_friction_tolerance_mean_values(self):
        self._target_node[:] = []
        node: etree.ElementBase = create_and_add_clean_speed_selection(self._target_node)
        test_tuples = [
            (-1, False),
            (0, False),
            (0.45, False),
            (0.50, True),
            (1.00, True),
            (2.00, True),
            (2.01, False),
            (3, False)
        ]
        for (value, expected_result) in test_tuples:
            node.attrib[SpeedSelectionConstants.FRICTION_FS_MEAN_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_friction_stdev_is_required(self):
        self.check_effect_of_deleting_attribute(SpeedSelectionConstants.FRICTION_FS_STDEV_ATTR, False)

    def test_friction_tolerance_stdev_values(self):
        self._target_node[:] = []
        node: etree.ElementBase = create_and_add_clean_speed_selection(self._target_node)
        test_tuples = [
            (-1, False),
            (-0.1, False),
            (0, True),
            (0.50, True),
            (1.00, True),
        ]
        for (value, expected_result) in test_tuples:
            node.attrib[SpeedSelectionConstants.FRICTION_FS_STDEV_ATTR] = str(value)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_other_attributes_are_okay(self):
        node: etree.ElementBase = create_and_add_clean_speed_selection(self._target_node)
        node.attrib['another-attribute'] = 'attribute value'
        self.assertTrue(self._doc.validate())


class TestsForDrivingBehaviors(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanDocument()
        self._target_node = self._doc.get_driving_behaviors_node()

    def check_effect_of_deleting_attribute(self, attribute: str, expected_result: bool):
        self._target_node[:] = []
        node: etree.ElementBase = create_and_add_clean_driving_behavior(self._target_node)
        node.attrib.pop(attribute)
        self.assertEqual(self._doc.validate(), expected_result)

    def test_that_collection_is_required(self):
        remaining_nodes: List[etree.ElementBase] = list(filter(
            lambda node: node.tag != DrivingBehaviorConstants.COLLECTION_TAG,
            self._doc.get_root_node()
        ))
        self._doc.get_root_node()[:] = remaining_nodes
        self.assertFalse(self._doc.validate())

    def test_behavior_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (100, True),
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = []
            for _ in range(count):
                create_and_add_clean_driving_behavior(self._target_node)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_parameters_are_required(self):
        test_tuples = [
            (DrivingBehaviorConstants.NAME_ATTR, False),
            (DrivingBehaviorConstants.UUID_ATTR, True),
            (DrivingBehaviorConstants.FOLLOWING_MODEL_ATTR, True),
            (DrivingBehaviorConstants.LANE_CHANGE_MODEL_ATTR, True),
            (DrivingBehaviorConstants.SPEED_SELECTION_MODEL_ATTR, True)
        ]
        for (attribute, is_required) in test_tuples:
            expected_result: bool = not is_required
            self.check_effect_of_deleting_attribute(attribute, expected_result)

    def test_uuid_values(self):
        test_tuples: List[Tuple[str, bool]] = [
            ('', False),
            ('de5e513a-5469-4778-ab61-30e5da4bcf4a', True),
            ('de5e513a-5469-4778-ab61-30e5da4bcg4a', False)
        ]
        attribute_list = [DrivingBehaviorConstants.UUID_ATTR,
                          DrivingBehaviorConstants.FOLLOWING_MODEL_ATTR,
                          DrivingBehaviorConstants.LANE_CHANGE_MODEL_ATTR,
                          DrivingBehaviorConstants.SPEED_SELECTION_MODEL_ATTR
                          ]
        for attribute in attribute_list:
            self._target_node[:] = []
            node: etree.ElementBase = create_and_add_clean_driving_behavior(self._target_node)
            for (value, expected_result) in test_tuples:
                node.attrib[attribute] = value
                self.assertEqual(self._doc.validate(), expected_result)

    def test_that_other_attributes_are_okay(self):
        node: etree.ElementBase = create_and_add_clean_driving_behavior(self._target_node)
        node.attrib['another-attribute'] = 'a value'
        self.assertTrue(self._doc.validate())


class TestsForRoadBehaviors(unittest.TestCase):
    def setUp(self) -> None:
        self._doc: CleanDocument = CleanDocument()
        self._target_node: etree.ElementBase = self._doc.get_road_behaviors_node()

    def test_that_collection_is_required(self):
        remaining_nodes: List[etree.ElementBase] = list(filter(
            lambda node: node.tag != RoadBehaviorConstants.COLLECTION_TAG,
            self._doc.get_root_node()
        ))
        self._doc.get_root_node()[:] = remaining_nodes
        self.assertFalse(self._doc.validate())

    def test_instance_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (10, True),
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = []
            for _ in range(count):
                create_and_add_clean_road_behavior(self._target_node)

            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_attributes_are_optional(self):
        test_tuples = [
            (RoadBehaviorConstants.NAME_ATTR, True),
            (RoadBehaviorConstants.UUID_ATTR, False),
            (RoadBehaviorConstants.DEFAULT_BEHAVIOR_ATTR, False)
        ]
        for (attribute_name, expected_result) in test_tuples:
            self._target_node[:] = []
            node: etree.ElementBase = create_and_add_clean_road_behavior(self._target_node)
            node.attrib.pop(attribute_name)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_name_values(self):
        test_tuples = [
            ('', True),
            ('a name', True),
            ('110', True),
        ]
        node: etree.ElementBase = create_and_add_clean_road_behavior(self._target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[RoadBehaviorConstants.NAME_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_values_of_attributes_taking_uuids(self):
        test_tuples: List[Tuple[str, bool]] = [
            ('', False),
            ('de5e513a-5469-4778-ab61-30e5da4bcf4a', True),
            ('de5e513a-5469-4778-ab61-30e5da4bcg4a', False)
        ]
        for (prospective_id, expected_result) in test_tuples:
            self._target_node[:] = []
            node: etree.ElementBase = create_add_add_road_behavior(self._target_node, prospective_id, [
                (prospective_id, [prospective_id])
            ])
            node.attrib[RoadBehaviorConstants.UUID_ATTR] = prospective_id
            self.assertEqual(self._doc.validate(), expected_result)

    def test_except_counts(self):
        test_tuples = [
            (0, True),
            (1, True),
            (10, True),
        ]
        for (except_count, expected_result) in test_tuples:
            self._target_node[:] = []
            create_add_add_road_behavior(self._target_node, str(uuid()), [
                (str(uuid()), [str(uuid())]) for _ in range(except_count)
            ])
            self.assertEqual(self._doc.validate(), expected_result)

    def test_except_behavior_attribute_is_required(self):
        road_behavior_node: etree.ElementBase = create_and_add_clean_road_behavior(self._target_node)
        except_node: etree.ElementBase = road_behavior_node[0]
        except_node.attrib.pop(RoadBehaviorConstants.EXCEPT_BEHAVIOR_ATTR)
        self.assertFalse(self._doc.validate())

    def test_except_group_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (10, True),
        ]
        for (count, expected_result) in test_tuples:
            self._target_node[:] = []
            create_add_add_road_behavior(self._target_node, str(uuid()), [
                (str(uuid()), [str(uuid()) for _ in range(count)])
            ])
            self.assertEqual(self._doc.validate(), expected_result)

    def test_except_group_id_is_required(self):
        road_behavior_node: etree.ElementBase = create_and_add_clean_road_behavior(self._target_node)
        except_node: etree.ElementBase = road_behavior_node[0]
        group_node: etree.ElementBase = except_node[0]
        group_node.attrib.pop(RoadBehaviorConstants.EXCEPT_GROUP_ID_ATTR)
        self.assertFalse(self._doc.validate())


if __name__ == '__main__':
    unittest.main()
