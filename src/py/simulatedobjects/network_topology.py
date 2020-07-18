from typing import List

class NetworkTopologyLink:
    class _ConnectionPoint:
        def __init__(self, *, connecting_road_id: str,
                this_road_offset: float, connecting_road_offset: float,
                this_road_ordinate: float, connecting_road_ordinate: float):
            super().__init__()

            self._connecting_road_id = connecting_road_id
            self._this_road_offset = this_road_offset
            self._connecting_road_offset = connecting_road_offset
            self._this_road_ordinate = this_road_ordinate
            self._connecting_road_ordinate = connecting_road_ordinate

        def get_connecting_road_id(self) -> str:
            return self._connecting_road_id
        
        def get_this_offset(self) -> float:
            return self._this_road_offset

        def get_connecting_offset(self) -> float:
            return self._connecting_road_offset

        def get_connecting_road_ordinate(self) -> float:
            return self._connecting_road_ordinate

        def get_this_road_ordinate(self) -> float:
            return self._this_road_ordinate

    def get_length(self) -> float:
        # TODO calculate this from geometry
        return 0

    def get_incoming_connections(self) -> List[_ConnectionPoint]:
        # TODO 
        return []

    def get_outgoing_connections(self) -> List[_ConnectionPoint]:
        # TODO
        return []