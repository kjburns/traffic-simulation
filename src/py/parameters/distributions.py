from abc import ABC, abstractmethod
from functools import reduce
from typing import Generic, TypeVar, Dict, final, List, Callable, Tuple, Iterable
from scipy import stats

from lxml import etree

from i18n_l10n.temporary_i18n_bridge import Localization
from simulator.xml_validation import XmlValidation
from simulator.simulator_logger import SimulatorLoggerWrapper as Logger
from parameters.units import Unit, DistanceUnits
from parameters.vehicle_models import VehicleModelCollection, VehicleModel


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
        TYPE = 'desired-acceleration-fractions'

    class DesiredDecelerationDistributions(FractionalDistributions):
        TYPE = 'desired-deceleration-fractions'

    class TargetSpeedDistributions(SpeedDistributions):
        TYPE = 'speed-distributions'

    class PostedSpeedDeviationDistributions(SpeedDistributions):
        TYPE = 'posted-speed-deviations'

    class PoissonDistributions:
        POISSON_TAG = 'poisson-distribution'
        ZERO_TRUNCATED_TAG = 'positive-poisson-distribution'
        LAMBDA_ATTR = 'lambda'

    class NonTransitOccupancyDistributions(GenericNames):
        TYPE = 'non-transit-occupancy'

    class TransitPassengerDistributions(GenericNames):
        TYPE = 'transit-passengers'


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
        self._name: str = node.attrib[DistributionXmlNames.GenericNames.NAME_ATTR] \
            if DistributionXmlNames.GenericNames.NAME_ATTR in node.attrib \
            else ''
        self._uuid: str = node.attrib[DistributionXmlNames.GenericNames.UUID_ATTR] \
            if DistributionXmlNames.GenericNames.UUID_ATTR in node.attrib \
            else ''

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
            return list(sorted(
                [StringDistribution.ShareCollection.ShareViewerImpl(share) for share in self._data],
                key=lambda share: share.value
            ))

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
            lambda share_tuple: (scaled_parameter - share_tuple[0]) * (scaled_parameter - share_tuple[1]) <= 0,
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


class VehicleModelDistribution(StringDistribution):
    def __init__(self, node: etree.ElementBase):
        super().__init__(node, VehicleModelDistribution.get_allowable_values)

    @classmethod
    def get_allowable_values(cls) -> List[str]:
        return VehicleModelCollection.keys()

    @classmethod
    def get_distribution_type_name(cls) -> str:
        return 'vehicle-models'


class ColorDistribution(Distribution[str]):
    def __init__(self, node: etree.ElementBase):
        super().__init__(node)

        def reducer(so_far: List[Tuple[float, float, str]], current: etree.ElementBase) -> List[Tuple[float, float, str]]:
            total_so_far: float = so_far[-1][1] if len(so_far) > 0 else 0.0
            so_far.append((
                total_so_far,
                total_so_far + float(current.attrib[DistributionXmlNames.Shares.SHARE_OCCURRENCE_ATTR]),
                current.attrib[DistributionXmlNames.Shares.SHARE_VALUE_ATTR],
            ))
            return so_far

        empty_list: List[Tuple[float, float, str]] = []
        colors_in_file_order: Iterable[etree.ElementBase] = node.iterfind(DistributionXmlNames.Shares.SHARE_TAG)
        colors_sorted: Iterable[etree.ElementBase] = sorted(
            colors_in_file_order,
            key=lambda share_node: share_node.attrib[DistributionXmlNames.Shares.SHARE_VALUE_ATTR]
        )

        self._ranges: List[Tuple[float, float, str]] = reduce(
            reducer,
            colors_sorted,
            empty_list,
        )

        if self._ranges[-1][1] == 0.0:
            raise ValueError(Localization.get_message('E0006', self.uuid))

        self._ranges = list(sorted(self._ranges, key=lambda rng: rng[2]))

    def get_value(self, parameter: float) -> str:
        self.check_parameter(parameter)

        weighted_parameter: float = parameter * self._ranges[-1][1]
        first_matching_value: str = list(filter(
            lambda value_range: (value_range[0] - weighted_parameter) * (value_range[1] - weighted_parameter) <= 0,
            self._ranges
        ))[0][2]

        return first_matching_value


