from lxml import etree
from uuid import uuid4 as UUID
from random import randint
import unittest

class DistributionSetConstants:
    TAG = 'distribution-set'
    TYPE_ATTR = 'type' 

class DistributionShareConstants:
    TAG = 'share'
    OCCURENCE_ATTR = 'occurence'
    VALUE_ATTR = 'value'

class EnumDistributionShareConstants(DistributionShareConstants):
    pass

class EnumDistributionSetConstants:
    CHILD_TAG = 'distribution'

class EnumDistributionConstants:
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'

class VehicleModelDistributionConstants:
    TAG = 'distribution'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'

class ConnectorLinkSelectionBehaviorDistributionConstants:
    NEAREST = 'NEAREST'
    FARTHEST = 'FARTHEST'
    BEST = 'BEST'
    RANDOM = 'RANDOM'

class NormalDistributionConstants:
    TAG = 'normal-distribution'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    MEAN_ATTR = 'mean'
    SD_ATTR = 'standard-deviation'
    MIN_VALUE_ATTR = 'min-value'
    MAX_VALUE_ATTR = 'max-value'
    REVERSE_ATTR = 'reverse'

class EmpiricalDistributionConstants:
    TAG = 'empirical-distribution'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    DATA_POINT_TAG = 'dp'
    DATA_POINT_PROBABILITY_ATTR = 'prob'
    DATA_POINT_VALUE_ATTR = 'val'

class RawEmpiricalDistributionConstants:
    TAG = 'raw-empirical-distribution'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    AGGRESSION_ATTR = 'aggression'
    AGGRESSION_VALUE_POSITIVE = 'positive'
    AGGRESSION_VALUE_NEGATIVE = 'negative'
    DATA_POINT_TAG = 'dp'
    DATA_POINT_VALUE_ATTR = 'value'

class BinnedDistributionConstants:
    TAG = 'binned-distribution'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    AGGRESSION_ATTR = 'aggression'
    AGGRESSION_VALUE_POSITIVE = 'positive'
    AGGRESSION_VALUE_NEGATIVE = 'negative'
    AGGRESSION_VALUE_NONE = 'none'
    BIN_TAG = 'bin'
    BIN_MIN_VALUE_ATTR = 'min-value'
    BIN_MAX_VALUE_ATTR = 'max-value'
    BIN_COUNT_ATTR = 'count'

def addBinnedDistributionBin(distr, minValue, maxValue, count):
    binElement = etree.SubElement(distr, BinnedDistributionConstants.BIN_TAG)
    binElement.attrib[BinnedDistributionConstants.BIN_MIN_VALUE_ATTR] = str(minValue)
    binElement.attrib[BinnedDistributionConstants.BIN_MAX_VALUE_ATTR] = str(maxValue)
    binElement.attrib[BinnedDistributionConstants.BIN_COUNT_ATTR] = str(count)

    return binElement

def addEnumDistributionShare(distr, occur, value):
    shareElement = etree.SubElement(distr, EnumDistributionShareConstants.TAG)
    shareElement.attrib[EnumDistributionShareConstants.OCCURENCE_ATTR] = str(occur)
    shareElement.attrib[EnumDistributionShareConstants.VALUE_ATTR] = value 
    shareElement.attrib['alias'] = value.lower()

    return shareElement

def addEmpiricalDataPoint(distributionNode, probability = None, value = None):
    ret = etree.SubElement(distributionNode, EmpiricalDistributionConstants.DATA_POINT_TAG)

    if (probability is not None):
        ret.attrib[EmpiricalDistributionConstants.DATA_POINT_PROBABILITY_ATTR] = str(probability)
    if (value is not None):
        ret.attrib[EmpiricalDistributionConstants.DATA_POINT_VALUE_ATTR] = str(value)
    
    return ret

def createCleanConnLinkSelBehavior():
    e = etree.Element(EnumDistributionSetConstants.CHILD_TAG)
    e.attrib[EnumDistributionConstants.NAME_ATTR] = 'Default'
    e.attrib[EnumDistributionConstants.UUID_ATTR] = str(UUID())
    e.attrib['isdefault'] = 'true'

    addEnumDistributionShare(e, 0.15, ConnectorLinkSelectionBehaviorDistributionConstants.NEAREST)
    addEnumDistributionShare(e, 0.35, ConnectorLinkSelectionBehaviorDistributionConstants.FARTHEST)
    addEnumDistributionShare(e, 0.35, ConnectorLinkSelectionBehaviorDistributionConstants.BEST)
    addEnumDistributionShare(e, 0.15, ConnectorLinkSelectionBehaviorDistributionConstants.RANDOM)

    return e

def createNormalDistributionNode(name, mean, sd, minValue = None, maxValue = None):
    e = etree.Element(NormalDistributionConstants.TAG)
    e.attrib[NormalDistributionConstants.NAME_ATTR] = name
    e.attrib[NormalDistributionConstants.UUID_ATTR] = str(UUID())
    e.attrib[NormalDistributionConstants.MEAN_ATTR] = str(mean)
    e.attrib[NormalDistributionConstants.SD_ATTR] = str(sd)
    if (minValue is not None):
        e.attrib[NormalDistributionConstants.MIN_VALUE_ATTR] = str(minValue)
    if (maxValue is not None):
        e.attrib[NormalDistributionConstants.MAX_VALUE_ATTR] = str(maxValue)
    
    return e

def createCleanNormalDistributionNode():
    return createNormalDistributionNode('a normal distribution', 0, 1)

def createCleanEmpiricalDistributionNode():
    return createEmpiricalDistributionNode('an empirical distribution', [(0, 5), (0.15, 10), (0.85, 15), (1, 20)])

def createEmpiricalDistributionNode(name, valuesTuples):
    e = etree.Element(EmpiricalDistributionConstants.TAG)
    if (name is not None):
        e.attrib[EmpiricalDistributionConstants.NAME_ATTR] = name
    e.attrib[EmpiricalDistributionConstants.UUID_ATTR] = str(UUID())
    for mapping in valuesTuples:
        dp = addEmpiricalDataPoint(e, mapping[0], mapping[1])
        if (mapping[0] == 0.85):
            dp.attrib['desc'] = '85th percentile'

    return e 

