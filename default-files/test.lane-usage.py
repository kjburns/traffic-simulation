from lxml import etree
import unittest
from typing import Callable, List, Set


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


class GroupConstants:
    TAG = 'group'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    VEHICLE_TAG = 'vehicle'
    VEHICLE_TYPE_ATTR = 'type'


class TypeConstants:
    TAG = 'vehicle-type'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    MODELS_ATTR = 'models'
    COLORS_ATTR = 'colors'
    ACCELERATION_ATTR = 'acceleration'
    DECELERATION_ATTR = 'deceleration'
    OCCUPANCY_ATTR = 'occupancy'
    SHARING_ATTR = 'sharing'
    SHARING_VALUE_NONE = 'none'
    SHARING_VALUE_HOV = 'hov'
    SHARING_VALUE_TRANSIT = 'transit'


def does_uuid_exist_in_collection(uuid: str, collection: etree.ElementBase) -> bool:
    # helper function to avoid repetition in tests

    def is_it_this_node(node: etree.ElementBase) -> bool:
        return node.attrib['uuid'] == uuid

    return any(map(is_it_this_node, collection))


def are_all_attribute_values_unique(getter: Callable[[object], None], collection: list) -> bool:
    values_as_list: list = list(map(getter, collection))
    values_as_set: set = set(values_as_list)

    return len(values_as_list) == len(values_as_set)


class TestsForDefaultLaneUsageFile(unittest.TestCase):
    def setUp(self) -> None:
        self._vehicle_classes_document: etree._ElementTree = etree.parse('default.vehicle-types.xml')
        self._vehicle_types_list: etree.ElementBase = self._vehicle_classes_document.getroot()[0]
        self._vehicle_groups_list: etree.ElementBase = self._vehicle_classes_document.getroot()[1]

        self._lane_usage_document: etree._ElementTree = etree.parse('default.lane-usage.xml')
        self._lane_policies_list: etree.ElementBase = self._lane_usage_document.getroot()[0]

    def test_that_document_validates(self):
        xs_doc = etree.parse('../xml/lane-usage.xsd')
        xsd = etree.XMLSchema(xs_doc)
        self.assertTrue(xsd.validate(self._lane_usage_document))

    def test_that_policy_uuids_are_unique(self):
        all_unique: bool = are_all_attribute_values_unique(
            lambda node: node.attrib[LanePolicyConstants.POLICY_UUID_ATTR], list(self._lane_policies_list))
        self.assertTrue(all_unique)

    def test_that_policy_except_groups_are_valid_references(self):
        valid_group_uuids: List[str] = list(map(
            lambda nd: nd.attrib[GroupConstants.UUID_ATTR],
            self._vehicle_groups_list
        ))

        def are_all_uuids_valid(policy_node: etree.ElementBase) -> bool:
            except_uuids: List[str] = list(map(
                lambda nd: nd.attrib[LanePolicyConstants.EXCEPT_GROUP_ATTR],
                policy_node
            ))

            return all(map(lambda uuid: uuid in valid_group_uuids, except_uuids))

        self.assertTrue(all(map(are_all_uuids_valid, self._lane_policies_list)))  # poop - my son

    def test_that_none_except_none_does_not_happen(self):
        def is_valid_policy(policy_node: etree.ElementBase) -> bool:
            start_from = policy_node.attrib[LanePolicyConstants.POLICY_START_FROM_ATTR]

            return True if \
                start_from == LanePolicyConstants.POLICY_START_FROM_VALUE_ALL \
                else \
                len(policy_node) > 0

        self.assertTrue(all(map(is_valid_policy, self._lane_policies_list)))

    def test_that_all_except_all_does_not_happen(self):
        def is_valid_policy(policy_node: etree.ElementBase) -> bool:
            start_from = policy_node.attrib[LanePolicyConstants.POLICY_START_FROM_ATTR]

            ret: bool

            if start_from == LanePolicyConstants.POLICY_START_FROM_VALUE_NONE:
                ret = True
            else:
                all_type_uuids: List[str] = list(map(
                    lambda node: node.attrib[TypeConstants.UUID_ATTR], self._vehicle_types_list))
                referenced_type_uuids: Set[str] = set()

                for exception in policy_node:
                    uuid: str = exception.attrib[LanePolicyConstants.EXCEPT_GROUP_ATTR]
                    group_element: etree.ElementBase = list(
                        filter(lambda node: node.attrib[GroupConstants.UUID_ATTR] == uuid,
                               self._vehicle_groups_list)
                    )[0]
                    type_set: Set[str] = set(map(
                        lambda node: node.attrib[GroupConstants.VEHICLE_TYPE_ATTR], group_element))
                    referenced_type_uuids = referenced_type_uuids.union(type_set)

                return len(referenced_type_uuids) < len(all_type_uuids)

            return ret

        self.assertTrue(all(map(is_valid_policy, self._lane_policies_list)))


if __name__ == '__main__':
    unittest.main()
