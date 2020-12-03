class NetworkXmlNames:
    ROOT_TAG = 'network'
    LAYOUT_UNITS_ATTR = 'layout-units'
    SPEED_UNITS_ATTR = 'speed-limit-units'
    VERSION_ATTR = 'version'


class RoadXmlNames:
    COLLECTION_TAG = 'roads'
    TAG = 'road'
    NAME_ATTR = 'name'
    UUID_ATTR = 'uuid'
    BEHAVIOR_ATTR = 'behavior'
    SPEED_LIMIT_ATTR = 'speed-limit'
    CHAIN_TAG = 'chain'
    CHAIN_LENGTH_ATTR = 'length'
    CHAIN_POINTS_ATTR = 'points'
    LANES_COLLECTION_TAG = 'lanes'
    LANE_TAG = 'lane'
    LANE_ORDINAL_ATTR = 'ordinal'
    LANE_WIDTH_ATTR = 'width'
    LANE_MAY_MOVE_LEFT_ATTR = 'may-move-left'
    LANE_MAY_MOVE_RIGHT_ATTR = 'may-move-right'
    LANE_POLICY_TAG = 'policy'
    LANE_POLICY_ID_ATTR = 'id'
    LANE_POLICY_EXCEPT_TAG = 'except'
    LANE_POLICY_EXCEPT_POLICY_ATTR = 'policy'
    LANE_POLICY_EXCEPT_START_ATTR = 'start-time'
    LANE_POLICY_EXCEPT_END_ATTR = 'end-time'
    POCKETS_COLLECTION_TAG = 'pockets'
    POCKET_TAG = 'pocket'
    POCKET_SIDE_ATTR = 'side'
    POCKET_START_ORD_ATTR = 'start-ord'
    POCKET_END_ORD_ATTR = 'end-ord'
    POCKET_START_TAPER_ATTR = 'start-taper'
    POCKET_END_TAPER_ATTR = 'end-taper'
    POCKET_LANE_COUNT_ATTR = 'lane-count'
    ENTRY_TAG = 'vehicle-entry'
    ENTRY_INTERVAL_TAG = 'interval'
    ENTRY_INTERVAL_START_ATTR = 'start'
    ENTRY_INTERVAL_END_ATTR = 'end'
    ENTRY_INTERVAL_VEHICLE_TAG = 'vehicle'
    ENTRY_INTERVAL_VEHICLE_TYPE_ATTR = 'type'
    ENTRY_INTERVAL_VEHICLE_COUNT_ATTR = 'count'
    ENTRY_INTERVAL_VEHICLE_BYPASS_ATTR = 'congestion-bypassing-fraction'