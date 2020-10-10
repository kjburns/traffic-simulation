import unittest
from lxml import etree
from uuid import uuid4 as uuid


class VehicleTypesConstants:
    VERSION_ATTR = 'version'
    TYPES_COLLECTION_TAG = 'types'
    GROUPS_COLLECTION_TAG = 'groups'  # not yet used


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


def create_and_add_clean_type_element(attach_to: etree.ElementBase) -> etree.ElementBase:
    ret: etree.ElementBase = etree.SubElement(attach_to, TypeConstants.TAG, {
        TypeConstants.NAME_ATTR: 'a vehicle type',
        TypeConstants.UUID_ATTR: str(uuid()),
        TypeConstants.MODELS_ATTR: str(uuid()),
        TypeConstants.COLORS_ATTR: str(uuid()),
        TypeConstants.ACCELERATION_ATTR: str(uuid()),
        TypeConstants.DECELERATION_ATTR: str(uuid()),
        TypeConstants.OCCUPANCY_ATTR: str(uuid()),
        TypeConstants.SHARING_ATTR: TypeConstants.SHARING_VALUE_HOV,
    })
    return ret


class CleanVehiclesDocument:
    def __init__(self):
        ns_map = {"xsi": 'http://www.w3.org/2001/XMLSchema-instance'}

        self._document_root = etree.Element('vehicle-types-and-groups', {
            VehicleTypesConstants.VERSION_ATTR: '1',
            '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation': '../vehicle-types.xsd',
        }, nsmap=ns_map)

        self._vehicles_node = etree.SubElement(self._document_root, VehicleTypesConstants.TYPES_COLLECTION_TAG)
        create_and_add_clean_type_element(self._vehicles_node)

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

    def get_vehicles_node(self):
        return self._vehicles_node

    def get_collection_elements(self):
        return [element for element in self._document_root]

    def get_document_root(self) -> etree.ElementBase:
        return self._document_root


class TestsForVehicleTypes(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = CleanVehiclesDocument()
        self.target_node = self.doc.get_vehicles_node()

    def internal_test_effect_of_removing_attribute(self, attribute_name: str, expected_result: bool):
        self.target_node[:] = []
        node: etree.ElementBase = create_and_add_clean_type_element(self.target_node)
        node.attrib.pop(attribute_name)
        self.assertEqual(self.doc.validate(), expected_result)

    def internal_test_attribute_value_expecting_uuid(self, attribute_name: str):
        self.target_node[:] = []
        node: etree.ElementBase = create_and_add_clean_type_element(self.target_node)
        test_tuples = [
            ('', False),
            ('56d00ad8-91dc-416e-b0a7-19d25e103cec', True),
            ('56d00ad8-91dc-416e-b0a7-19d25e103ceg', False),
        ]
        for (value, expected_result) in test_tuples:
            node.attrib[attribute_name] = value
            self.assertEqual(self.doc.validate(), expected_result)

    def test_that_collection_node_is_required(self):
        node_to_delete = list(filter(lambda element: element.tag == VehicleTypesConstants.TYPES_COLLECTION_TAG,
                                     self.doc.get_collection_elements()))[0]
        self.doc.get_document_root().remove(node_to_delete)
        self.assertFalse(self.doc.validate())

    def test_collection_counts(self):
        test_tuples = [
            (0, False),
            (1, True),
            (4, True),
            (1000, True),
        ]
        for (count, expected_result) in test_tuples:
            self.target_node[:] = []
            for _ in range(count):
                create_and_add_clean_type_element(self.target_node)

            self.assertEqual(self.doc.validate(), expected_result)

    def test_that_name_is_optional(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.NAME_ATTR, True)

    def test_name_values(self):
        node = create_and_add_clean_type_element(self.target_node)
        test_tuples = [
            ('', True),
            ('name', True),
            ('382910438', True),
        ]
        for (value, expected_result) in test_tuples:
            node.attrib[TypeConstants.NAME_ATTR] = value
            self.assertEqual(self.doc.validate(), expected_result)

    def test_uuid(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.UUID_ATTR, False)
        self.internal_test_attribute_value_expecting_uuid(TypeConstants.UUID_ATTR)

    def test_models_id(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.MODELS_ATTR, False)
        self.internal_test_attribute_value_expecting_uuid(TypeConstants.MODELS_ATTR)

    def test_colors_id(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.COLORS_ATTR, False)
        self.internal_test_attribute_value_expecting_uuid(TypeConstants.COLORS_ATTR)

    def test_acceleration_id(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.ACCELERATION_ATTR, False)
        self.internal_test_attribute_value_expecting_uuid(TypeConstants.ACCELERATION_ATTR)

    def test_deceleration_id(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.DECELERATION_ATTR, False)
        self.internal_test_attribute_value_expecting_uuid(TypeConstants.DECELERATION_ATTR)

    def test_occupancy_id(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.OCCUPANCY_ATTR, False)
        self.internal_test_attribute_value_expecting_uuid(TypeConstants.OCCUPANCY_ATTR)

    def test_that_sharing_is_optional(self):
        self.internal_test_effect_of_removing_attribute(TypeConstants.SHARING_ATTR, True)

    def test_sharing_values(self):
        node: etree.ElementBase = create_and_add_clean_type_element(self.target_node)
        test_tuples = [
            (TypeConstants.SHARING_VALUE_NONE, True),
            (TypeConstants.SHARING_VALUE_HOV, True),
            (TypeConstants.SHARING_VALUE_TRANSIT, True),
            ('', False),
            ('00812', False),
        ]
        for (value, expected_result) in test_tuples:
            node.attrib[TypeConstants.SHARING_ATTR] = value
            self.assertEqual(self.doc.validate(), expected_result)

    def test_that_other_attributes_are_okay(self):
        node: etree.ElementBase = create_and_add_clean_type_element(self.target_node)
        node.attrib['other-attribute'] = 'other value'
        self.assertTrue(self.doc.validate())

    def test_that_other_sub_elements_are_banned(self):
        node: etree.ElementBase = create_and_add_clean_type_element(self.target_node)
        etree.SubElement(node, 'other-element')
        self.assertFalse(self.doc.validate())


if __name__ == '__main__':
    unittest.main()
