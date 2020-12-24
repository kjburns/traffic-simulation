from abc import ABC, abstractmethod
from functools import reduce
from typing import Generic, TypeVar, Dict, final, List, Callable, Tuple, Iterable, Union
from scipy import stats

from lxml import etree
from lxml.etree import ElementBase

from i18n_l10n.temporary_i18n_bridge import Localization
from simulator.xml_validation import XmlValidation
from simulator.simulator_logger import SimulatorLoggerWrapper as Logger
from parameters.units import Unit, DistanceUnits, SpeedUnits, AccelerationUnits
from parameters.vehicle_models import VehicleModelCollection


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


class HasUuid(Generic[T]):
    def __init__(self, node: etree.ElementBase):
        self._uuid: str = node.attrib[DistributionXmlNames.GenericNames.UUID_ATTR] \
            if node is not None and DistributionXmlNames.GenericNames.UUID_ATTR in node.attrib \
            else ''

    @final
    @property
    def uuid(self) -> str:
        return self._uuid


class Distribution(ABC, HasUuid, Generic[T]):
    @final
    def check_parameter(self, parameter: float) -> None:
        if parameter < 0 or parameter > 1:
            raise ValueError(Localization.get_message('E0004', str(parameter)))

    @abstractmethod
    def get_value(self, parameter: float) -> T:
        pass

    @abstractmethod
    def get_parameter(self, value: T) -> Union[None, float]:
        """
        Gets a parameter that, when supplied to get_value as the parameter, would return 'value'.
        Args:
            value: the value whose parameter is being sought

        Returns:
            If the value exists within the distribution, returns:
                * a parameter that would provide that value if value is numeric.
                * the parameter in the middle of a bin if value is not numeric.
        """
        pass

    @abstractmethod
    def __init__(self, node: Union[etree.ElementBase, None]):
        super().__init__(node)
        self._name: str = node.attrib[DistributionXmlNames.GenericNames.NAME_ATTR] \
            if node is not None and DistributionXmlNames.GenericNames.NAME_ATTR in node.attrib \
            else ''

    @final
    @property
    def name(self) -> str:
        return self._name


class DistributionSet(Generic[T]):
    def __init__(self,
                 collection_node: etree.ElementBase,
                 node_handler: Callable[[etree.ElementBase], HasUuid]):
        self._distributions: Dict[str, HasUuid] = dict()
        for child_node in collection_node.iterchildren():
            distribution: HasUuid = node_handler(child_node)
            self.add_distribution(distribution)

    @final
    def __getitem__(self, key: str) -> T:
        return self._distributions[key]

    @final
    def clear(self):
        self._distributions.clear()

    @final
    def add_distribution(self, distribution: HasUuid) -> None:
        self._distributions[distribution.uuid] = distribution