class RealNumberDistribution(Distribution[float], ABC):
    pass


class NormalDistribution(RealNumberDistribution):
    def get_value(self, parameter: float) -> float:
        value_candidate: float = self._distribution.ppf(
            1 - parameter if self._reverse else parameter
        )

        if self._min_value is not None:
            value_candidate = max(value_candidate, self._min_value)

        if self._max_value is not None:
            value_candidate = min(value_candidate, self._max_value)

        return value_candidate

    def __init__(self, node: etree.ElementBase, *, guid: str = None):
        def check_extreme_values():
            if self._min_value is not None and self._max_value is not None:
                if self._min_value > self._max_value:
                    raise ValueError(Localization.get_message('E0007', guid if guid is not None else '<unknown uuid>'))

                if self._distribution.cdf(self._max_value) - self._distribution.cdf(self._min_value) < 0.50:
                    Logger.logger().warning(
                        msg=Localization.get_message('W0003', str(self._mean), str(self._sd))
                    )
                    return

            if self._min_value is not None and self._max_value is None:
                if self._distribution.cdf(self._min_value) > 0.25:
                    Logger.logger().warning(
                        msg=Localization.get_message('W0002', str(self._mean), str(self._sd))
                    )
                    return

            if self._min_value is None and self._max_value is not None:
                if self._distribution.cdf(self._max_value) < 0.75:
                    Logger.logger().warning(
                        msg=Localization.get_message('W0002', str(self._mean), str(self._sd))
                    )
                    return

            Logger.logger().debug(msg='Truncated normal distribution extreme value check passes.')

        super().__init__(node)
        self._mean: float = float(node.attrib[DistributionXmlNames.NormalDistributions.MEAN_ATTR])
        self._sd: float = float(node.attrib[DistributionXmlNames.NormalDistributions.SD_ATTR])
        self._reverse: bool = bool(node.attrib[DistributionXmlNames.NormalDistributions.REVERSE_ATTR]) \
            if DistributionXmlNames.NormalDistributions.REVERSE_ATTR in node.attrib \
            else False
        self._min_value: float = float(node.attrib[DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR]) \
            if DistributionXmlNames.NormalDistributions.MIN_VALUE_ATTR in node.attrib \
            else None
        self._max_value: float = float(node.attrib[DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR]) \
            if DistributionXmlNames.NormalDistributions.MAX_VALUE_ATTR in node.attrib \
            else None

        self._distribution: stats.norm_gen = stats.norm(self._mean, self._sd)

        check_extreme_values()


class EmpiricalDistribution(RealNumberDistribution):
    def get_value(self, parameter: float) -> T:
        pass

    def __init__(self, node: etree.ElementBase):
        super().__init__(node)


class RawEmpiricalDistribution(RealNumberDistribution):
    def __init__(self, node: etree.ElementBase):
        super().__init__(node)

    def get_value(self, parameter: float) -> T:
        pass


class BinnedDistribution(RealNumberDistribution):
    def get_value(self, parameter: float) -> T:
        pass

    def __init__(self, node: etree.ElementBase):
        super().__init__(node)


class RealNumberDistributionFactory:
    @staticmethod
    def from_xml(xml: etree.ElementBase, *, guid: str = None) -> RealNumberDistribution:
        if xml.tag == DistributionXmlNames.NormalDistributions.TAG:
            return NormalDistribution(xml, guid=guid)
        elif xml.tag == DistributionXmlNames.EmpiricalDistributions.TAG:
            return EmpiricalDistribution(xml)
        elif xml.tag == DistributionXmlNames.RawEmpiricalDistributions.TAG:
            return RawEmpiricalDistribution(xml)
        elif xml.tag == DistributionXmlNames.BinnedDistributions.TAG:
            return BinnedDistribution(xml)
        pass


