from lxml import etree
from uuid import uuid4 as UUID
import unittest

def addConnLinkSelBehaviorShare(distr, occur, value):
    shareElement = etree.SubElement(distr, 'share')
    shareElement.attrib['occurence'] = str(occur)
    shareElement.attrib['value'] = value 
    shareElement.attrib['alias'] = value.lower()

    return shareElement

def createCleanConnLinkSelBehavior():
    e = etree.Element('distribution')
    e.attrib['name'] = 'Default'
    e.attrib['uuid'] = str(UUID())
    e.attrib['isdefault'] = 'true'

    addConnLinkSelBehaviorShare(e, 0.15, 'NEAREST')
    addConnLinkSelBehaviorShare(e, 0.35, 'FARTHEST')
    addConnLinkSelBehaviorShare(e, 0.35, 'BEST')
    addConnLinkSelBehaviorShare(e, 0.15, 'RANDOM')

    return e

def createCleanNormalDistributionNode(name, mean, sd, minValue = None, maxValue = None):
    e = etree.Element('normal-distribution')
    e.attrib['name'] = name
    e.attrib['uuid'] = str(UUID())
    e.attrib['mean'] = str(mean)
    e.attrib['standard-deviation'] = str(sd)
    if (minValue):
        e.attrib['min-value'] = str(minValue)
    if (maxValue):
        e.attrib['max-value'] = str(maxValue)
    
    return e

def createCleanEmpiricalDistributionNode(name, valuesTuples):
    e = etree.Element('empirical-distribution')
    e.attrib['name'] = name
    e.attrib['uuid'] = str(UUID())
    for mapping in valuesTuples:
        dp = etree.SubElement(e, 'dp')
        dp.attrib['prob'] = str(mapping[0])
        dp.attrib['val'] = str(mapping[1])
        if (mapping[0] == 0.85):
            dp.attrib['desc'] = '85th percentile'

    return e 

def createCleanRawEmpiricalDistributionNode(name, values):
    e = etree.Element('raw-empirical-distribution')
    e.attrib['name'] = name
    e.attrib['uuid'] = str(UUID())
    for i, value in enumerate(values):
        dp = etree.SubElement(e, 'dp', {'value': str(value), 'customAttribute': str(i)})
        e.append(dp)
    return e

class CleanDistributionsDocument:
    def __init__(self):
        NSMAP = {"xsi" : 'http://www.w3.org/2001/XMLSchema-instance'}

        self.documentRoot = etree.Element('distributions', nsmap = NSMAP)
        self.documentRoot.attrib['{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'] = '../distributions.xsd'

        self.connectorLinkSelectionBehaviorsNode = etree.SubElement(self.documentRoot, 'distribution-set')
        self.connectorLinkSelectionBehaviorsNode.attrib['type'] = 'connector-link-selection-behaviors'
        self.connectorLinkSelectionBehaviorsNode.append(createCleanConnLinkSelBehavior())

        self.connectorMaxPositioningDistancesNode = etree.SubElement(self.documentRoot, 'distribution-set')
        self.connectorMaxPositioningDistancesNode.attrib['type'] = 'connector-max-positioning-distance'
        firstNormalDist = createCleanNormalDistributionNode('Default', 1609, 402, minValue=400)
        firstNormalDist.attrib['median'] = '1600'
        self.connectorMaxPositioningDistancesNode.append(firstNormalDist)
        self.connectorMaxPositioningDistancesNode.append(createCleanNormalDistributionNode('Aggressive', 804.5, 201, minValue=300, maxValue=1000))
        self.connectorMaxPositioningDistancesNode.append(createCleanEmpiricalDistributionNode("Observed by advanced technology", 
            [(0, 2000), (0.15, 1500), (0.85, 800), (1, 400)]))
        values = [1525.1118, 2202.5331, 1257.0525, 1577.4787,  831.2836,
                  1304.6679, 1109.5408, 1702.9872, 1945.2201, 2457.4059,
                  1692.9078, 1556.1454, 1397.7309, 1578.0382, 2232.6108,
                  2037.6286, 1629.7739,  897.0939,  910.1857, 1023.5309, 
                  1756.4594]
        self.connectorMaxPositioningDistancesNode.append(createCleanRawEmpiricalDistributionNode('Observed LC Distances', values))

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
        xsDoc = etree.parse('xml/distributions.xsd')
        xsd = etree.XMLSchema(xsDoc)
        return xsd.validate(self.getDocument())

    def getConnectorLinkSelectionBehaviorsNode(self):
        return self.connectorLinkSelectionBehaviorsNode
    
    def getConnectorMaxPositioningDistancesNode(self):
        return self.connectorMaxPositioningDistancesNode