class StringDistribution(Distribution[str], ABC):
    @final
    def get_parameter(self, value: T) -> Union[None, float]: pass

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
    def get_parameter(self, value: T) -> Union[None, float]:
        pass

    def __init__(self, node: etree.ElementBase):
        super().__init__(node)

        def reducer(so_far: List[Tuple[float, float, str]], current: etree.ElementBase) -> \
                List[Tuple[float, float, str]]:
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
    def get_parameter(self, value: float) -> Union[None, float]:
        if self._min_value is not None:
            if value < self._min_value:
                return None
            elif value == self._min_value:
                return 0.0

        if self._max_value is not None:
            if value > self._max_value:
                return None
            elif value == self._max_value:
                # Nothing Special to do here, will be handled below.
                pass

        return float(self._distribution.cdf(value))

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
    def get_parameter(self, value: float) -> Union[None, float]:
        maximum_value: float = max(map(lambda bin_info: max(bin_info[2:]), self._bins))
        minimum_value: float = min(map(lambda bin_info: min(bin_info[2:]), self._bins))

        if value < minimum_value or value > maximum_value:
            return None

        # the distribution is a locus of data points whose maximum value is 'maximum_value' and
        # whose minimum value is 'minimum_value'. Because 'value' has been established to be between
        # these extrema at this point, there must be at least one bin containing 'value'.
        # We will use the first such bin found. If the distribution is monotonic, there will be only
        # one such bin.

        bin_containing_value: Tuple[float, float, float, float] = list(filter(
            lambda bin_info: (bin_info[2] - value) * (bin_info[3] - value) <= 0,
            self._bins
        ))[0]
        bin_parameter: float = (value - bin_containing_value[2]) / \
                               (bin_containing_value[3] - bin_containing_value[2])
        return bin_containing_value[0] + bin_parameter * (bin_containing_value[1] - bin_containing_value[0])

    def get_value(self, parameter: float) -> float:
        self.check_parameter(parameter)

        bin_containing_parameter: Tuple[float, float, float, float] = list(filter(
            lambda b: (b[0] - parameter) * (b[1] - parameter) <= 0,
            self._bins
        ))[0]
        bin_parameter: float = (parameter - bin_containing_parameter[0]) / \
                               (bin_containing_parameter[1] - bin_containing_parameter[0])
        return bin_containing_parameter[2] + bin_parameter * (bin_containing_parameter[3] - bin_containing_parameter[2])

    @staticmethod
    def from_xml(node: etree.ElementBase) -> RealNumberDistribution:
        tuples: List[Tuple[float, float]] = [
            (float(dp_node.attrib[DistributionXmlNames.EmpiricalDistributions.DATA_POINT_PROBABILITY_ATTR]),
             float(dp_node.attrib[DistributionXmlNames.EmpiricalDistributions.DATA_POINT_VALUE_ATTR]))
            for dp_node in node.iterfind(DistributionXmlNames.EmpiricalDistributions.DATA_POINT_TAG)
        ]

        return EmpiricalDistribution(tuples)

    def __init__(self, tuples: List[Tuple[float, float]]):
        super().__init__(None)
        sorted_tuples: List[Tuple[float, float]] = list(sorted(tuples, key=lambda tup: tup[0]))
        self._bins: List[Tuple[float, float, float, float]] = [
            (
                sorted_tuples[left_dp_index][0],
                sorted_tuples[left_dp_index + 1][0],
                sorted_tuples[left_dp_index][1],
                sorted_tuples[left_dp_index + 1][1],
            )
            for left_dp_index in range(len(sorted_tuples) - 1)
        ]


class RawEmpiricalDistribution(RealNumberDistribution):
    def get_parameter(self, value: T) -> Union[None, float]:
        pass

    def __init__(self, node: etree.ElementBase):
        super().__init__(node)

    def get_value(self, parameter: float) -> T:
        pass


class BinnedDistribution(RealNumberDistribution):
    def get_value(self, parameter: float) -> T:
        pass

    def __init__(self, node: etree.ElementBase):
        super().__init__(node)

    def get_parameter(self, value: T) -> Union[None, float]:
        pass


class RealNumberDistributionFactory:
    @staticmethod
    def from_xml(xml: etree.ElementBase, *, guid: str = None) -> RealNumberDistribution:
        if xml.tag == DistributionXmlNames.NormalDistributions.TAG:
            return NormalDistribution(xml, guid=guid)
        elif xml.tag == DistributionXmlNames.EmpiricalDistributions.TAG:
            return EmpiricalDistribution.from_xml(xml)
        elif xml.tag == DistributionXmlNames.RawEmpiricalDistributions.TAG:
            return RawEmpiricalDistribution(xml)
        elif xml.tag == DistributionXmlNames.BinnedDistributions.TAG:
            return BinnedDistribution(xml)
        pass