def createBinnedDistributionNode(name, valuesTuples, aggression):
    e = etree.Element(BinnedDistributionConstants.TAG)
    if (name is not None):
        e.attrib[BinnedDistributionConstants.NAME_ATTR] = name
    e.attrib[BinnedDistributionConstants.UUID_ATTR] = str(UUID())
    e.attrib[BinnedDistributionConstants.AGGRESSION_ATTR] = aggression

    for mapping in valuesTuples:
        addBinnedDistributionBin(e, mapping[0], mapping[1], mapping[2])

    return e

def createCleanBinnedDistributionNode():
    return createBinnedDistributionNode('A binned distribution', [
        (0, 10, 2), 
        (10, 20, 5), 
        (20, 30, 10), 
        (30, 40, 6), 
        (40, 50, 3)
    ], BinnedDistributionConstants.AGGRESSION_VALUE_NEGATIVE)

def createRawEmpiricalDistributionNode(name, values, aggrDir):
    e = etree.Element(RawEmpiricalDistributionConstants.TAG)
    e.attrib[RawEmpiricalDistributionConstants.NAME_ATTR] = name
    e.attrib[RawEmpiricalDistributionConstants.UUID_ATTR] = str(UUID())
    e.attrib[RawEmpiricalDistributionConstants.AGGRESSION_ATTR] = aggrDir
    for value in values:
        addRawEmpiricalDistributionObservation(e, value)
    return e

def addRawEmpiricalDistributionObservation(node, value = None):
    ret = etree.SubElement(node, RawEmpiricalDistributionConstants.DATA_POINT_TAG)
    if (value is not None):
        ret.attrib[RawEmpiricalDistributionConstants.DATA_POINT_VALUE_ATTR] = str(value)
    
    return ret

def addVehicleModelShare(distributionNode, occurence, value):
    ret = etree.SubElement(
        distributionNode, 
        DistributionShareConstants.TAG, 
        {
            EnumDistributionShareConstants.OCCURENCE_ATTR: str(occurence),
            EnumDistributionShareConstants.VALUE_ATTR: str(value)
        }
    )        

    return ret

def createVehicleModelsDistributionNode(attachTo, shareTuplesAsOccurence_Value, name = 'a vehicle model distribution'):
    ret = etree.SubElement(
        attachTo, 
        VehicleModelDistributionConstants.TAG, 
        {
            VehicleModelDistributionConstants.NAME_ATTR: name,
            VehicleModelDistributionConstants.UUID_ATTR: str(UUID())
        }
    )
    for shareTuple in shareTuplesAsOccurence_Value:
        addVehicleModelShare(ret, shareTuple[0], shareTuple[1])

    return ret

class ColorDistributionConstants:
    DISTRIBUTION_TYPE = 'colors'
    DISTRIBUTION_TAG = 'distribution'
    DISTRIBUTION_NAME_ATTR = 'name'
    DISTRIBUTION_UUID_ATTR = 'uuid'
    SHARE_TAG = 'share'
    SHARE_OCCURENCE_ATTR = 'occurence'
    SHARE_VALUE_ATTR = 'value'

def createAndAddColorShare(distr, occurence, color):
    ret = etree.SubElement(distr, ColorDistributionConstants.SHARE_TAG, {
        ColorDistributionConstants.SHARE_OCCURENCE_ATTR: str(occurence),
        ColorDistributionConstants.SHARE_VALUE_ATTR: color,
    })

    return ret

def createAndAddColorDistributionNode(attachTo, shareTuplesAsOccurence_Value, name = 'a color distribution'):
    ret = etree.SubElement(attachTo, ColorDistributionConstants.DISTRIBUTION_TAG, {
        ColorDistributionConstants.DISTRIBUTION_NAME_ATTR: name,
        ColorDistributionConstants.DISTRIBUTION_UUID_ATTR: str(UUID()),
    })

    for shareTuple in shareTuplesAsOccurence_Value:
        createAndAddColorShare(ret, shareTuple[0], shareTuple[1])

    return ret

def createAndAddCleanColorDistributionNode(attachTo):
    return createAndAddColorDistributionNode(attachTo, [
        [1, '#ff0000',],
        [2, '#ff8000',],
        [3, '#ffff00',],
        [4, '#00ff00',],
        [5, '#0000ff',],
        [6, '#ff00ff',],
    ])

def create_and_add_acceleration_distribution_point(accel_distr_node, speed, mean, stdev):
    dp_attributes = {
        AccelerationDistributionConstants.DATAPOINT_VELOCITY_ATTR: str(speed),
        AccelerationDistributionConstants.DATAPOINT_MEAN_ATTR: str(mean),
        AccelerationDistributionConstants.DATAPOINT_STDEV_ATTR: str(stdev),
    }
    dp = etree.SubElement(accel_distr_node, AccelerationDistributionConstants.DATAPOINT_TAG, dp_attributes)
    return dp

def create_and_add_acceleration_distribution_node(attach_to, dp_tuples_as_v_m_sd, speed_unit, accel_unit, name = 'an accel distribution'):
    main_attributes = {
        AccelerationDistributionConstants.NAME_ATTR: name,
        AccelerationDistributionConstants.UUID_ATTR: str(UUID()),
        AccelerationDistributionConstants.SPEED_UNIT_ATTR: speed_unit,
        AccelerationDistributionConstants.ACCELERATION_UNIT_ATTR: accel_unit,
    }
    ret = etree.SubElement(attach_to, AccelerationDistributionConstants.DISTRIBUTION_TAG, attrib=main_attributes)
    for dp in dp_tuples_as_v_m_sd:
        create_and_add_acceleration_distribution_point(ret, dp[0], dp[1], dp[2])
    
    return ret

def create_and_add_clean_accel_distribution_node(attach_to):
    tuples = [(0, 10, 1), (60, 2, 0.2), (100, -0.5, 0.1)]
    return create_and_add_acceleration_distribution_node(
        attach_to, tuples, SpeedUnits.MILES_PER_HOUR, AccelerationUnits.FEET_PER_SECOND_SQUARED) 

