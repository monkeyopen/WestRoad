import pytest
import json
from datetime import datetime
from typing import Dict, Any

# 使用绝对导入
from src.core.game_state import GameState
from src.core.models.player import PlayerState
from src.core.models.base_models import ResourceSet, CattleCard, BoardState
from src.core.models.enums import GamePhase, PlayerColor


class TestResourceSet:
    """测试ResourceSet类"""

    def test_resource_set_initialization(self):
        """测试资源集初始化"""
        resources = ResourceSet(money=10, workers=3, certificates=2)
        assert resources.money == 10
        assert resources.workers == 3
        assert resources.certificates == 2
        assert resources.craftsmen == 0  # 默认值


class TestCattleCard:
    """测试CattleCard类"""

    def test_cattle_card_creation(self):
        """测试牛牌创建"""
        card = CattleCard(
            card_id="card_001",
            card_number="1A",
            base_value=5,
            special_ability="double_move"
        )
        assert card.card_id == "card_001"
        assert card.card_number == "1A"
        assert card.base_value == 5
        assert card.special_ability == "double_move"


class TestPlayerState:
    """测试PlayerState类"""

    @pytest.fixture
    def sample_player(self):
        """创建示例玩家"""
        return PlayerState(
            player_id="player_001",
            user_id="user_123",
            player_color=PlayerColor.RED,
            display_name="测试玩家",
            position=5,
            resources=ResourceSet(money=15, workers=2),
            victory_points=10
        )

    def test_player_initialization(self, sample_player):
        """测试玩家初始化"""
        assert sample_player.player_id == "player_001"
        assert sample_player.user_id == "user_123"
        assert sample_player.player_color == PlayerColor.RED
        assert sample_player.display_name == "测试玩家"
        assert sample_player.position == 5
        assert sample_player.victory_points == 10


class TestGameState:
    """测试GameState主类"""

    @pytest.fixture
    def sample_game_state(self):
        """创建示例游戏状态"""
        game_state = GameState(session_id="test_session_001")

        # 添加玩家
        player1 = PlayerState(
            player_id="player_001",
            user_id="user_123",
            player_color=PlayerColor.RED,
            display_name="玩家1",
            resources=ResourceSet(money=10, workers=3)
        )

        player2 = PlayerState(
            player_id="player_002",
            user_id="user_456",
            player_color=PlayerColor.BLUE,
            display_name="玩家2",
            resources=ResourceSet(money=8, workers=2)
        )

        game_state.players = [player1, player2]
        game_state.player_order = [0, 1]
        game_state.current_phase = GamePhase.PLAYER_TURN
        game_state.current_player_index = 0

        return game_state

    def test_game_state_initialization(self):
        """测试游戏状态初始化"""
        game_state = GameState(session_id="test_session")

        assert game_state.session_id == "test_session"
        assert game_state.game_version == "1.0"
        assert game_state.current_phase == GamePhase.SETUP
        assert game_state.current_round == 0
        assert game_state.current_player_index == 0
        assert game_state.version == 1
        assert isinstance(game_state.last_updated, datetime)
        assert len(game_state.players) == 0

    def test_current_player_property(self, sample_game_state):
        """测试current_player属性"""
        game_state = sample_game_state

        # 测试获取当前玩家
        current_player = game_state.current_player
        assert current_player is not None
        assert current_player.player_id == "player_001"

    def test_to_dict_serialization(self, sample_game_state):
        """测试序列化为字典"""
        game_state = sample_game_state
        state_dict = game_state.to_dict()

        # 检查基础字段
        assert state_dict["session_id"] == "test_session_001"
        assert state_dict["current_phase"] == "player_turn"
        assert state_dict["current_round"] == 0
        assert state_dict["current_player_index"] == 0
        assert state_dict["version"] == 1

        # 检查玩家数据
        assert len(state_dict["players"]) == 2
        assert state_dict["players"][0]["player_id"] == "player_001"
        assert state_dict["players"][0]["resources"]["money"] == 10

    # 这里继续添加其他测试方法...
    # 由于篇幅限制，只展示关键测试，完整测试代码可以逐步添加