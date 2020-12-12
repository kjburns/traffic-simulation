from lxml import etree
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, final, List, Callable, Tuple
from i18n_l10n.temporary_i18n_bridge import Localization
from functools import reduce
from simulator.xml_validation import XmlValidation
from i18n_l10n.temporary_i18n_bridge import Localization


class DistributionXmlNames:
    ROOT_TAG = 'distributions'

    class DistributionSets:
        TAG = 'distribution-set'
        TYPE_ATTR = 'type'

    class Shares:
        SHARE_TAG = 'share'
        SHARE_OCCURRENCE_ATTR = 'occurrence'
        SHARE_VALUE_ATTR = 'value'

    class EnumShares(Shares):
        pass

    class GenericNames:
        NAME_ATTR = 'name'
        UUID_ATTR = 'uuid'
        TAG = 'distribution'

    class VehicleModels(GenericNames, Shares):
        TYPE = 'vehicle-models'

    class Colors(GenericNames, Shares):
        TYPE = 'colors'

    class ConnectorLinkSelectionBehaviors(GenericNames):
        TYPE = 'connector-link-selection-behaviors'
        NEAREST = 'NEAREST'
        FARTHEST = 'FARTHEST'
        BEST = 'BEST'
        RANDOM = 'RANDOM'

    class NormalDistributions:
        TAG = 'normal-distribution'
        MEAN_ATTR = 'mean'
        SD_ATTR = 'standard-deviation'
        MIN_VALUE_ATTR = 'min-value'
        MAX_VALUE_ATTR = 'max-value'
        REVERSE_ATTR = 'reverse'

    class EmpiricalDistributions:
        TAG = 'empirical-distribution'
        DATA_POINT_TAG = 'dp'
        DATA_POINT_PROBABILITY_ATTR = 'prob'
        DATA_POINT_VALUE_ATTR = 'val'

    class RawEmpiricalDistributions:
        TAG = 'raw-empirical-distribution'
        AGGRESSION_ATTR = 'aggression'
        AGGRESSION_VALUE_POSITIVE = 'positive'
        AGGRESSION_VALUE_NEGATIVE = 'negative'
        DATA_POINT_TAG = 'dp'
        DATA_POINT_VALUE_ATTR = 'value'

    class BinnedDistributions:
        TAG = 'binned-distribution'
        AGGRESSION_ATTR = 'aggression'
        AGGRESSION_VALUE_POSITIVE = 'positive'
        AGGRESSION_VALUE_NEGATIVE = 'negative'
        AGGRESSION_VALUE_NONE = 'none'
        BIN_TAG = 'bin'
        BIN_MIN_VALUE_ATTR = 'min-value'
        BIN_MAX_VALUE_ATTR = 'max-value'
        BIN_COUNT_ATTR = 'count'

    class _DistributionsWithUnits(GenericNames):
        UNITS_ATTR = 'units'

    class DistanceDistributions(_DistributionsWithUnits):
        pass

    class SpeedDistributions(_DistributionsWithUnits):
        pass

    class AccelerationDistributions(_DistributionsWithUnits):
        pass

    class ConnectorMaximumPositioningDistances(DistanceDistributions):
        TYPE: str = 'connector-max-positioning-distance'

    class AccelerationFunctions(GenericNames):
        TYPE = 'acceleration'
        SPEED_UNIT_ATTR = 'speed-unit'
        ACCELERATION_UNIT_ATTR = 'acceleration-unit'
        DP_TAG = 'dp'
        DP_VELOCITY_ATTR = 'velocity'
        DP_MEAN_ATTR = 'mean'
        DP_STANDARD_DEVIATION_ATTR = 'standard-deviation'

    class DecelerationDistributions(AccelerationDistributions):
        TYPE = 'max-deceleration'

    class FractionalDistributions(GenericNames):
        pass

    class DesiredAccelerationDistributions(FractionalDistributions):
        TYPE = 'desired-deceleration-fractions'

    class DesiredDecelerationDistributions(FractionalDistributions):
        TYPE = 'desired-deceleration-fractions'

    class TargetSpeedDistributions(SpeedDistributions):
        TYPE = 'speed-distributions'

    class PostedSpeedDeviationDistributions(SpeedDistributions):
        TYPE = 'posted-speed-deviations'


