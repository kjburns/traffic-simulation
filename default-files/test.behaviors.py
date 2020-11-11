from lxml import etree
import unittest
from typing import Callable, List


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


def does_uuid_exist_in_collection(uuid: str, collection: etree.ElementBase) -> bool:
    # helper function to avoid repetition in tests

    def is_it_this_node(node: etree.ElementBase) -> bool:
        return node.attrib['uuid'] == uuid

    return any(map(is_it_this_node, collection))


def are_all_attribute_values_unique(getter: Callable[[object], None], collection: list) -> bool:
    values_as_list: list = list(map(getter, collection))
    values_as_set: set = set(values_as_list)

    return len(values_as_list) == len(values_as_set)


class TestsForFollowingBehaviors(unittest.TestCase):
    def setUp(self) -> None:
        self._behaviors_document: etree._ElementTree = etree.parse('default.behaviors.xml')
        self._following_behaviors_list: etree.ElementBase = self._behaviors_document.getroot()[0]

    def test_that_document_validates(self):
        xs_doc = etree.parse('../xml/behavior.xsd')
        xsd = etree.XMLSchema(xs_doc)
        self.assertTrue(xsd.validate(self._behaviors_document))

    def test_that_uuids_are_unique(self):
        self.assertTrue(are_all_attribute_values_unique(
            lambda node: node.attrib[FritzscheConstants.UUID_ATTR],
            list(self._following_behaviors_list)
        ))

    def test_that_each_behavior_has_a_name(self):
        def is_valid_behavior(behavior_node: etree.ElementBase) -> bool:
            return ((FritzscheConstants.NAME_ATTR in behavior_node.attrib) and
                    (behavior_node.attrib[FritzscheConstants.NAME_ATTR].strip() != ''))

        self.assertTrue(all(map(is_valid_behavior, self._following_behaviors_list)))


class TestsForLaneChangeBehaviors(unittest.TestCase):
    def setUp(self) -> None:
        self._behaviors_document: etree._ElementTree = etree.parse('default.behaviors.xml')
        self._lane_change_behaviors_list: etree.ElementBase = self._behaviors_document.getroot()[1]

    def test_that_uuids_are_unique(self):
        self.assertTrue(are_all_attribute_values_unique(
            lambda node: node.attrib[HidasLCConstants.UUID_ATTR],
            list(self._lane_change_behaviors_list)
        ))

    def test_that_each_behavior_has_a_name(self):
        def is_valid_behavior(behavior_node: etree.ElementBase) -> bool:
            return ((HidasLCConstants.NAME_ATTR in behavior_node.attrib) and
                    (behavior_node.attrib[HidasLCConstants.NAME_ATTR].strip() != ''))

        self.assertTrue(all(map(is_valid_behavior, self._lane_change_behaviors_list)))


class TestsForSpeedSelectionBehaviors(unittest.TestCase):
    def setUp(self) -> None:
        self._behaviors_document: etree._ElementTree = etree.parse('default.behaviors.xml')
        self._speed_selection_behaviors_list: etree.ElementBase = self._behaviors_document.getroot()[2]

    def test_that_uuids_are_unique(self):
        self.assertTrue(are_all_attribute_values_unique(
            lambda node: node.attrib[SpeedSelectionConstants.UUID_ATTR],
            list(self._speed_selection_behaviors_list)
        ))

    def test_that_each_behavior_has_a_name(self):
        def is_valid_behavior(behavior_node: etree.ElementBase) -> bool:
            return ((SpeedSelectionConstants.NAME_ATTR in behavior_node.attrib) and
                    (behavior_node.attrib[SpeedSelectionConstants.NAME_ATTR].strip() != ''))

        self.assertTrue(all(map(is_valid_behavior, self._speed_selection_behaviors_list)))

    def test_that_friction_standard_deviations_are_reasonable(self):
        def is_valid_behavior(behavior_node: etree.ElementBase) -> bool:
            return float(behavior_node.attrib[SpeedSelectionConstants.FRICTION_FS_STDEV_ATTR]) <= 0.2

        self.assertTrue(all(map(is_valid_behavior, self._speed_selection_behaviors_list)))


class TestsForDrivingBehaviors(unittest.TestCase):
    def setUp(self) -> None:
        self._behaviors_document: etree._ElementTree = etree.parse('default.behaviors.xml')
        self._following_behaviors_list: etree.ElementBase = self._behaviors_document.getroot()[0]
        self._lane_change_behaviors_list: etree.ElementBase = self._behaviors_document.getroot()[1]
        self._speed_selection_behaviors_list: etree.ElementBase = self._behaviors_document.getroot()[2]
        self._driving_behaviors_list: etree.ElementBase = self._behaviors_document.getroot()[3]

    def test_that_uuids_are_unique(self):
        self.assertTrue(are_all_attribute_values_unique(
            lambda node: node.attrib[DrivingBehaviorConstants.UUID_ATTR],
            list(self._driving_behaviors_list)
        ))

    def test_that_each_entry_has_a_name(self):
        def is_valid_behavior(behavior_node: etree.ElementBase) -> bool:
            return ((DrivingBehaviorConstants.NAME_ATTR in behavior_node.attrib) and
                    (behavior_node.attrib[DrivingBehaviorConstants.NAME_ATTR].strip() != ''))

        self.assertTrue(all(map(is_valid_behavior, self._driving_behaviors_list)))

    def test_that_each_entry_references_valid_behaviors(self):
        def is_valid_behavior(behavior_node: etree.ElementBase) -> bool:
            return all([
                does_uuid_exist_in_collection(
                    behavior_node.attrib[DrivingBehaviorConstants.FOLLOWING_MODEL_ATTR],
                    self._following_behaviors_list),
                does_uuid_exist_in_collection(
                    behavior_node.attrib[DrivingBehaviorConstants.LANE_CHANGE_MODEL_ATTR],
                    self._lane_change_behaviors_list),
                does_uuid_exist_in_collection(
                    behavior_node.attrib[DrivingBehaviorConstants.SPEED_SELECTION_MODEL_ATTR],
                    self._speed_selection_behaviors_list),
            ])

        self.assertTrue(all(map(is_valid_behavior, self._driving_behaviors_list)))


if __name__ == '__main__':
    unittest.main()
