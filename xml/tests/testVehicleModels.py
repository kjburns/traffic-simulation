from lxml import etree
from uuid import uuid4 as UUID
import unittest

class RootElementConstants():
    TAG = 'vehicle-models'
    UNITS_ATTRIBUTE = 'units'
    VERSION_ATTRIBUTE = 'version'
    VEHICLE_TAG = 'vehicle-model'
    CURRENT_VERSION = 1

class UnitConstants():
    NAME_ATTRIBUTE = 'name'
    LENGTH_ATTRIBUTE = 'length'
    WIDTH_ATTRIBUTE = 'width'
    ARTICULATION_POINT_ATTRIBUTE = 'articulation-point'
    TRAILER_TAG = 'trailer'

class TrailerConstants(UnitConstants):
    TOWING_POINT_ATTRIBUTE = 'towing-point'

class LeadVehicleConstants(UnitConstants):
    UUID_ATTRIBUTE = 'uuid'

def createVehicleModel(name, length, width, articulationPoint=None):
    ret = etree.Element(RootElementConstants.VEHICLE_TAG, 
            {LeadVehicleConstants.UUID_ATTRIBUTE: str(UUID()), 
             LeadVehicleConstants.LENGTH_ATTRIBUTE: str(length), 
             LeadVehicleConstants.WIDTH_ATTRIBUTE: str(width)})
    if (name != None):
        ret.attrib[LeadVehicleConstants.NAME_ATTRIBUTE] = name
    
    if (articulationPoint != None):
        ret.attrib[LeadVehicleConstants.ARTICULATION_POINT_ATTRIBUTE] = str(articulationPoint)

    return ret

def createCleanVehicleModel():
    return createVehicleModel('vehicle name', 5, 2)

def createTrailer(name, length, width, towingPoint):
    ret = etree.Element(UnitConstants.TRAILER_TAG, 
            {TrailerConstants.LENGTH_ATTRIBUTE: str(length), 
             TrailerConstants.WIDTH_ATTRIBUTE: str(width), 
             TrailerConstants.TOWING_POINT_ATTRIBUTE: str(towingPoint)})
    if (name != None):
        ret.attrib[TrailerConstants.NAME_ATTRIBUTE] = name
    
    return ret

def createCleanTrailer():
    return createTrailer('name', 10, 2, 0.01)

class CleanVehicleModelsDocument:
    def __init__(self, units):
        NSMAP = {"xsi" : 'http://www.w3.org/2001/XMLSchema-instance'}

        self.documentRoot = etree.Element(RootElementConstants.TAG, {
                RootElementConstants.UNITS_ATTRIBUTE: str(units),
                RootElementConstants.VERSION_ATTRIBUTE: str(RootElementConstants.CURRENT_VERSION)}, 
            nsmap = NSMAP)
        self.documentRoot.attrib['{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'] = '../distributions.xsd'

        self.documentRoot.append(createVehicleModel('Ford Focus', 4.534, 1.823))

        truckModel = createVehicleModel('Ford F-150 with trailer', 5.7887, 2.029, 5.78)
        trailerModel = createTrailer('6x10 cargo trailer', 4.2926, 2.3622, 0.05)
        truckModel.append(trailerModel)

        self.documentRoot.append(truckModel)

    def printDocumentToConsole(self):
        print(etree.tostring(self.documentRoot, 
                xml_declaration=True, pretty_print=True, encoding='UTF-8')) 
    
    def writeDocumentToFile(self, filename):
        fp = open(filename, 'w')
        fp.write(etree.tostring(self.documentRoot, 
                pretty_print=True, encoding='unicode'))
        fp.close()
    
    def getDocument(self):
        return etree.ElementTree(self.getDocumentRoot())

    def getDocumentRoot(self):
        return self.documentRoot

    def validate(self) -> bool:
        xsDoc = etree.parse('xml/vehicle-models.xsd')
        xsd = etree.XMLSchema(xsDoc)
        return xsd.validate(self.getDocument())
    
    def clearAllVehicles(self):
        for child in self.documentRoot:
            self.documentRoot.remove(child)
    
#
# These tests operate with metres as the unit system. Correct specification of
# units is tested, but in general all tests with units in metres are adequate
# to test the operation of the xsd.
#

