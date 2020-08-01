import unittest
from lxml import etree
from io import StringIO

class DistributionsTestsBase(unittest.TestCase):
    def printDocumentToConsole(self, document):
        print(etree.tostring(document, 
                xml_declaration=False, pretty_print=True, encoding='unicode')) 

    def getUuidCounts(self, list, attribute = 'uuid'):
        uuidCounts = {}

        for item in list:
            uuid = item.attrib[attribute]
            if (uuid in uuidCounts):
                uuidCounts[uuid] = uuidCounts[uuid] + 1
            else:
                uuidCounts[uuid] = 1
        
        return uuidCounts
    
    def getCollectionElement(self, collectionName):
        doc = etree.parse('default.distributions.xml')
        filterer = createCollectionFilterer(collectionName)
        matchingCollections = list(filter(filterer, doc.getroot()))
        return matchingCollections[0]

class DocumentTests(DistributionsTestsBase):
    def setUp(self):
        self.doc = etree.parse('default.distributions.xml')

    def testThatDocumentValidates(self):
        xsdPath = '../xml/distributions.xsd'
        xsDoc = etree.parse(xsdPath) 
        xsd = etree.XMLSchema(xsDoc)
        validates = xsd.validate(self.doc)
        self.assertTrue(validates)

def createCollectionFilterer(collectionName):
    def filterer(collection):
        name = collection.attrib['type']
        return name == collectionName

    return filterer

class ConnectorLinkSelectionBehaviorTests(DistributionsTestsBase):
    #
    # For this distribution set, not having duplicate uuids is adequate,
    # as there are no external references to be resolved.
    #
    def setUp(self):
        self.collection = self.getCollectionElement('connector-link-selection-behaviors')

    def testThatNoUuidsAreDuplicated(self):
        uuidCounts = self.getUuidCounts(self.collection)
        self.assertEqual(max(uuidCounts.values()), 1)

class ConnectorMaxPositioningDistanceTests(DistributionsTestsBase):
    #
    # For this distribution set, not having duplicate uuids is adequate,
    # as there are no external references to be resolved.
    # This distribution set may be empty.
    #
    def setUp(self):
        self.collection = self.getCollectionElement('connector-max-positioning-distance')

    def testThatNoUuidsAreDuplicated(self):
        uuidCounts = self.getUuidCounts(self.collection)
        if (len(uuidCounts) > 0):
            self.assertEqual(max(uuidCounts.values()), 1)
        else:
            # there are no elements in the list, so the test passes
            self.assertTrue(4 == 4)

class VehicleModelDistributionTests(DistributionsTestsBase):
    #
    # For this distribution set, not having duplicate uuids is required,
    # and external references to vehicle models must be resolved.
    #
    def setUp(self):
        self.collection = self.getCollectionElement('vehicle-models')
        self.vehicles = etree.parse('default.vehicle-models.xml')

    def testThatNoUuidsAreDuplicated(self):
        uuidCounts = self.getUuidCounts(self.collection)
        self.assertEqual(max(uuidCounts.values()), 1)

    def testThatUuidCounterCountsCorrectly(self):
        # since this collection is known to have more than one distribution
        # this function is included here
        uuidCounts = self.getUuidCounts(self.collection)
        countedUuids = len(uuidCounts)
        self.assertEqual(countedUuids, len(self.collection))
    
    def testThatUuidCounterStartsWithOne(self):
        # since this collection is known to have more than one distribution
        # this function is included here
        uuidCounts = self.getUuidCounts(self.collection)
        self.assertEqual(min(uuidCounts.values()), 1)
    
    def testThatVehicleIdsAreUniqueInEachDistribution(self):
        for distr in self.collection:
            uuidCounts = self.getUuidCounts(distr, 'value')
            self.assertEqual(max(uuidCounts.values()), 1)
        
    def testThatVehiclesAreDefinedInModelsFile(self):
        def getVehicleByUuid(uuid):
            matches = list(filter(lambda item: item.attrib['uuid'] == uuid, self.vehicles.getroot()))
            if (len(matches) == 0):
                return None
            else:
                return matches[0]

        for distr in self.collection:
            for share in distr:
                veh = getVehicleByUuid(share.attrib['value'])
                self.assertIsNotNone(veh)
    
class ColorDistributionTests(DistributionsTestsBase):
    #
    # For this distribution set, not having duplicate uuids is adequate,
    # as there are no external references to be resolved.
    #
    def setUp(self):
        self.collection = self.getCollectionElement('colors')

    def testThatNoUuidsAreDuplicated(self):
        uuidCounts = self.getUuidCounts(self.collection)
        self.assertEqual(max(uuidCounts.values()), 1)

class AccelFunctionDistributionTests(DistributionsTestsBase):
    #
    # For this distribution set, not having duplicate uuids is adequate,
    # as there are no external references to be resolved.
    #
    def setUp(self):
        self.collection = self.getCollectionElement('acceleration')

    def testThatNoUuidsAreDuplicated(self):
        uuidCounts = self.getUuidCounts(self.collection)
        self.assertEqual(max(uuidCounts.values()), 1)

if (__name__ == '__main__'):
    unittest.main()