class DistanceDistribution(Distribution[float]):
    def __init__(self, xml: etree.ElementBase, guid: str = None):
        super().__init__(xml)
        self._units: Unit = DistanceUnits.DICTIONARY[
            xml.attrib[DistributionXmlNames.ConnectorMaximumPositioningDistances.UNITS_ATTR]
        ]
        self._distribution: RealNumberDistribution = RealNumberDistributionFactory.from_xml(xml[0], guid=guid)

    def get_value(self, parameter: float) -> T:
        return self._units.convert_to_base_units(self._distribution.get_value(parameter))

    @property
    def units(self) -> Unit:
        return self._units


class Distributions:
    _doc_root: etree.ElementBase = None
    _connector_link_selection_behaviors: DistributionSet[ConnectorLinkSelectionBehaviorDistribution] = None
    _connector_max_positioning_distances: DistributionSet[DistanceDistribution] = None
    _vehicle_models: DistributionSet[VehicleModel] = None
    _colors: DistributionSet[str] = None

    @classmethod
    def reset(cls):
        # just for testing
        if cls._connector_link_selection_behaviors is not None:
            cls._connector_link_selection_behaviors.clear()
        if cls._connector_max_positioning_distances is not None:
            cls._connector_max_positioning_distances.clear()
        if cls._vehicle_models is not None:
            cls._vehicle_models.clear()
        if cls._colors is not None:
            cls._colors.clear()
        # TODO add more here as collections are added

    @classmethod
    def connector_link_selection_behaviors(cls) -> DistributionSet[ConnectorLinkSelectionBehaviorDistribution]:
        return cls._connector_link_selection_behaviors

    @classmethod
    def connector_max_positioning_distances(cls) -> DistributionSet[DistanceDistribution]:
        return cls._connector_max_positioning_distances

    @classmethod
    def vehicle_models(cls) -> DistributionSet[VehicleModel]:
        return cls._vehicle_models

    @classmethod
    def colors(cls) -> DistributionSet[str]:
        return cls._colors

    @classmethod
    def read_from_xml(cls, root_node: etree.ElementBase, *, filename: str = 'file unknown') -> None:
        def get_distribution_set_node(distribution_set_name: str) -> etree.ElementBase:
            candidates: List[etree.ElementBase] = list(filter(
                lambda e: e.attrib[DistributionXmlNames.DistributionSets.TYPE_ATTR] == distribution_set_name,
                root_node))
            return candidates[0] if len(candidates) != 0 else None

        schema: etree.XMLSchema = etree.XMLSchema(etree.parse(XmlValidation.DISTRIBUTIONS_XSD))
        if not schema.validate(root_node):
            raise RuntimeError('E0002', filename)

        cls._connector_link_selection_behaviors = DistributionSet(
            get_distribution_set_node(DistributionXmlNames.ConnectorLinkSelectionBehaviors.TYPE),
            ConnectorLinkSelectionBehaviorDistribution
        )

        cls._connector_max_positioning_distances = DistributionSet(
            get_distribution_set_node(DistributionXmlNames.ConnectorMaximumPositioningDistances.TYPE),
            DistanceDistribution
        )

        cls._vehicle_models = DistributionSet(
            get_distribution_set_node(DistributionXmlNames.VehicleModels.TYPE),
            VehicleModelDistribution
        )

        cls._colors = DistributionSet(
            get_distribution_set_node(DistributionXmlNames.Colors.TYPE),
            ColorDistribution
        )

    @classmethod
    def process_file(cls, filename: str) -> None:
        _doc_root = etree.parse(filename).getroot()
        cls.read_from_xml(_doc_root, filename=filename)
