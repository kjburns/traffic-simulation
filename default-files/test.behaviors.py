from lxml import etree
import unittest
from typing import Callable


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


if __name__ == '__main__':
    unittest.main()