class TestsForCleanDocument(unittest.TestCase):
    def setUp(self):
        self.doc = CleanVehicleModelsDocument('metres')
    
    def testThatCleanDocumentValidates(self):
        self.assertTrue(self.doc.validate())
    
    def testThatRootElementNameIsCorrect(self):
        root = self.doc.getDocumentRoot()
        self.assertTrue(root.tag == RootElementConstants.TAG)
    
    def testThatRootElementExists(self):
        root = self.doc.getDocumentRoot()
        self.assertIsNotNone(root)
    
    def testThatRootElementHasUnitsAttribute(self):
        root = self.doc.getDocumentRoot()
        self.assertIn(RootElementConstants.UNITS_ATTRIBUTE, root.attrib)
    
    def testThatRootElementHasVersionAttribute(self):
        root = self.doc.getDocumentRoot()
        self.assertIn(RootElementConstants.VERSION_ATTRIBUTE, root.attrib)

class TestsForRootElement(unittest.TestCase):
    def setUp(self):
        self.doc = CleanVehicleModelsDocument('metres')

    def testThatUnitsMayBeMetres(self):
        self.assertTrue(CleanVehicleModelsDocument('metres').validate())
    
    def testThatUnitsMayBeMeters(self):
        self.assertTrue(CleanVehicleModelsDocument('meters').validate())
    
    def testThatUnitsMayBeFeet(self):
        self.assertTrue(CleanVehicleModelsDocument('feet').validate())
    
    def testThatOtherUnitsAreBanned(self):
        self.assertFalse(CleanVehicleModelsDocument('kilometres').validate())
    
    def testThatUnitsAreRequired(self):
        self.doc.getDocumentRoot().attrib.pop(RootElementConstants.UNITS_ATTRIBUTE)
        self.assertFalse(self.doc.validate())
    
    def testThatVersionIsRequired(self):
        self.doc.getDocumentRoot().attrib.pop(RootElementConstants.VERSION_ATTRIBUTE)
        self.assertFalse(self.doc.validate())
    
    def testThatVersionMustBeNumeric(self):
        self.doc.getDocumentRoot().attrib[RootElementConstants.VERSION_ATTRIBUTE] = 'non-numeric'
        self.assertFalse(self.doc.validate())
    
    def testThatVersionMustBeAnInteger(self):
        self.doc.getDocumentRoot().attrib[RootElementConstants.VERSION_ATTRIBUTE] = '1.5'
        self.assertFalse(self.doc.validate())

    def testThatOtherAttributesAreOkInRoot(self):
        root = self.doc.getDocumentRoot()
        root.attrib['another-attribute'] = 'ok!'
        self.assertTrue(self.doc.validate())

class TestsForVehicleModels(unittest.TestCase):
    def setUp(self):
        self.doc = CleanVehicleModelsDocument('metres')

    def testThatVehicleModelCountMayNotBeZero(self):
        self.doc.clearAllVehicles()
        self.assertFalse(self.doc.validate())
    
    def testThatVehicleModelCountMayBeOne(self):
        self.doc.clearAllVehicles()
        root = self.doc.getDocumentRoot()
        root.append(createCleanVehicleModel())
        self.assertTrue(self.doc.validate())
    
    def testThatVehicleCountMayBeOneThousand(self):
        root = self.doc.getDocumentRoot()
        for _ in range(999):
            vehicle = createCleanVehicleModel()
            root.append(vehicle)
        self.assertTrue(self.doc.validate())

class TestsForSimpleTypes(unittest.TestCase):
    def setUp(self):
        self.doc = CleanVehicleModelsDocument('metres')

    def testThatUuidsAreBeingValidated(self):
        firstElement = self.doc.getDocumentRoot()[0]
        firstElement.attrib[LeadVehicleConstants.UUID_ATTRIBUTE] = 'not a valid uuid!'
        self.assertFalse(self.doc.validate())

