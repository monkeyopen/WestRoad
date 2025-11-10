from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class Location:
    """地点定义"""
    location_id: int
    location_type: str  # station, hazard, building_site, etc.
    name: str
    owner_id: Optional[str] = None  # 如果被玩家建造，则有所有者
    available_actions: List[str] = field(default_factory=list)


@dataclass
class BoardState:
    """版图状态"""
    locations: Dict[int, Location] = field(default_factory=dict)
    neutral_buildings: Dict[int, str] = field(default_factory=dict)
    player_buildings: Dict[int, Dict[str, str]] = field(default_factory=dict)
    available_locations: List[int] = field(default_factory=list)
    kansas_city_state: Dict[str, any] = field(default_factory=dict)


    def __post_init__(self):
        if self.available_locations is None:
            self.available_locations = []
        if self.player_buildings is None:
            self.player_buildings = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)
