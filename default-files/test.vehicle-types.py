from lxml import etree
import unittest


def does_uuid_exist_in_collection(uuid: str, collection: etree.ElementBase) -> bool:
    # helper function to avoid repetition in tests

    def is_it_this_node(node: etree.ElementBase) -> bool:
        return node.attrib['uuid'] == uuid

    return any(map(is_it_this_node, collection))


class TestsForVehicleTypes(unittest.TestCase):
    _vehicle_model_distributions_index = 2
    _color_distributions_index = 3
    _acceleration_distributions_index = 4
    _deceleration_distributions_index = 5
    _occupancy_distributions_index = 10

    def setUp(self) -> None:
        _distributions_document: etree._ElementTree = etree.parse('default.distributions.xml')
        self._distributions_list: etree.ElementBase = _distributions_document.getroot()

        self._vehicle_classes_document: etree._ElementTree = etree.parse('default.vehicle-types.xml')
        self._vehicle_types_list: etree.ElementBase = self._vehicle_classes_document.getroot()[0]

        # remember that direct children of the above nodes can be accessed by index

    def test_that_file_validates(self):
        xs_doc = etree.parse('../xml/vehicle-types.xsd')
        xsd = etree.XMLSchema(xs_doc)
        self.assertTrue(xsd.validate(self._vehicle_classes_document))

    def test_that_type_uuids_are_unique(self):
        # if uuids are unique, then reducing the collection into a set of its uuids will result in a set
        # with the same number of elements as the collection itself.

        uuid_set = set(map(lambda node: node.attrib['uuid'], self._vehicle_types_list))
        self.assertEqual(len(uuid_set), len(self._vehicle_types_list))

    def test_that_all_types_have_names(self):
        # while the XSD doesn't require this, we want our default files to not have nameless elements,
        # because nameless elements are meaningless to the modeler.

        def is_acceptable(node: etree.ElementBase) -> bool:
            return ('name' in node.attrib and
                    len(node.attrib['name'].strip()) > 0)

        self.assertTrue(all(map(is_acceptable, self._vehicle_types_list)))

    def are_references_intact_for_certain_attribute(self, attribute: str, distribution_index: int) -> bool:
        # helper function to avoid duplication in tests

        def is_this_node_ok(node: etree.ElementBase) -> bool:
            return does_uuid_exist_in_collection(node.attrib[attribute], self._distributions_list[distribution_index])

        return all(map(is_this_node_ok, self._vehicle_types_list))

    def test_model_references_exist(self):
        self.assertTrue(self.are_references_intact_for_certain_attribute(
            'models', self._vehicle_model_distributions_index))

    def test_color_references_exist(self):
        self.assertTrue(self.are_references_intact_for_certain_attribute('colors', self._color_distributions_index))

    def test_acceleration_references_exist(self):
        self.assertTrue(self.are_references_intact_for_certain_attribute(
            'acceleration', self._acceleration_distributions_index))

    def test_deceleration_references_exist(self):
        self.assertTrue(self.are_references_intact_for_certain_attribute(
            'deceleration', self._deceleration_distributions_index))

    def test_occupancy_references_exist(self):
        self.assertTrue(self.are_references_intact_for_certain_attribute(
            'occupancy', self._occupancy_distributions_index))


if __name__ == '__main__':
    unittest.main()
