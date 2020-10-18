import unittest

from lxml import etree


def print_document_to_console(document):
    print(etree.tostring(document,
                         xml_declaration=False, pretty_print=True, encoding='unicode'))


def get_uuid_counts(object_list, attribute='uuid'):
    uuid_counts = {}

    for item in object_list:
        uuid = item.attrib[attribute]
        if uuid in uuid_counts:
            uuid_counts[uuid] = uuid_counts[uuid] + 1
        else:
            uuid_counts[uuid] = 1

    return uuid_counts


def get_collection_element(collection_name):
    doc = etree.parse('default.distributions.xml')
    filterer = create_collection_filterer(collection_name)
    matching_collections = list(filter(filterer, doc.getroot()))
    return matching_collections[0]


class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.doc = etree.parse('default.distributions.xml')

    def testThatDocumentValidates(self):
        xsd_path = '../xml/distributions.xsd'
        xs_doc = etree.parse(xsd_path)
        xsd = etree.XMLSchema(xs_doc)
        validates = xsd.validate(self.doc)
        self.assertTrue(validates)


def create_collection_filterer(collection_name):
    def filterer(collection):
        name = collection.attrib['type']
        return name == collection_name

    return filterer


class TestCaseWithUuidUniquenessChecker(unittest.TestCase):
    def check_that_uuids_are_unique(self, collection, collection_name: str = None) -> None:
        if collection_name is not None:
            print(collection_name, '... ', sep='', end='')

        uuid_counts = get_uuid_counts(collection)
        if len(uuid_counts) > 0:
            self.assertEqual(max(uuid_counts.values()), 1)
        else:
            # there are no elements in the list, so the test passes
            self.assertTrue(4 == 4)


class TestsForCollectionsWhichOnlyRequireUuidUniqueness(TestCaseWithUuidUniquenessChecker):
    def tests(self):
        collections = [
            'connector-link-selection-behaviors',
            'connector-max-positioning-distance',
            'colors',
            'acceleration',
            'max-deceleration',
            'desired-acceleration-fractions',
            'desired-deceleration-fractions',
            'speed-distributions',
            'posted-speed-deviations',
            'non-transit-occupancy',
            'transit-passengers',
        ]
        for collection_name in collections:
            self.check_that_uuids_are_unique(get_collection_element(collection_name), collection_name)


class VehicleModelDistributionTests(TestCaseWithUuidUniquenessChecker):
    #
    # For this distribution set, not having duplicate uuids is required,
    # and external references to vehicle models must be resolved.
    #
    def setUp(self):
        self.collection = get_collection_element('vehicle-models')
        self.vehicles = etree.parse('default.vehicle-models.xml')

    def testThatNoUuidsAreDuplicated(self):
        self.check_that_uuids_are_unique(self.collection)

    def testThatUuidCounterCountsCorrectly(self):
        # since this collection is known to have more than one distribution
        # this function is included here
        uuid_counts = get_uuid_counts(self.collection)
        counted_uuids = len(uuid_counts)
        self.assertEqual(counted_uuids, len(self.collection))

    def testThatUuidCounterStartsWithOne(self):
        # since this collection is known to have more than one distribution
        # this function is included here
        uuid_counts = get_uuid_counts(self.collection)
        self.assertEqual(min(uuid_counts.values()), 1)

    def testThatVehicleIdsAreUniqueInEachDistribution(self):
        for distr in self.collection:
            uuid_counts = get_uuid_counts(distr, 'value')
            self.assertEqual(max(uuid_counts.values()), 1)

    def testThatVehiclesAreDefinedInModelsFile(self):
        def getVehicleByUuid(uuid):
            matches = list(filter(lambda item: item.attrib['uuid'] == uuid, self.vehicles.getroot()))
            if len(matches) == 0:
                return None
            else:
                return matches[0]

        for distr in self.collection:
            for share in distr:
                veh = getVehicleByUuid(share.attrib['value'])
                self.assertIsNotNone(veh)


if __name__ == '__main__':
    unittest.main()
