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


class CleanDocument:
    def __init__(self):
        ns_map = {"xsi": 'http://www.w3.org/2001/XMLSchema-instance'}

        self._document_root = etree.Element(BehaviorRootConstants.TAG, {
            BehaviorRootConstants.VERSION_ATTR: '1',
            '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation': '../behavior.xsd',
        }, nsmap=ns_map)

        self._following_behaviors_node = etree.SubElement(
            self._document_root, FollowingBehaviorConstants.COLLECTION_TAG)
        create_and_add_clean_fritzsche(self._following_behaviors_node)

        self._lane_change_behaviors_node = etree.SubElement(
            self._document_root, LaneChangeBehaviorConstants.COLLECTION_TAG
        )
        create_and_add_clean_hidas_lc(self._lane_change_behaviors_node)

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

    def test_that_collection_is_required(self): pass  # TODO

    def test_instance_counts(self): pass  # TODO

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


if __name__ == '__main__':
    unittest.main()
