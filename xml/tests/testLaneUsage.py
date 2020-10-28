import unittest
from uuid import uuid4 as uuid
from lxml import etree
from typing import Callable
from abc import abstractmethod


class LaneUsageConstants:
    ROOT_TAG = 'lane-usage'
    VERSION_ATTR = 'version'


class LanePolicyConstants:
    COLLECTION_TAG = 'lane-policies'
    POLICY_TAG = 'policy'
    POLICY_NAME_ATTR = 'name'
    POLICY_UUID_ATTR = 'uuid'
    POLICY_START_FROM_ATTR = 'start-from'
    POLICY_START_FROM_VALUE_ALL = 'all-allowed'
    POLICY_START_FROM_VALUE_NONE = 'none-allowed'
    EXCEPT_TAG = 'except'
    EXCEPT_GROUP_ATTR = 'group'


def create_lane_policy_except(attach_to: etree.ElementBase, vehicle_group_uuid: str) -> etree.ElementBase:
    node: etree.ElementBase = etree.SubElement(attach_to, LanePolicyConstants.EXCEPT_TAG, {
        LanePolicyConstants.EXCEPT_GROUP_ATTR: vehicle_group_uuid,
    })

    return node


def create_and_add_clean_lane_policy(attach_to: etree.ElementBase) -> etree.ElementBase:
    node: etree.ElementBase = etree.SubElement(attach_to, LanePolicyConstants.POLICY_TAG, {
        LanePolicyConstants.POLICY_NAME_ATTR: 'a lane policy',
        LanePolicyConstants.POLICY_UUID_ATTR: str(uuid()),
        LanePolicyConstants.POLICY_START_FROM_ATTR: LanePolicyConstants.POLICY_START_FROM_VALUE_ALL,
    })

    return node


class IValidatesDocument:
    @abstractmethod
    def validate(self) -> bool:
        return False


class CleanLaneUsageDocument(IValidatesDocument):
    def __init__(self):
        ns_map = {"xsi": 'http://www.w3.org/2001/XMLSchema-instance'}

        self._document_root = etree.Element(LaneUsageConstants.ROOT_TAG, {
            LaneUsageConstants.VERSION_ATTR: '1',
            '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation': '../lane-usage.xsd',
        }, nsmap=ns_map)

        self._policies_node = etree.SubElement(self._document_root, LanePolicyConstants.COLLECTION_TAG)
        create_and_add_clean_lane_policy(self._policies_node)

    def print_document_to_console(self):
        print(etree.tostring(self._document_root,
                             xml_declaration=False, pretty_print=True, encoding='unicode'))

    def write_document_to_file(self, filename):
        fp = open(filename, 'w')
        fp.write(etree.tostring(self._document_root,
                                pretty_print=True, encoding='unicode'))
        fp.close()

    def validate(self) -> bool:
        xs_doc = etree.parse('../lane-usage.xsd')
        xsd = etree.XMLSchema(xs_doc)
        document = etree.ElementTree(self._document_root)
        return xsd.validate(document)

    def get_root_node(self):
        return self._document_root

    def get_policies_node(self):
        return self._policies_node


class TestCaseWithUuidChecker(unittest.TestCase):
    @property
    @abstractmethod
    def doc(self) -> IValidatesDocument:
        return None

    def check_uuid_values(self, setter: Callable[[str], None]) -> None:
        test_tuples = [
            ('', False),
            ('62d987f6-becc-430e-a8fa-c940f8fa0a86', True),
            ('62d987g6-be3c-430e-a8fa-c940f8fa0a86', False)
        ]
        for (value, expected_result) in test_tuples:
            setter(value)
            self.assertEqual(self.doc.validate(), expected_result)

    def check_effect_of_removing_node(self, remove_from: etree.ElementBase, attribute_name: str,
                                      expected_result: bool) -> None:
        remove_from.attrib.pop(attribute_name)
        self.assertEqual(self.doc.validate(), expected_result)


class TestsForLanePolicies(TestCaseWithUuidChecker):
    @property
    def doc(self) -> IValidatesDocument:
        return self._doc

    def setUp(self) -> None:
        self._doc = CleanLaneUsageDocument()
        self.target_node = self._doc.get_policies_node()

    def test_that_collection_is_required(self):
        nodes_to_keep = list(filter(lambda node: node.tag != LanePolicyConstants.COLLECTION_TAG,
                                    self._doc.get_root_node()))
        self._doc.get_root_node()[:] = nodes_to_keep
        self.assertFalse(self._doc.validate())

    def test_collection_member_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (4, True),
            (100, True),
        ]
        for (count, expected_result) in test_tuples:
            self.target_node[:] = []
            for _ in range(count):
                create_and_add_clean_lane_policy(self.target_node)
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_name_is_optional(self):
        node = create_and_add_clean_lane_policy(self.target_node)
        node.attrib.pop(LanePolicyConstants.POLICY_NAME_ATTR)
        self.assertTrue(self._doc.validate())

    def test_name_values(self):
        test_tuples = [
            ('', True),
            ('name', True),
            ('2291', True),
        ]
        node = create_and_add_clean_lane_policy(self.target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[LanePolicyConstants.POLICY_NAME_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_that_uuid_is_required(self):
        node = create_and_add_clean_lane_policy(self.target_node)
        self.check_effect_of_removing_node(node, LanePolicyConstants.POLICY_UUID_ATTR, False)

    def test_uuid_values(self):
        node = create_and_add_clean_lane_policy(self.target_node)

        def setter(text: str) -> None:
            node.attrib[LanePolicyConstants.POLICY_UUID_ATTR] = text

        self.check_uuid_values(setter)

    def test_that_start_from_is_required(self):
        node = create_and_add_clean_lane_policy(self.target_node)
        self.check_effect_of_removing_node(node, LanePolicyConstants.POLICY_START_FROM_ATTR, False)

    def test_start_from_values(self):
        test_tuples = [
            ('', False),
            (LanePolicyConstants.POLICY_START_FROM_VALUE_ALL, True),
            (LanePolicyConstants.POLICY_START_FROM_VALUE_NONE, True),
            ('something else', False),
        ]
        node = create_and_add_clean_lane_policy(self.target_node)
        for (value, expected_result) in test_tuples:
            node.attrib[LanePolicyConstants.POLICY_START_FROM_ATTR] = value
            self.assertEqual(self._doc.validate(), expected_result)

    def test_except_count(self):
        test_tuples = [
            (0, True),
            (1, True),
            (4, True),
            (1000, True),
        ]
        node = create_and_add_clean_lane_policy(self.target_node)
        for (count, expected_value) in test_tuples:
            node[:] = []
            for _ in range(count):
                create_lane_policy_except(node, str(uuid()))
            self.assertEqual(self._doc.validate(), expected_value)

    def test_that_except_uuid_is_required(self):
        node = create_and_add_clean_lane_policy(self.target_node)
        ex = create_lane_policy_except(node, str(uuid()))
        self.check_effect_of_removing_node(ex, LanePolicyConstants.EXCEPT_GROUP_ATTR, False)

    def test_except_uuid_values(self):
        node = create_and_add_clean_lane_policy(self.target_node)
        exc = create_lane_policy_except(node, str(uuid()))

        def setter(text: str) -> None:
            exc.attrib[LanePolicyConstants.EXCEPT_GROUP_ATTR] = text

        self.check_uuid_values(setter)


if __name__ == '__main__':
    unittest.main()