class TestsForCleanDocument(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatConnectorLinkSelectionBehaviorNodeExists(self):
        self.assertIsNotNone(self.doc.getConnectorLinkSelectionBehaviorsNode)

    def testThatConnectorMaxPositioningDistancesNodeExists(self):
        self.assertIsNotNone(self.doc.getConnectorMaxPositioningDistancesNode)

    #
    #   TODO As more data is added to the parameters file, add more testThatXxxNodeExists() methods
    #

    def testThatCleanDocumentValidates(self):
        self.assertTrue(self.doc.validate())

class TestsForSimpleDataTypes(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()
    
    def testThatUuidsAreBeingValidated(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['uuid'] = 'invalid-uuid'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatStandardDeviationsAreBeingValidated(self):
        node = createCleanNormalDistributionNode('name', 0, -1)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    #
    #   TODO As more simple types are added to the parameters file, add more of these methods
    #

class TestsForNormalDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatMeanIsRequired(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib.pop('mean')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatMeanMustBeNumeric(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['mean'] = 'not numeric!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatStandardDeviationIsRequired(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib.pop('standard-deviation')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatStandardDeviationMustBeNumeric(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['standard-deviation'] = 'not numeric!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatStandardDeviationMustBeNonnegative(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['standard-deviation'] = '-1'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatStandardDeviationZeroIsOkay(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['standard-deviation'] = '0'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatReverseIsBoolean(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['reverse'] = 'truuuue'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatReverseIsBoolean2(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['reverse'] = 'true'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatReverseIsBoolean3(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['reverse'] = 'false'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib.pop('uuid')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValid(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['uuid'] = 'not a uuid!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatNameIsOptional(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib.pop('name')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatBothLimitsAreAllowed(self):
        node = createCleanNormalDistributionNode('name', 0, 1, -2, 2)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatLowerLimitOnlyIsAllowed(self):
        node = createCleanNormalDistributionNode('name', 0, 1, -2)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatUpperLimitOnlyIsAllowed(self):
        node = createCleanNormalDistributionNode('name', 0, 1, maxValue=2)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatElementCannotHaveSubelements(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        etree.SubElement(node, 'subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherAttributesAreOkay(self):
        node = createCleanNormalDistributionNode('name', 0, 1)
        node.attrib['a-new-attribute'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())


class TestsForEmpiricalDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatDataCountCannotBeZero(self):
        node = createCleanEmpiricalDistributionNode('name', [])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatProbabilityMustNotBeNegative(self):
        node = createCleanEmpiricalDistributionNode('name', [(-1, 4)])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatProbabilityMustNotBeGreaterThanOne(self):
        node = createCleanEmpiricalDistributionNode('name', [(2, 4)])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatProbabilityOfZeroIsOkay(self):
        node = createCleanEmpiricalDistributionNode('name', [(0, 4)])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatProbabilityOfOneIsOkay(self):
        node = createCleanEmpiricalDistributionNode('name', [(1, 4)])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatProbabilityOfOneHalfIsOkay(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatProbabilityIsRequired(self):
        node = createCleanEmpiricalDistributionNode('name', [(0, 4)])
        etree.SubElement(node, 'dp', {'val': '4'})
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatProbabilityMustBeNumeric(self):
        node = createCleanEmpiricalDistributionNode('name', [('probability', 4)])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatValueIsRequired(self):
        node = createCleanEmpiricalDistributionNode('name', [(0, 4)])
        etree.SubElement(node, 'dp', {'prob': '0.5'})
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatValueMustBeNumeric(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 'value')])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatNameIsOptional(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        node.attrib.pop('name')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        node.attrib.pop('uuid')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValid(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        node.attrib['uuid'] = 'not a uuid!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatMultiplePointsAreOkay(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4), (0.8, 5), (0.9, 10), (1.0, 15)])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatOneThousandsPointsAreOkay(self):
        points = [(i * 0.001, i) for i in range(1000)]
        node = createCleanEmpiricalDistributionNode('name', points)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatOtherSubelementsAreBanned(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        etree.SubElement(node, 'another-subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherAttributesAreOkay(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        node.attrib['a-new-attribute'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatObservationSubAttributesAreBanned(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        observation = etree.Element('dp', {'prob': '0.6', 'val': '5'})
        etree.SubElement(observation, 'subelement')
        node.append(observation)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherObservationAttributesAreOkay(self):
        node = createCleanEmpiricalDistributionNode('name', [(0.5, 4)])
        etree.SubElement(node, 'dp', {'prob': '0.6', 'val': '5', 'otherattribute': 'okay!'})
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

class TestsForRawEmpiricalDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()
        self.values = self.createValueSet()

    def createValueSet(self):
        return [128.97, 129.36, 117.36, 141.92,  65.82,
                101.74,  91.67,  50.82,  85.34, 111.96,
                 82.23, 117.07, 123.26,  70.19,  92.38,
                 78.59, 107.46, 103.81, 124.06,  54.93]
    
    def testThatNameIsOptional(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        node.attrib.pop('name')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        node.attrib.pop('uuid')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatUuidIsValid(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        node.attrib['uuid'] = 'not a uuid!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherSubelementsAreBanned(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        etree.SubElement(node, 'another-subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherAttributesAreOkay(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        node.attrib['another-attribute'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatObservationSubAttributesAreBanned(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        dpNode = etree.SubElement(node, 'dp', {'value': '1234'})
        etree.SubElement(dpNode, 'another-subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherObservationAttributesAreOkay(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        etree.SubElement(node, 'dp', {'value': '1234', 'another-attr': 'okay!'})
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatValueIsRequired(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        etree.SubElement(node, 'dp', {'other-attr': 'blah'})
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatValueMustBeNumeric(self):
        node = createCleanRawEmpiricalDistributionNode('name', self.values)
        etree.SubElement(node, 'dp', {'value': 'not numeric!'})
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatDataCountCannotBeZero(self):
        node = createCleanRawEmpiricalDistributionNode('name', [])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatDataCountCanBeOne(self):
        node = createCleanRawEmpiricalDistributionNode('name', [5])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatOneThousandsPointsAreOkay(self):
        points = [i * 0.25 for i in range(1000)]
        node = createCleanRawEmpiricalDistributionNode('name', points)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

class TestsForConnectorLinkSelectionBehaviorDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()
        self.cleanDistr = createCleanConnLinkSelBehavior()
    
    def testThatEnumDistributionCanBeAdded(self):
        node = self.doc.getConnectorLinkSelectionBehaviorsNode()
        distr = createCleanConnLinkSelBehavior()
        node.append(distr)
        self.assertTrue(self.doc.validate())

    def testThatOtherSubelementsAreBanned(self):
        node = self.doc.getConnectorLinkSelectionBehaviorsNode()
        etree.SubElement(node, 'another-element')
        self.assertFalse(self.doc.validate())
    
    def testThatOtherAttributesAreBanned(self):
        node = self.doc.getConnectorLinkSelectionBehaviorsNode()
        node.attrib['new-attribute'] = 'banned'
        self.assertFalse(self.doc.validate())

    def testThatNameIsOptional(self):
        self.cleanDistr.attrib.pop('name')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        self.cleanDistr.attrib.pop('uuid')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValid(self):
        self.cleanDistr.attrib['uuid'] = 'not a uuid!'
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatShareMustBeNumeric(self):
        addConnLinkSelBehaviorShare(self.cleanDistr, 'non numeric!', 'BEST')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())

    def testThatShareMustBeNonnegative(self):
        addConnLinkSelBehaviorShare(self.cleanDistr, -0.25, 'BEST')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())

    def testThatShareMayBeZero(self):
        addConnLinkSelBehaviorShare(self.cleanDistr, 0.00, 'BEST')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertTrue(self.doc.validate())

    def testThatInvalidValuesCannotBeUsed(self):
        addConnLinkSelBehaviorShare(self.cleanDistr, 0.30, 'DOPIEST')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatShareSubelementsAreBanned(self):
        sub = addConnLinkSelBehaviorShare(self.cleanDistr, 0.25, 'BEST')
        etree.SubElement(sub, 'sub-element')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherShareAttributesAreOkay(self):
        sub = addConnLinkSelBehaviorShare(self.cleanDistr, 0.25, 'BEST')
        sub.attrib['another-element'] = 'ok!'
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertTrue(self.doc.validate())

class TestsForConnectorMaxPositioningDistance(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatNormalDistributionCanBeAdded(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        distr = createCleanNormalDistributionNode('name', 1, 2)
        node.append(distr)
        self.assertTrue(self.doc.validate())

    def testThatEmpiricalDistributionCanBeAdded(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        distr = createCleanEmpiricalDistributionNode('name', [(0, 3), (0.15, 4), (0.85, 5), (1.0, 6)])
        node.append(distr)
        self.assertTrue(self.doc.validate())
    
    def testThatRawEmpiricalDistributionCanBeAdded(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        distr = createCleanRawEmpiricalDistributionNode('name', [3, 4, 5, 6])
        node.append(distr)
        self.assertTrue(self.doc.validate())

    def testThatOtherSubelementsAreBanned(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        etree.SubElement(node, 'another-element')
        self.assertFalse(self.doc.validate())
    
    def testThatOtherAttributesAreBanned(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        node.attrib['new-attribute'] = 'banned'
        self.assertFalse(self.doc.validate())

if (__name__ == '__main__'):
    unittest.main()
