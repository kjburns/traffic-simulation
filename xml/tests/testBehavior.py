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


def create_and_add_clean_fritzsche(attach_to: etree.ElementBase) -> etree.ElementBase:
    node: etree.ElementBase = etree.SubElement(attach_to, FritzscheConstants.TAG, {
        FritzscheConstants.NAME_ATTR: 'A behavior set',
        FritzscheConstants.UUID_ATTR: str(uuid()),
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


if __name__ == '__main__':
    unittest.main()
