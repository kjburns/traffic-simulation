import unittest
from uuid import uuid4 as uuid
from lxml import etree


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


class CleanLaneUsageDocument:
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
        xs_doc = etree.parse('../vehicle-types.xsd')
        xsd = etree.XMLSchema(xs_doc)
        document = etree.ElementTree(self._document_root)
        return xsd.validate(document)

    def get_policies_node(self):
        return self._policies_node


class TestsForLanePolicies(unittest.TestCase):
    def setUp(self) -> None:
        self._doc = CleanLaneUsageDocument()
        self.target_node = self._doc.get_policies_node()


if __name__ == '__main__':
    unittest.main()