class RealNumberDistributionWrapper(Distribution[float]):
    @property
    @abstractmethod
    def wrapped_distribution(self) -> Distribution[float]:
        pass

    @final
    def get_value(self, parameter: float) -> T:
        """

        Args:
            parameter: A number in the range [0, 1]

        Returns:
            The value of the distribution, in base units, at the supplied parameter.
        """
        return self.units.convert_to_base_units(self.wrapped_distribution.get_value(parameter))

    @property
    @abstractmethod
    def units(self) -> Unit:
        pass

    @final
    def get_parameter(self, value: T) -> Union[None, float]:
        """

        Args:
            value: The value of the distribution, in base units.

        Returns:
            The parameter of the distribution, if any, matching the supplied value; if the parameter
            does not exist, returns None.
        """
        return self.wrapped_distribution.get_parameter(self.units.convert_to_this_unit(value))


class DistanceDistribution(RealNumberDistributionWrapper):
    def __init__(self, xml: etree.ElementBase, guid: str = None):
        super().__init__(xml)
        self._units: Unit = DistanceUnits.DICTIONARY()[
            xml.attrib[DistributionXmlNames.ConnectorMaximumPositioningDistances.UNITS_ATTR]
        ]
        self._distribution: RealNumberDistribution = RealNumberDistributionFactory.from_xml(xml[0], guid=guid)

    @property
    def units(self) -> Unit:
        return self._units

    @property
    def wrapped_distribution(self) -> Distribution[float]:
        return self._distribution


class DecelerationDistribution(RealNumberDistributionWrapper):
    def __init__(self, xml: etree.ElementBase, guid: str = None):
        super().__init__(xml)
        self._units: Unit = AccelerationUnits.DICTIONARY()[
            xml.attrib[DistributionXmlNames.DecelerationDistributions.UNITS_ATTR]
        ]
        self._distribution: RealNumberDistribution = RealNumberDistributionFactory.from_xml(xml[0], guid=guid)

        probability_of_illogical_value: float = \
            self._distribution.get_parameter(self.units.convert_to_this_unit(1.0))  # 1.0 m/s^2
        if probability_of_illogical_value is not None and probability_of_illogical_value > 0.01:
            Logger.logger().warning(Localization.get_message('W0005', self.uuid))

    @property
    def units(self) -> Unit:
        return self._units

    @property
    def wrapped_distribution(self) -> Distribution[float]:
        return self._distribution