T = TypeVar('T')


class Distribution(ABC, Generic[T]):
    @final
    def check_parameter(self, parameter: float) -> None:
        if parameter < 0 or parameter > 1:
            raise ValueError(Localization.get_message('E0004', str(parameter)))

    @abstractmethod
    def get_value(self, parameter: float) -> T:
        pass

    @abstractmethod
    def __init__(self, node: etree.ElementBase):
        self._name: str = node.attrib[DistributionXmlNames.GenericNames.NAME_ATTR]
        self._uuid: str = node.attrib[DistributionXmlNames.GenericNames.UUID_ATTR]

    @final
    @property
    def name(self) -> str:
        return self._name

    @final
    @property
    def uuid(self) -> str:
        return self._uuid


class DistributionSet(Generic[T]):
    def __init__(self,
                 collection_node: etree.ElementBase,
                 node_handler: Callable[[etree.ElementBase], Distribution[T]]):
        self._distributions: Dict[str, Distribution[T]] = dict()
        for child_node in collection_node.iterchildren():
            distribution: Distribution[T] = node_handler(child_node)
            self.add_distribution(distribution)

    @final
    def __getitem__(self, key: str):
        return self._distributions[key]

    @final
    def clear(self):
        self._distributions.clear()

    @final
    def add_distribution(self, distribution: Distribution[T]) -> None:
        self._distributions[distribution.uuid] = distribution


class StringDistribution(Distribution[str], ABC):
    class ShareCollection:
        class ShareViewer(ABC):
            @property
            @abstractmethod
            def value(self) -> str:
                pass

            @property
            @abstractmethod
            def occurrence(self) -> float:
                pass

        class ShareViewerImpl(ShareViewer):
            def __init__(self, other):
                self._value: str = other.value
                self._occurrence: float = other.occurrence

            @property
            def value(self) -> str:
                return self._value

            @property
            def occurrence(self) -> float:
                return self._occurrence

        class Share(ShareViewer):
            def __init__(self, value: str, amount: float):
                self._value = value
                self._amount = amount

            @property
            def value(self) -> str:
                return self._value

            @property
            def occurrence(self) -> float:
                return self._amount

            @occurrence.setter
            def occurrence(self, new_value: float) -> None:
                self._amount = new_value

        def __init__(self, allowable_values_getter: Callable[[], List[str]]):
            self._data: List[StringDistribution.ShareCollection.Share] = list()
            for value in allowable_values_getter():
                share: StringDistribution.ShareCollection.Share = StringDistribution.ShareCollection.Share(value, 0.0)
                self._data.append(share)

        def add_share(self, share_value: str, share_amount: float, *, distribution_name: str = 'String Distribution'):
            add_to_element_candidates = list(filter(lambda x: x.value == share_value, self._data))
            if len(add_to_element_candidates) == 0:
                # Illegal Value (not in acceptable list)
                raise ValueError(Localization.get_message('E0005', distribution_name, share_value))

            add_to_element_candidates[0].occurrence += share_amount

        def get_all_shares(self) -> List[ShareViewer]:
            return [StringDistribution.ShareCollection.ShareViewerImpl(share) for share in self._data]

    def __init__(self, node: etree.ElementBase, allowable_values_getter: Callable[[], List[str]]):
        super(StringDistribution, self).__init__(node)
        self._data: StringDistribution.ShareCollection = StringDistribution.ShareCollection(allowable_values_getter)

        for element in node.iterfind(DistributionXmlNames.EnumShares.SHARE_TAG):
            occurrence: float = float(element.attrib[DistributionXmlNames.EnumShares.SHARE_OCCURRENCE_ATTR])
            value: str = element.attrib[DistributionXmlNames.EnumShares.SHARE_VALUE_ATTR]
            self._data.add_share(value, occurrence, distribution_name=self.get_distribution_type_name())

        # Check that the total of shares is not zero
        shares_total: float = sum(map(lambda item: item.occurrence, self._data.get_all_shares()))
        if shares_total == 0.0:
            raise ValueError(Localization.get_message('E0006', self.name))

        def accumulator(so_far: List[Tuple[float, float, str]],
                        this_one: StringDistribution.ShareCollection.ShareViewer
                        ) -> List[Tuple[float, float, str]]:
            total_so_far: float = so_far[-1][1] if len(so_far) > 0 else 0.0
            so_far.append((total_so_far, total_so_far + this_one.occurrence, this_one.value))

            return so_far

        self._start_end_value_tuples: List[Tuple[float, float, str]] = reduce(
            accumulator, self.get_share_collection().get_all_shares(), []
        )

    def get_value(self, parameter: float) -> str:
        # check parameter
        self.check_parameter(parameter)

        # scale parameter to range of shares
        scale: float = self._start_end_value_tuples[-1][1]
        scaled_parameter: float = parameter * scale

        # The parameter x is in the range [a, b] if (a - x)(b - x) <= 0.
        # Given that the probability of a random continuous variable
        #  being equal to any particular value is zero, we can say that
        #  being in the range [a, b] is the same as [a, b), which is what
        #  we actually want (since the parameter should never equal one).
        # Given this, we will use the filter operation to make quick work,
        #  and if more than one range is returned, we will just pick the
        #  first one.
        value: str = list(filter(
            lambda share_tuple: (scaled_parameter - share_tuple[0]) * (scaled_parameter - share_tuple[1]) < 0,
            self._start_end_value_tuples
        ))[0][2]

        return value

    @classmethod
    @abstractmethod
    def get_allowable_values(cls) -> List[str]:
        pass

    @final
    def get_share_collection(self) -> ShareCollection:
        return self._data

    @classmethod
    @abstractmethod
    def get_distribution_type_name(cls) -> str: pass