class TestsForLeadVehicles(unittest.TestCase):
    def setUp(self):
        self.doc = CleanVehicleModelsDocument('metres')
    
    def getFirstElement(self):
        return self.doc.getDocumentRoot()[0]
    
    def testThatFirstElementIsAVehicleModel(self):
        self.assertTrue(self.getFirstElement().tag == RootElementConstants.VEHICLE_TAG)

    def testThatNameIsOptional(self):
        self.getFirstElement().attrib.pop(LeadVehicleConstants.NAME_ATTRIBUTE)
        self.assertTrue(self.doc.validate())
    
    def testThatNameMayBeAnEmptyString(self):
        self.getFirstElement().attrib[LeadVehicleConstants.NAME_ATTRIBUTE] = ''
        self.assertTrue(self.doc.validate())
    
    def testThatNameMayBeANonEmptyString(self):
        self.getFirstElement().attrib[LeadVehicleConstants.NAME_ATTRIBUTE] = 'a non-empty string'
        self.assertTrue(self.doc.validate())
    
    def testThatLengthIsRequired(self):
        self.getFirstElement().attrib.pop(LeadVehicleConstants.LENGTH_ATTRIBUTE)
        self.assertFalse(self.doc.validate())
    
    def testThatLengthMayNotBeNegative(self):
        self.getFirstElement().attrib[LeadVehicleConstants.LENGTH_ATTRIBUTE] = '-1'
        self.assertFalse(self.doc.validate())
    
    def testThatLengthMayNotBeZero(self):
        self.getFirstElement().attrib[LeadVehicleConstants.LENGTH_ATTRIBUTE] = '0'
        self.assertFalse(self.doc.validate())
    
    def testThatLengthMayBePositive(self):
        self.getFirstElement().attrib[LeadVehicleConstants.LENGTH_ATTRIBUTE] = '1'
        self.assertTrue(self.doc.validate())
    
    def testThatLengthMustBeNumeric(self):
        self.getFirstElement().attrib[LeadVehicleConstants.LENGTH_ATTRIBUTE] = 'not a number'
        self.assertFalse(self.doc.validate())

    def testThatWidthIsRequired(self):
        self.getFirstElement().attrib.pop(LeadVehicleConstants.WIDTH_ATTRIBUTE)
        self.assertFalse(self.doc.validate())
    
    def testThatWidthMayNotBeNegative(self):
        self.getFirstElement().attrib[LeadVehicleConstants.WIDTH_ATTRIBUTE] = '-1'
        self.assertFalse(self.doc.validate())
    
    def testThatWidthMayNotBeZero(self):
        self.getFirstElement().attrib[LeadVehicleConstants.WIDTH_ATTRIBUTE] = '0'
        self.assertFalse(self.doc.validate())
    
    def testThatWidthMayBePositive(self):
        self.getFirstElement().attrib[LeadVehicleConstants.WIDTH_ATTRIBUTE] = '1'
        self.assertTrue(self.doc.validate())
    
    def testThatWidthMustBeNumeric(self):
        self.getFirstElement().attrib[LeadVehicleConstants.WIDTH_ATTRIBUTE] = 'not a number'
        self.assertFalse(self.doc.validate())
    
    def getSecondElement(self):
        return self.doc.getDocumentRoot()[1]
    
    def testThatArticulationPointIsOptional(self):
        #
        # Even though this vehicle has a trailer, there is not a way
        # for xsd to require this attribute when a trailer is present.
        # Therefore, even though the test succeeds here, it would still
        # generate an error/warning by the simulator, or the simulator
        # would have to assume a default value (such as the end of the
        # lead vehicle).
        #
        self.getSecondElement().attrib.pop(LeadVehicleConstants.ARTICULATION_POINT_ATTRIBUTE)
        self.assertTrue(self.doc.validate())
    
    def testThatArticulationPointMayNotBeNegative(self):
        self.getSecondElement().attrib[LeadVehicleConstants.ARTICULATION_POINT_ATTRIBUTE] = '-1'
        self.assertFalse(self.doc.validate())
    
    def testThatArticulationPointMayNotBeZero(self):
        self.getSecondElement().attrib[LeadVehicleConstants.ARTICULATION_POINT_ATTRIBUTE] = '0'
        self.assertFalse(self.doc.validate())
    
    def testThatArticulationPointMayBePositive(self):
        self.getSecondElement().attrib[LeadVehicleConstants.ARTICULATION_POINT_ATTRIBUTE] = '1'
        self.assertTrue(self.doc.validate())

    def testThatArticulationPointMustBeNumeric(self):
        self.getSecondElement().attrib[LeadVehicleConstants.ARTICULATION_POINT_ATTRIBUTE] = 'not a number!'
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        self.getFirstElement().attrib.pop(LeadVehicleConstants.UUID_ATTRIBUTE)
        self.assertFalse(self.doc.validate())
    
    def testThatArbitrarySubelementsAreBanned(self):
        etree.SubElement(self.getFirstElement(), 'arbitrary-subelement')
        self.assertFalse(self.doc.validate())
    
    def testThatArbitraryAttributesAreOk(self):
        self.getFirstElement().attrib['arbitrary-attribute'] = 'value'
        self.assertTrue(self.doc.validate())
    