class AccelerationFunction(HasUuid):
    def __init__(self, xml: etree.ElementBase):
        self._speed_parameter_factor: float = 1.0

        def create_empirical_distribution(getter: Callable[[ElementBase], float]) -> RealNumberDistribution:
            self._speed_parameter_factor = self._speed_units.convert_to_base_units(max(map(
                lambda node: float(node.attrib[DistributionXmlNames.AccelerationFunctions.DP_VELOCITY_ATTR]),
                xml.iterfind(DistributionXmlNames.AccelerationFunctions.DP_TAG)
            )))
            data_point_tuples: List[Tuple[float, float]] = list(sorted([
                (
                    self._speed_units.convert_to_base_units(
                        float(node.attrib[DistributionXmlNames.AccelerationFunctions.DP_VELOCITY_ATTR])
                    ) / self._speed_parameter_factor,
                    self._acceleration_units.convert_to_base_units(
                        float(getter(node))
                    ),
                )
                for node in xml.iterfind(DistributionXmlNames.AccelerationFunctions.DP_TAG)
            ], key=lambda node: node[0]))

            return EmpiricalDistribution(data_point_tuples)

        super().__init__(xml)
        self._name = xml.attrib[DistributionXmlNames.AccelerationFunctions.NAME_ATTR] \
            if DistributionXmlNames.AccelerationFunctions.NAME_ATTR in xml.attrib \
            else ''
        self._speed_units: Unit = SpeedUnits.DICTIONARY()[xml.attrib[
            DistributionXmlNames.AccelerationFunctions.SPEED_UNIT_ATTR
        ]]
        self._acceleration_units: Unit = AccelerationUnits.DICTIONARY()[xml.attrib[
            DistributionXmlNames.AccelerationFunctions.ACCELERATION_UNIT_ATTR
        ]]
        self._mean_distribution: RealNumberDistribution = create_empirical_distribution(
            lambda node: node.attrib[DistributionXmlNames.AccelerationFunctions.DP_MEAN_ATTR]
        )
        self._std_deviation_distribution: RealNumberDistribution = create_empirical_distribution(
            lambda node: node.attrib[DistributionXmlNames.AccelerationFunctions.DP_STANDARD_DEVIATION_ATTR]
        )

        # check for decreasing monotonicity
        mean_acceleration_values: List[float] = list(map(
            lambda node: float(node.attrib[DistributionXmlNames.AccelerationFunctions.DP_MEAN_ATTR]),
            sorted(
                xml.iterfind(DistributionXmlNames.AccelerationFunctions.DP_TAG),
                key=lambda node: float(node.attrib[DistributionXmlNames.AccelerationFunctions.DP_VELOCITY_ATTR])
            )
        ))
        diffs: List[float] = [
            mean_acceleration_values[i] - mean_acceleration_values[i - 1]
            for i in range(1, len(mean_acceleration_values))
        ]
        if any(map(lambda diff: diff > 0, diffs)):
            Logger.logger().warning(Localization.get_message('W0004', self.uuid))

    def get_value(self, parameter: float, speed_in_base_units: float) -> float:
        speed_parameter: float = speed_in_base_units / self._speed_parameter_factor
        nd: stats.norm_gen = stats.norm(
            self._mean_distribution.get_value(speed_parameter),
            self._std_deviation_distribution.get_value(speed_parameter)
        )
        return nd.ppf(parameter)

    @property
    def name(self) -> str:
        return self._name


class Distributions:
    _doc_root: etree.ElementBase = None
    _connector_link_selection_behaviors: DistributionSet[ConnectorLinkSelectionBehaviorDistribution] = None
    _connector_max_positioning_distances: DistributionSet[DistanceDistribution] = None
    _vehicle_models: DistributionSet[VehicleModelDistribution] = None
    _colors: DistributionSet[ColorDistribution] = None
    _accelerations: DistributionSet[AccelerationFunction] = None
    _max_decelerations: DistributionSet[DecelerationDistribution] = None

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
        if cls._accelerations is not None:
            cls._accelerations.clear()
        if cls._max_decelerations is not None:
            cls._max_decelerations.clear()
        # TODO add more here as collections are added

    @classmethod
    def connector_link_selection_behaviors(cls) -> DistributionSet[ConnectorLinkSelectionBehaviorDistribution]:
        return cls._connector_link_selection_behaviors

    @classmethod
    def connector_max_positioning_distances(cls) -> DistributionSet[DistanceDistribution]:
        return cls._connector_max_positioning_distances

    @classmethod
    def vehicle_models(cls) -> DistributionSet[VehicleModelDistribution]:
        return cls._vehicle_models

    @classmethod
    def colors(cls) -> DistributionSet[ColorDistribution]:
        return cls._colors

    @classmethod
    def max_acceleration_functions(cls) -> DistributionSet[AccelerationFunction]:
        return cls._accelerations

    @classmethod
    def max_decelerations(cls) -> DistributionSet[DecelerationDistribution]:
        return cls._max_decelerations

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

        cls._accelerations = DistributionSet(
            get_distribution_set_node(DistributionXmlNames.AccelerationFunctions.TYPE),
            AccelerationFunction
        )

        cls._max_decelerations = DistributionSet(
            get_distribution_set_node(DistributionXmlNames.DecelerationDistributions.TYPE),
            DecelerationDistribution
        )

    @classmethod
    def process_file(cls, filename: str) -> None:
        _doc_root = etree.parse(filename).getroot()
        cls.read_from_xml(_doc_root, filename=filename)
