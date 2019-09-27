import unittest
from lxml import etree
from io import StringIO

class VehicleTypesTests(unittest.TestCase):
    def setUp(self):
        self.doc = etree.parse('default.vehicle-models.xml')
    
    def testThatDocumentValidates(self):
        xsdPath = '../xml/vehicle-models.xsd'
        xsDoc = etree.parse(xsdPath) 
        xsd = etree.XMLSchema(xsDoc)
        validates = xsd.validate(self.doc)
        self.assertTrue(validates)
    
    def testThatNoUuidsAreDuplicated(self):
        uuidCounts = self.getUuidCounts()
        self.assertEqual(max(uuidCounts.values()), 1)
    
    def testThatUuidCounterCountsCorrectly(self):
        uuidCounts = self.getUuidCounts()
        countedUuids = len(uuidCounts)
        self.assertEqual(countedUuids, len(self.doc.getroot()))
    
    def testThatUuidCounterStartsWithOne(self):
        uuidCounts = self.getUuidCounts()
        self.assertEqual(min(uuidCounts.values()), 1)
    
    def getUuidCounts(self):
        uuidCounts = {}

        for model in self.doc.getroot():
            uuid = model.attrib['uuid']
            if (uuid in uuidCounts):
                uuidCounts[uuid] = uuidCounts[uuid] + 1
            else:
                uuidCounts[uuid] = 1
        
        return uuidCounts

    def printDocumentToConsole(self, document):
        print(etree.tostring(document, 
                xml_declaration=False, pretty_print=True, encoding='unicode')) 

if (__name__ == '__main__'):
    unittest.main()