class CleanDistributionsDocument:
    def __init__(self):
        NSMAP = {"xsi" : 'http://www.w3.org/2001/XMLSchema-instance'}

        self.documentRoot = etree.Element('distributions', nsmap = NSMAP)
        self.documentRoot.attrib['{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'] = '../distributions.xsd'

        self.connectorLinkSelectionBehaviorsNode = etree.SubElement(self.documentRoot, DistributionSetConstants.TAG)
        self.connectorLinkSelectionBehaviorsNode.attrib[DistributionSetConstants.TYPE_ATTR] = 'connector-link-selection-behaviors'
        self.connectorLinkSelectionBehaviorsNode.append(createCleanConnLinkSelBehavior())

        self.connectorMaxPositioningDistancesNode = etree.SubElement(self.documentRoot, DistributionSetConstants.TAG)
        self.connectorMaxPositioningDistancesNode.attrib[DistributionSetConstants.TYPE_ATTR] = 'connector-max-positioning-distance'
        firstNormalDist = createNormalDistributionNode('Default', 1609, 402, minValue=400)
        firstNormalDist.attrib['median'] = '1600'
        self.connectorMaxPositioningDistancesNode.append(firstNormalDist)
        self.connectorMaxPositioningDistancesNode.append(createNormalDistributionNode('Aggressive', 804.5, 201, minValue=300, maxValue=1000))
        self.connectorMaxPositioningDistancesNode.append(createEmpiricalDistributionNode("Observed by advanced technology", 
            [(0, 2000), (0.15, 1500), (0.85, 800), (1, 400)]))
        values = [1525.1118, 2202.5331, 1257.0525, 1577.4787,  831.2836,
                  1304.6679, 1109.5408, 1702.9872, 1945.2201, 2457.4059,
                  1692.9078, 1556.1454, 1397.7309, 1578.0382, 2232.6108,
                  2037.6286, 1629.7739,  897.0939,  910.1857, 1023.5309, 
                  1756.4594]
        self.connectorMaxPositioningDistancesNode.append(
                createRawEmpiricalDistributionNode('Observed LC Distances', values, 
                        RawEmpiricalDistributionConstants.AGGRESSION_VALUE_NEGATIVE))
        bins = [ (0, 10, 2), (10, 20, 5), (20, 30, 10), (30, 40, 6), (40, 50, 3) ]
        self.connectorMaxPositioningDistancesNode.append(
                createBinnedDistributionNode('A binned distribution', bins, BinnedDistributionConstants.AGGRESSION_VALUE_NEGATIVE))

        self.vehicleModelsNode = etree.SubElement(
                self.documentRoot, 
                DistributionSetConstants.TAG, 
                {
                    DistributionSetConstants.TYPE_ATTR: 'vehicle-models'
                }
        )
        createVehicleModelsDistributionNode(
            self.vehicleModelsNode, 
            [
                (35, '47e301a2-f905-4245-94ef-127daf6736b7'),
                (30, '9c344e0f-30cc-44e9-ba3b-b3c1b6137bda'),
                (20, '223367cb-69a6-474c-b55f-2405f0c1ba18')
            ]
        )

        self.colorsNode = etree.SubElement(
            self.documentRoot,
            DistributionSetConstants.TAG, {
                DistributionSetConstants.TYPE_ATTR: ColorDistributionConstants.DISTRIBUTION_TYPE,
            }
        )
        createAndAddCleanColorDistributionNode(self.colorsNode)

        self.accel_functions_node = etree.SubElement(
            self.documentRoot,
            DistributionSetConstants.TAG, {
                DistributionSetConstants.TYPE_ATTR: AccelerationDistributionConstants.DISTRIBUTION_TYPE,
            }
        )
        create_and_add_clean_accel_distribution_node(self.accel_functions_node)

    def printDocumentToConsole(self):
        print(etree.tostring(self.documentRoot, 
                xml_declaration=False, pretty_print=True, encoding='unicode')) 
    
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
        xsDoc = etree.parse('../distributions.xsd')
        xsd = etree.XMLSchema(xsDoc)
        return xsd.validate(self.getDocument())

    def getConnectorLinkSelectionBehaviorsNode(self):
        return self.connectorLinkSelectionBehaviorsNode
    
    def getConnectorMaxPositioningDistancesNode(self):
        return self.connectorMaxPositioningDistancesNode

    def getVehicleModelsNode(self):
        return self.vehicleModelsNode
    
    def getColorsNode(self):
        return self.colorsNode

    def get_accelerations_node(self):
        return self.accel_functions_node