class ConnectorLinkSelectionBehaviorDistribution(StringDistribution):
    @classmethod
    def get_allowable_values(cls) -> List[str]:
        return [
            DistributionXmlNames.ConnectorLinkSelectionBehaviors.NEAREST,
            DistributionXmlNames.ConnectorLinkSelectionBehaviors.FARTHEST,
            DistributionXmlNames.ConnectorLinkSelectionBehaviors.BEST,
            DistributionXmlNames.ConnectorLinkSelectionBehaviors.RANDOM
        ]

    def __init__(self, node: etree.ElementBase):
        super().__init__(node, ConnectorLinkSelectionBehaviorDistribution.get_allowable_values)

    @classmethod
    def get_distribution_type_name(cls) -> str:
        return 'Connector_Link_Selection_Behavior'


class Distributions:
    _doc_root: etree.ElementBase = None
    _connector_link_selection_behaviors: DistributionSet[ConnectorLinkSelectionBehaviorDistribution] = None

    @classmethod
    def reset(cls):
        # just for testing
        cls._connector_link_selection_behaviors.clear()
        # TODO add more here as collections are added

    @classmethod
    def connector_link_selection_behaviors(cls):
        return cls._connector_link_selection_behaviors

    @classmethod
    def process_file(cls, filename: str) -> None:
        def get_distribution_set_node(distribution_set_name: str) -> etree.ElementBase:
            print(etree.tostring(_doc_root))
            candidates: List[etree.ElementBase] = list(filter(
                lambda e: e.attrib[DistributionXmlNames.DistributionSets.TYPE_ATTR] == distribution_set_name,
                _doc_root))
            return candidates[0] if len(candidates) != 0 else None

        _doc_root = etree.parse(filename).getroot()
        schema: etree.XMLSchema = etree.XMLSchema(etree.parse(XmlValidation.DISTRIBUTIONS_XSD))
        if not schema.validate(_doc_root):
            raise RuntimeError('E0002', filename)

        cls._connector_link_selection_behaviors = DistributionSet(
            get_distribution_set_node(DistributionXmlNames.ConnectorLinkSelectionBehaviors.TYPE),
            ConnectorLinkSelectionBehaviorDistribution)