class TestsForTrailers(unittest.TestCase):
    def setUp(self):
        self.doc = CleanVehicleModelsDocument('metres')
        self.testLeadVehicle = createCleanVehicleModel()
        self.testLeadVehicle.attrib[LeadVehicleConstants.NAME_ATTRIBUTE] = 'lead'
        self.testLeadVehicle.attrib[LeadVehicleConstants.ARTICULATION_POINT_ATTRIBUTE] = '4.8'
        self.doc.getDocumentRoot().append(self.testLeadVehicle)
    
    def testThatTestLeadVehicleValidates(self):
        self.assertTrue(self.doc.validate())

    def testThatATrailerCanBeAdded(self):
        trailer = createCleanTrailer()
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())

    def testThatMultipleTrailersCannotBeAttachedToLeadVehicle(self):
        for _ in range(2):
            trailer = createCleanTrailer()
            self.testLeadVehicle.append(trailer)
        
        self.assertFalse(self.doc.validate())
    
    def addTrailersToLeadVehicle(self, numTrailers):
        towingVehicle = self.testLeadVehicle
        for _ in range(numTrailers):
            trailer = createCleanTrailer()
            towingVehicle.append(trailer)
            towingVehicle = trailer
    
    def testThatMultipleTrailersCanBeChained(self):
        self.addTrailersToLeadVehicle(2)
        self.assertTrue(self.doc.validate())
    
    def testThatOneThousandTrailersCanBeChained(self):
        self.addTrailersToLeadVehicle(1000)
        self.assertTrue(self.doc.validate)
    
    def testThatNameIsOptional(self):
        trailer = createCleanTrailer()
        trailer.attrib.pop(TrailerConstants.NAME_ATTRIBUTE)
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())
    
    def testThatNameMayBeAnEmptyString(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.NAME_ATTRIBUTE] = ''
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())

    def testThatNameMayBeANonEmptyString(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.NAME_ATTRIBUTE] = 'a non-empty string'
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())
    
    def testThatLengthIsRequired(self):
        trailer = createCleanTrailer()
        trailer.attrib.pop(TrailerConstants.LENGTH_ATTRIBUTE)
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatLengthMayBePositive(self):
        trailer = createCleanTrailer()
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())

    def testThatLengthMayNotBeNegative(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.LENGTH_ATTRIBUTE] = '-10'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatLengthMayNotBeZero(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.LENGTH_ATTRIBUTE] = '0'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatLengthMustBeNumeric(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.LENGTH_ATTRIBUTE] = 'non-numeric'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatWidthIsRequired(self):
        trailer = createCleanTrailer()
        trailer.attrib.pop(TrailerConstants.WIDTH_ATTRIBUTE)
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())

    def testThatWidthMayBePositive(self):
        trailer = createCleanTrailer()
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())

    def testThatWidthMayNotBeNegative(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.WIDTH_ATTRIBUTE] = '-1'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatWidthMayNotBeZero(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.WIDTH_ATTRIBUTE] = '0'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatWidthMustBeNumeric(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.WIDTH_ATTRIBUTE] = 'non-numeric'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatArticulationPointIsAllowed(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.ARTICULATION_POINT_ATTRIBUTE] = '9.9'
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())
    
    def testThatArticulationPointMayBePositive(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.ARTICULATION_POINT_ATTRIBUTE] = '9.9'
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())
    
    def testThatArticulationPointMayNotBeNegative(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.ARTICULATION_POINT_ATTRIBUTE] = '-5'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatArticulationPointMayNotBeZero(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.ARTICULATION_POINT_ATTRIBUTE] = '0'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatArticulationPointMustBeNumeric(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.ARTICULATION_POINT_ATTRIBUTE] = 'non-numeric'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatTowingPointIsRequired(self):
        trailer = createCleanTrailer()
        trailer.attrib.pop(TrailerConstants.TOWING_POINT_ATTRIBUTE)
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatTowingPointMustBeNumeric(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.TOWING_POINT_ATTRIBUTE] = 'non-numeric'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatTowingPointMayBePositive(self):
        trailer = createCleanTrailer()
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())
    
    def testThatTowingPointMayNotBeZero(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.TOWING_POINT_ATTRIBUTE] = '0'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())

    def testThatTowingPointMayNotBeNegative(self):
        trailer = createCleanTrailer()
        trailer.attrib[TrailerConstants.TOWING_POINT_ATTRIBUTE] = '-1'
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatArbitrarySubelementsAreBanned(self):
        trailer = createCleanTrailer()
        etree.SubElement(trailer, 'arbitrary-subelement')
        self.testLeadVehicle.append(trailer)
        self.assertFalse(self.doc.validate())
    
    def testThatArbitraryAttributesAreOk(self):
        trailer = createCleanTrailer()
        trailer.attrib['arbitrary-attribute'] = 'value'
        self.testLeadVehicle.append(trailer)
        self.assertTrue(self.doc.validate())
    
if (__name__ == '__main__'):
    unittest.main()