class TestsForCleanDocument(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatConnectorLinkSelectionBehaviorNodeExists(self):
        self.assertIsNotNone(self.doc.getConnectorLinkSelectionBehaviorsNode()) 

    def testThatConnectorMaxPositioningDistancesNodeExists(self):
        self.assertIsNotNone(self.doc.getConnectorMaxPositioningDistancesNode()) 

    def testThatVehicleModelsNodeExists(self):
        self.assertIsNotNone(self.doc.getVehicleModelsNode())

    #
    #   As more data is added to the parameters file, add more testThatXxxNodeExists() methods
    #

    def testThatCleanDocumentValidates(self):
        self.assertTrue(self.doc.validate())

class TestsForSimpleDataTypes(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()
    
    def testThatUuidsAreBeingValidated(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.UUID_ATTR] = 'invalid-uuid'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatStandardDeviationsAreBeingValidated(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.SD_ATTR] = '-1'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatAggressionDirectionsAreBeingValidated(self):
        node = createRawEmpiricalDistributionNode('test-distr', [0, 3, 4], 'invalid-direction')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    # Color simple-type is tested with color distributions below

    #
    #   As more simple types are added to the parameters file, add more of these methods
    #

class TestsForNormalDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatMeanIsRequired(self):
        node = createCleanNormalDistributionNode()
        node.attrib.pop(NormalDistributionConstants.MEAN_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatMeanMustBeNumeric(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.MEAN_ATTR] = 'not numeric!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatStandardDeviationIsRequired(self):
        node = createCleanNormalDistributionNode()
        node.attrib.pop(NormalDistributionConstants.SD_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatStandardDeviationMustBeNumeric(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.SD_ATTR] = 'not numeric!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatStandardDeviationMustBeNonnegative(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.SD_ATTR] = '-1'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatStandardDeviationZeroIsOkay(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.SD_ATTR] = '0'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatReverseIsBoolean(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.REVERSE_ATTR] = 'truuuue'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatReverseIsBoolean2(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.REVERSE_ATTR] = 'true'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatReverseIsBoolean3(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.REVERSE_ATTR] = 'false'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        node = createCleanNormalDistributionNode()
        node.attrib.pop(NormalDistributionConstants.UUID_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValid(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.UUID_ATTR] = 'not a uuid!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatNameIsOptional(self):
        node = createCleanNormalDistributionNode()
        node.attrib.pop(NormalDistributionConstants.NAME_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatBothLimitsAreAllowed(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.MIN_VALUE_ATTR] = '-2'
        node.attrib[NormalDistributionConstants.MAX_VALUE_ATTR] = '2'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatLowerLimitOnlyIsAllowed(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.MIN_VALUE_ATTR] = '-2'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatUpperLimitOnlyIsAllowed(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.MAX_VALUE_ATTR] = '2'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatLowerLimitMustBeNumeric(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.MIN_VALUE_ATTR] = 'non-numeric'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatUpperLimitMustBeNumeric(self):
        node = createCleanNormalDistributionNode()
        node.attrib[NormalDistributionConstants.MAX_VALUE_ATTR] = 'non-numeric'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatElementCannotHaveSubelements(self):
        node = createCleanNormalDistributionNode()
        etree.SubElement(node, 'subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherAttributesAreOkay(self):
        node = createCleanNormalDistributionNode()
        node.attrib['a-new-attribute'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

class TestsForEmpiricalDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatDataCountCannotBeZero(self):
        node = createEmpiricalDistributionNode('an empirical distribution', [])
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatProbabilityMustNotBeNegative(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, -1, 4)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatProbabilityMustNotBeGreaterThanOne(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, 2, 4)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatProbabilityOfZeroIsOkay(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, 0, 4)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatProbabilityOfOneIsOkay(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, 1, 4)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatProbabilityOfOneHalfIsOkay(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, 0.5, 4)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatProbabilityIsRequired(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, value=4)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatProbabilityMustBeNumeric(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, 'probability', 4)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatValueIsRequired(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, probability = 0.5)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatValueMustBeNumeric(self):
        node = createCleanEmpiricalDistributionNode()
        addEmpiricalDataPoint(node, 0.5, 'value')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatNameIsOptional(self):
        node = createCleanEmpiricalDistributionNode()
        node.attrib.pop(EmpiricalDistributionConstants.NAME_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        node = createCleanEmpiricalDistributionNode()
        node.attrib.pop(EmpiricalDistributionConstants.UUID_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValid(self):
        node = createCleanEmpiricalDistributionNode()
        node.attrib[EmpiricalDistributionConstants.UUID_ATTR] = 'not a uuid!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOneThousandPointsAreOkay(self):
        points = [(i * 0.001, i) for i in range(1000)]
        node = createEmpiricalDistributionNode('an empirical distribution', points)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatOtherSubelementsAreBanned(self):
        node = createCleanEmpiricalDistributionNode()
        etree.SubElement(node, 'another-subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherAttributesAreOkay(self):
        node = createCleanEmpiricalDistributionNode()
        node.attrib['a-new-attribute'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())

    def testThatObservationSubElementsAreBanned(self):
        node = createCleanEmpiricalDistributionNode()
        observation = addEmpiricalDataPoint(node, 0.6, 5)
        etree.SubElement(observation, 'subelement')
        node.append(observation)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherObservationAttributesAreOkay(self):
        node = createCleanEmpiricalDistributionNode()
        observation = addEmpiricalDataPoint(node, 0.6, 5)
        observation.attrib['other-attribute'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
class TestsForBinnedDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()
    
    def append(self, node):
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)

    def testThatNameIsOptional(self):
        node = createCleanBinnedDistributionNode()
        node.attrib.pop(BinnedDistributionConstants.NAME_ATTR)
        self.append(node)
        self.assertTrue(self.doc.validate())

    def testThatUuidIsRequired(self):
        node = createCleanBinnedDistributionNode()
        node.attrib.pop(BinnedDistributionConstants.UUID_ATTR)
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatUuidIsValidated(self):
        node = createCleanBinnedDistributionNode()
        node.attrib[BinnedDistributionConstants.UUID_ATTR] = "not a uuid"
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatAggressionDirectionIsRequired(self):
        node = createCleanBinnedDistributionNode()
        node.attrib.pop(BinnedDistributionConstants.AGGRESSION_ATTR)
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherSubelementsAreBanned(self):
        node = createCleanBinnedDistributionNode()
        e = etree.Element('a-sub-element')
        node.append(e)
        self.append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherAttributesAreOkay(self):
        node = createCleanBinnedDistributionNode()
        node.attrib['a-new-attribute'] = 'attribute value'
        self.append(node)
        self.assertTrue(self.doc.validate())

    def testThatBinSubElementsAreBanned(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.append(etree.Element('a-sub-element'))
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatOtherBinAttributesAreOkay(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib['bin-name'] = 'aggressive folks'
        self.append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatMinValueIsRequired(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib.pop(BinnedDistributionConstants.BIN_MIN_VALUE_ATTR)
        self.append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatMinValueMustBeNumeric(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib[BinnedDistributionConstants.BIN_MIN_VALUE_ATTR] = 'not a number'
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatMaxValueIsRequired(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib.pop(BinnedDistributionConstants.BIN_MAX_VALUE_ATTR)
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatMaxValueMustBeNumeric(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib[BinnedDistributionConstants.BIN_MAX_VALUE_ATTR] = 'not a number'
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatCountIsRequired(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib.pop(BinnedDistributionConstants.BIN_COUNT_ATTR)
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatCountMustBeNumeric(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib[BinnedDistributionConstants.BIN_COUNT_ATTR] = 'not a number'
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatCountMustBeNonnegative(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib[BinnedDistributionConstants.BIN_COUNT_ATTR] = '-5'
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatCountMayBeZero(self):
        node = createCleanBinnedDistributionNode()
        firstBin = node[0]
        firstBin.attrib[BinnedDistributionConstants.BIN_COUNT_ATTR] = '0'
        self.append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatBinCountMayNotBeZero(self):
        node = createCleanBinnedDistributionNode()
        node[:] = []
        self.append(node)
        self.assertFalse(self.doc.validate())

    def testThatBinCountMayBeOne(self):
        node = createCleanBinnedDistributionNode()
        node[1:] = []
        self.append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatBinCountMayBeOneThousand(self):
        node = createCleanBinnedDistributionNode()
        node[:] = []
        for i in range(1000):
            addBinnedDistributionBin(node, i * 10, (i + 1) * 10, randint(0, 10))
        self.append(node)
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
                
    def createCleanDistributionNode(self):
        return createRawEmpiricalDistributionNode('a raw empirical distribution', self.values, 
                RawEmpiricalDistributionConstants.AGGRESSION_VALUE_POSITIVE)
    
    def testThatNameIsOptional(self):
        node = self.createCleanDistributionNode()
        node.attrib.pop(RawEmpiricalDistributionConstants.NAME_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        node = self.createCleanDistributionNode()
        node.attrib.pop(RawEmpiricalDistributionConstants.UUID_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())

    def testThatUuidIsValid(self):
        node = self.createCleanDistributionNode()
        node.attrib[RawEmpiricalDistributionConstants.UUID_ATTR] = 'not a uuid!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatAggressionDirectionIsRequired(self):
        node = self.createCleanDistributionNode()
        node.attrib.pop(RawEmpiricalDistributionConstants.AGGRESSION_ATTR)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherSubelementsAreBanned(self):
        node = self.createCleanDistributionNode()
        etree.SubElement(node, 'another-subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherAttributesAreOkay(self):
        node = self.createCleanDistributionNode()
        node.attrib['another-attribute'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatObservationSubElementsAreBanned(self):
        node = self.createCleanDistributionNode()
        dpNode = addRawEmpiricalDistributionObservation(node, 1234)
        etree.SubElement(dpNode, 'another-subelement')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherObservationAttributesAreOkay(self):
        node = self.createCleanDistributionNode()
        dpNode = addRawEmpiricalDistributionObservation(node, 1234)
        dpNode.attrib['another-attr'] = 'okay!'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatValueIsRequired(self):
        node = self.createCleanDistributionNode()
        dpNode = addRawEmpiricalDistributionObservation(node)
        dpNode.attrib['other-attr'] = 'blah'
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatValueMustBeNumeric(self):
        node = self.createCleanDistributionNode()
        addRawEmpiricalDistributionObservation(node, 'not numeric!')
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatDataCountCannotBeZero(self):
        node = createRawEmpiricalDistributionNode('an empty raw empirical distribution', [], 
                RawEmpiricalDistributionConstants.AGGRESSION_VALUE_POSITIVE)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertFalse(self.doc.validate())
    
    def testThatDataCountCanBeOne(self):
        node = createRawEmpiricalDistributionNode('a raw empirical distribution with one point', [5], 
                RawEmpiricalDistributionConstants.AGGRESSION_VALUE_POSITIVE)
        self.doc.getConnectorMaxPositioningDistancesNode().append(node)
        self.assertTrue(self.doc.validate())
    
    def testThatOneThousandsPointsAreOkay(self):
        points = [i * 0.25 for i in range(1000)]
        node = createRawEmpiricalDistributionNode('a raw empirical distribution with 1000 points', points, 
                RawEmpiricalDistributionConstants.AGGRESSION_VALUE_POSITIVE)
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
        self.cleanDistr.attrib.pop(EnumDistributionConstants.NAME_ATTR)
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        self.cleanDistr.attrib.pop(EnumDistributionConstants.UUID_ATTR)
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValid(self):
        self.cleanDistr.attrib[EnumDistributionConstants.UUID_ATTR] = 'not a uuid!'
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatShareMustBeNumeric(self):
        addEnumDistributionShare(self.cleanDistr, 'non numeric!', ConnectorLinkSelectionBehaviorDistributionConstants.BEST)
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())

    def testThatShareMustBeNonnegative(self):
        addEnumDistributionShare(self.cleanDistr, -0.25, ConnectorLinkSelectionBehaviorDistributionConstants.BEST)
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())

    def testThatShareMayBeZero(self):
        addEnumDistributionShare(self.cleanDistr, 0.00, ConnectorLinkSelectionBehaviorDistributionConstants.BEST)
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertTrue(self.doc.validate())

    def testThatInvalidValuesCannotBeUsed(self):
        addEnumDistributionShare(self.cleanDistr, 0.30, 'DOPIEST')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatShareSubelementsAreBanned(self):
        sub = addEnumDistributionShare(self.cleanDistr, 0.25, ConnectorLinkSelectionBehaviorDistributionConstants.BEST)
        etree.SubElement(sub, 'sub-element')
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertFalse(self.doc.validate())
    
    def testThatOtherShareAttributesAreOkay(self):
        sub = addEnumDistributionShare(self.cleanDistr, 0.25, ConnectorLinkSelectionBehaviorDistributionConstants.BEST)
        sub.attrib['another-element'] = 'ok!'
        self.doc.getConnectorLinkSelectionBehaviorsNode().append(self.cleanDistr)
        self.assertTrue(self.doc.validate())
    
    def testThatDistributionCountMayNotBeZero(self):
        self.doc.getConnectorLinkSelectionBehaviorsNode()[:] = []
        self.assertFalse(self.doc.validate())

class TestsForConnectorMaxPositioningDistance(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()

    def testThatNormalDistributionCanBeAdded(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        distr = createNormalDistributionNode('a normal distribution', 1, 2)
        node.append(distr)
        self.assertTrue(self.doc.validate())

    def testThatEmpiricalDistributionCanBeAdded(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        distr = createEmpiricalDistributionNode('an empirical distribution', [(0, 3), (0.15, 4), (0.85, 5), (1.0, 6)])
        node.append(distr)
        self.assertTrue(self.doc.validate())
    
    def testThatRawEmpiricalDistributionCanBeAdded(self):
        node = self.doc.getConnectorMaxPositioningDistancesNode()
        distr = createRawEmpiricalDistributionNode('a raw empirical distribution', [3, 4, 5, 6], 
                RawEmpiricalDistributionConstants.AGGRESSION_VALUE_POSITIVE)
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
    
    def testThatDistributionCountMayBeZero(self):
        self.doc.getConnectorMaxPositioningDistancesNode()[:] = []
        self.assertTrue(self.doc.validate())

class TestsForVehicleModelDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()
        self.cleanDistr = createVehicleModelsDistributionNode(
            self.doc.getVehicleModelsNode(), 
            [
                (35, '47e301a2-f905-4245-94ef-127daf6736b7'),
                (30, '9c344e0f-30cc-44e9-ba3b-b3c1b6137bda'),
                (20, '223367cb-69a6-474c-b55f-2405f0c1ba18')
            ]
        )

    def testThatOtherAttributesAreBannedOnDistributionsElement(self):
        self.doc.getVehicleModelsNode().attrib['another-attr'] = 'banned'
        self.assertFalse(self.doc.validate())
    
    def testThatOtherSubelementsAreBannedOnDistributionsElement(self):
        node = self.doc.getVehicleModelsNode()
        etree.SubElement(node, 'another-element')
        self.assertFalse(self.doc.validate())

    def testThatDistributionCountMayNotBeZero(self):
        node = self.doc.getVehicleModelsNode()
        elementsToRemove = []
        for element in node:
            elementsToRemove.append(element)
        
        for element in elementsToRemove:
            node.remove(element)
        
        self.assertFalse(self.doc.validate())

    def testThatDistributionCountMayBeOneThousand(self):
        node = self.doc.getVehicleModelsNode()
        for i in range(1000):
            createVehicleModelsDistributionNode(node, [
                (35, UUID()),
                (40, UUID()),
                (55, UUID())
            ], 'Vehicle Models ' + str(i))
        
        self.assertTrue(self.doc.validate())
    
    def testThatNameIsOptional(self):
        node = self.cleanDistr
        node.attrib.pop(VehicleModelDistributionConstants.NAME_ATTR)

        self.assertTrue(self.doc.validate())
    
    def testThatNameMayBeEmptyString(self):
        node = self.cleanDistr
        node.attrib[VehicleModelDistributionConstants.NAME_ATTR] = ''

        self.assertTrue(self.doc.validate())
    
    def testThatUuidIsRequired(self):
        self.cleanDistr.attrib.pop(VehicleModelDistributionConstants.UUID_ATTR)

        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValid(self):
        self.cleanDistr.attrib[VehicleModelDistributionConstants.UUID_ATTR] = 'not a valid uuid'

        self.assertFalse(self.doc.validate())
    
    def testThatOtherAttributesAreOkay(self):
        self.cleanDistr.attrib['another-attribute'] = 'another value'

        self.assertTrue(self.doc.validate())
    
    def testThatOtherSubelementsAreBanned(self):
        etree.SubElement(self.cleanDistr, 'another-element')

        self.assertFalse(self.doc.validate())
    
    def testThatZeroSharesIsNotOkay(self):
        createVehicleModelsDistributionNode(self.doc.getVehicleModelsNode(), [])
        self.assertFalse(self.doc.validate())

    def testThatOneThousandSharesIsOkay(self):
        tuples = [(10, UUID()) for _ in range(1000)]
        createVehicleModelsDistributionNode(self.doc.getVehicleModelsNode(), tuples)

        self.assertTrue(self.doc.validate())
    
    def testThatOccurenceCannotBeNegative(self):
        createVehicleModelsDistributionNode(self.doc.getVehicleModelsNode(), [(-3, UUID())])
        self.assertFalse(self.doc.validate())
    
    def testThatOccurenceCanBeZero(self):
        createVehicleModelsDistributionNode(self.doc.getVehicleModelsNode(), [(0, UUID())])
        self.assertTrue(self.doc.validate())
    
    def testThatOccurenceIsRequired(self):
        firstNode = self.cleanDistr[0]
        firstNode.attrib.pop(DistributionShareConstants.OCCURENCE_ATTR)

        self.assertFalse(self.doc.validate())
    
    def testThatOccurenceMayNotBeEmpty(self):
        firstNode = self.cleanDistr[0]
        firstNode.attrib[DistributionShareConstants.OCCURENCE_ATTR] = ''

        self.assertFalse(self.doc.validate())
    
    def testThatOccurenceMayNotBeString(self):
        firstNode = self.cleanDistr[0]
        firstNode.attrib[DistributionShareConstants.OCCURENCE_ATTR] = 'not a number'

        self.assertFalse(self.doc.validate())

    def testThatValueIsRequired(self):
        firstNode = self.cleanDistr[0]
        firstNode.attrib.pop(DistributionShareConstants.VALUE_ATTR)

        self.assertFalse(self.doc.validate())

    def testThatValueMayNotBeEmpty(self):
        firstNode = self.cleanDistr[0]
        firstNode.attrib[DistributionShareConstants.VALUE_ATTR] = ''

        self.assertFalse(self.doc.validate())
    
    def testThatValueMayNotBeArbitraryString(self):
        firstNode = self.cleanDistr[0]
        firstNode.attrib[DistributionShareConstants.VALUE_ATTR] = 'not a uuid'

        self.assertFalse(self.doc.validate())
    
    def testThatValueMayNotBeArbitraryNumber(self):
        firstNode = self.cleanDistr[0]
        firstNode.attrib[DistributionShareConstants.VALUE_ATTR] = '12345'

        self.assertFalse(self.doc.validate())
    
    def testThatMultipleSharesWithTheSameUuidAreAllowedInADistribution(self):
        tuples = []
        for i in range(5):
            uuid = tuples[0][1] if (i == 4) else UUID()
            tuples.append(((i + 1) * 10, uuid))
        
        createVehicleModelsDistributionNode(self.doc.getVehicleModelsNode(), tuples)
        self.assertTrue(self.doc.validate())

class TestsForColorDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()        
        self.targetNode = self.doc.getColorsNode()

    def testThatNameIsOptional(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        node.attrib.pop(ColorDistributionConstants.DISTRIBUTION_NAME_ATTR)
        self.assertTrue(self.doc.validate())

    def testThatUuidIsRequired(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        node.attrib.pop(ColorDistributionConstants.DISTRIBUTION_UUID_ATTR)
        self.assertFalse(self.doc.validate())
    
    def testThatUuidIsValidated(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        node.attrib[ColorDistributionConstants.DISTRIBUTION_UUID_ATTR] = 'an invalid uuid'
        self.assertFalse(self.doc.validate())

    def testThatOtherSubelementsAreBanned(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        etree.SubElement(node, 'a-child-node')
        self.assertFalse(self.doc.validate())

    def testThatOtherAttributesAreOkay(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        node.attrib['another-attribute'] = 'value'
        self.assertTrue(self.doc.validate())

    def testThatShareSubElementsAreBanned(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        firstShare = node[0]
        etree.SubElement(firstShare, 'a-child-node')
        self.assertFalse(self.doc.validate())
    
    def testThatOtherShareAttributesAreOkay(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        firstShare = node[0]
        firstShare.attrib['another-attribute'] = 'value'
        self.assertTrue(self.doc.validate())
    
    def testThatColorIsValidated(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        createAndAddColorShare(node, 20, 'an invalid color')
        self.assertFalse(self.doc.validate())
    
    def testThatLowerCaseColorsAreOkay(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        createAndAddColorShare(node, 20, '#abcdef')
        self.assertTrue(self.doc.validate())
    
    def testThatUpperCaseColorsAreOkay(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        createAndAddColorShare(node, 20, '#ABCDEF')
        self.assertTrue(self.doc.validate())
    
    def testThatShareCountCannotBeZero(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        node[:] = []
        self.assertFalse(self.doc.validate())

    def testThatShareCountMayBeOne(self):
        node = createAndAddCleanColorDistributionNode(self.targetNode)
        node[:] = []
        createAndAddColorShare(node, 30, "#000000")
        self.assertTrue(self.doc.validate())
    
    def testThatOneThousandSharesIsOkay(self):
        def createRandomShare():
            red = hex(randint(16, 255))[2:]
            green = hex(randint(16, 255))[2:]
            blue = hex(randint(16, 255))[2:]
            return [randint(0, 100), '#' + red + green + blue,]

        shares = [createRandomShare() for _ in range(0, 1000)]
        createAndAddColorDistributionNode(self.targetNode, shares) 
        self.assertTrue(self.doc.validate())
    
    def testThatShareOccurenceMustBeNonnegative(self):
        shares = [[-5, '#ffffff']]
        createAndAddColorDistributionNode(self.targetNode, shares) 
        self.assertFalse(self.doc.validate())

    def testThatShareOccurenceMayBeZero(self):
        shares = [[0, '#ffffff']]
        createAndAddColorDistributionNode(self.targetNode, shares) 
        self.assertTrue(self.doc.validate())
    
    def testThatShareOccurenceMustBeNumeric(self):
        shares = [['five', '#ffffff']]
        createAndAddColorDistributionNode(self.targetNode, shares) 
        self.assertFalse(self.doc.validate())
    
    def testThatShareOccurenceIsRequired(self):
        shares = [[5, '#ffffff']]
        node = createAndAddColorDistributionNode(self.targetNode, shares) 
        node[0].attrib.pop(ColorDistributionConstants.SHARE_OCCURENCE_ATTR)
        self.assertFalse(self.doc.validate())
    
    def testThatShareValueIsRequired(self):
        shares = [[5, '#ffffff']]
        node = createAndAddColorDistributionNode(self.targetNode, shares) 
        node[0].attrib.pop(ColorDistributionConstants.SHARE_VALUE_ATTR)
        self.assertFalse(self.doc.validate())
    
    def testThatDistributionCountMayNotBeZero(self):
        self.doc.getColorsNode()[:] = []
        self.assertFalse(self.doc.validate())

class SpeedUnits:
    METERS_PER_SECOND = 'meters-per-second'
    KILOMETERS_PER_HOUR = 'kilometers-per-hour'
    FEET_PER_SECOND = 'feet-per-second'
    MILES_PER_HOUR = 'miles-per-hour'

class AccelerationUnits:
    METERS_PER_SECOND_SQUARED = 'meters-per-second-squared'
    FEET_PER_SECOND_SQUARED = 'feet-per-second-squared'
    G = 'g'

class AccelerationDistributionConstants:
    DISTRIBUTION_TAG = 'distribution'
    DISTRIBUTION_TYPE = 'acceleration'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    SPEED_UNIT_ATTR = 'speed-unit'
    ACCELERATION_UNIT_ATTR = 'acceleration-unit'
    DATAPOINT_TAG = 'dp'
    DATAPOINT_VELOCITY_ATTR = 'velocity'
    DATAPOINT_MEAN_ATTR = 'mean'
    DATAPOINT_STDEV_ATTR = 'standard-deviation'

class TestsForAccelerationDistributions(unittest.TestCase):
    def setUp(self):
        self.doc = CleanDistributionsDocument()        
        self.target_node = self.doc.get_accelerations_node()

    def test_that_name_is_optional(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib.pop(AccelerationDistributionConstants.NAME_ATTR)
        self.assertTrue(self.doc.validate())

    def test_that_uuid_is_required(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib.pop(AccelerationDistributionConstants.UUID_ATTR)
        self.assertFalse(self.doc.validate())

    def test_that_uuid_must_be_a_uuid(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib[AccelerationDistributionConstants.UUID_ATTR] = 'not a uuid'
        self.assertFalse(self.doc.validate())
        node.attrib[AccelerationDistributionConstants.UUID_ATTR] = 'c3937207-d6db-481g-998e-e3abec44abb2' # there's a g in it
        self.assertFalse(self.doc.validate())

    def test_that_speed_unit_is_required(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib.pop(AccelerationDistributionConstants.SPEED_UNIT_ATTR)
        self.assertFalse(self.doc.validate())

    def test_that_speed_unit_values_work(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        choices: list = [
            SpeedUnits.FEET_PER_SECOND, SpeedUnits.KILOMETERS_PER_HOUR, 
            SpeedUnits.METERS_PER_SECOND, SpeedUnits.MILES_PER_HOUR
        ]
        for unit in choices:
            node.attrib[AccelerationDistributionConstants.SPEED_UNIT_ATTR] = unit
            self.assertTrue(self.doc.validate())

    def test_that_speed_unit_is_restricted(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib[AccelerationDistributionConstants.SPEED_UNIT_ATTR] = SpeedUnits.FEET_PER_SECOND + 's'
        self.assertFalse(self.doc.validate())
        node.attrib[AccelerationDistributionConstants.SPEED_UNIT_ATTR] = ''
        self.assertFalse(self.doc.validate())

    def test_that_accel_unit_is_required(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib.pop(AccelerationDistributionConstants.ACCELERATION_UNIT_ATTR)
        self.assertFalse(self.doc.validate())

    def test_that_accel_unit_values_work(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        choices: list = [
            AccelerationUnits.FEET_PER_SECOND_SQUARED,
            AccelerationUnits.G,
            AccelerationUnits.METERS_PER_SECOND_SQUARED
        ]
        for unit in choices:
            node.attrib[AccelerationDistributionConstants.ACCELERATION_UNIT_ATTR] = unit
            self.assertTrue(self.doc.validate())

    def test_that_accel_unit_is_restricted(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib[AccelerationDistributionConstants.ACCELERATION_UNIT_ATTR] = AccelerationUnits.G + 's'
        self.assertFalse(self.doc.validate())
        node.attrib[AccelerationDistributionConstants.ACCELERATION_UNIT_ATTR] = ''
        self.assertFalse(self.doc.validate())

    def test_that_other_attributes_are_ok(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        node.attrib['another-attribute'] = AccelerationUnits.G + 's'
        self.assertTrue(self.doc.validate())

    def test_that_zero_datapoints_fails(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        to_delete = node.findall(AccelerationDistributionConstants.DATAPOINT_TAG)
        for dp in to_delete:
            node.remove(dp)

        self.assertFalse(self.doc.validate())

    def test_that_one_datapoint_fails(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        to_delete = node.findall(AccelerationDistributionConstants.DATAPOINT_TAG)
        for dp in to_delete[1:]:
            node.remove(dp)

        self.assertFalse(self.doc.validate())

    def test_that_two_datapoints_is_ok(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        to_delete = node.findall(AccelerationDistributionConstants.DATAPOINT_TAG)
        for dp in to_delete[2:]:
            node.remove(dp)

        self.assertTrue(self.doc.validate())

    def test_that_100_datapoints_is_ok(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        for number in range(3, 100):
            create_and_add_acceleration_distribution_point(node, number, number / 10., number / 100.)

        self.assertTrue(self.doc.validate())

    def test_that_dp_velocity_is_required(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        dp: etree.Element = node.find(AccelerationDistributionConstants.DATAPOINT_TAG)
        dp.attrib.pop(AccelerationDistributionConstants.DATAPOINT_VELOCITY_ATTR)
        self.assertFalse(self.doc.validate())

    def test_that_dp_velocity_must_be_nonnegative(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        dp: etree.Element = node.find(AccelerationDistributionConstants.DATAPOINT_TAG)
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_VELOCITY_ATTR] = '-5'
        self.assertFalse(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_VELOCITY_ATTR] = ''
        self.assertFalse(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_VELOCITY_ATTR] = 'not a number'
        self.assertFalse(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_VELOCITY_ATTR] = '0'
        self.assertTrue(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_VELOCITY_ATTR] = '5'
        self.assertTrue(self.doc.validate())

    def test_that_dp_mean_is_required(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        dp: etree.Element = node.find(AccelerationDistributionConstants.DATAPOINT_TAG)
        dp.attrib.pop(AccelerationDistributionConstants.DATAPOINT_MEAN_ATTR)
        self.assertFalse(self.doc.validate())

    def test_that_dp_mean_must_be_numeric(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        dp: etree.Element = node.find(AccelerationDistributionConstants.DATAPOINT_TAG)
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_MEAN_ATTR] = '-5'
        self.assertTrue(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_MEAN_ATTR] = '0'
        self.assertTrue(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_MEAN_ATTR] = '5'
        self.assertTrue(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_MEAN_ATTR] = ''
        self.assertFalse(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_MEAN_ATTR] = 'not a number'
        self.assertFalse(self.doc.validate())

    def test_that_dp_stdev_is_required(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        dp: etree.Element = node.find(AccelerationDistributionConstants.DATAPOINT_TAG)
        dp.attrib.pop(AccelerationDistributionConstants.DATAPOINT_STDEV_ATTR)
        self.assertFalse(self.doc.validate())

    def test_that_dp_stdev_must_be_nonnegative(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        dp: etree.Element = node.find(AccelerationDistributionConstants.DATAPOINT_TAG)
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_STDEV_ATTR] = '-5'
        self.assertFalse(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_STDEV_ATTR] = ''
        self.assertFalse(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_STDEV_ATTR] = 'not a number'
        self.assertFalse(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_STDEV_ATTR] = '0'
        self.assertTrue(self.doc.validate())
        dp.attrib[AccelerationDistributionConstants.DATAPOINT_STDEV_ATTR] = '5'
        self.assertTrue(self.doc.validate())

    def test_that_dp_other_attributes_are_ok(self):
        node: etree.Element = create_and_add_clean_accel_distribution_node(self.target_node)
        dp: etree.Element = node.find(AccelerationDistributionConstants.DATAPOINT_TAG)
        dp.attrib['another-attribute'] = '-5'
        self.assertTrue(self.doc.validate())

if (__name__ == '__main__'):
    unittest.main()
