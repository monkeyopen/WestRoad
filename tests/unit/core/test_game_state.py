
import pytest
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 现在可以正常导入
from src.core.game_state import GameState
from src.core.models.enums import GamePhase, PlayerColor
from src.core.models.player import PlayerState, ResourceSet, CattleCard
from src.core.models.board import BoardState, Location


class TestGameState:
    """测试GameState类"""

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

    def test_current_player_property(self):
        """测试current_player属性"""
        game_state = GameState(session_id="test_session")

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
        game_state.current_player_index = 0

        # 测试获取当前玩家
        current_player = game_state.current_player
        assert current_player is not None
        assert current_player.player_id == "player_001"

    def test_game_started_property(self):
        """测试game_started属性"""
        game_state = GameState(session_id="test")

        # 设置阶段应为未开始
        game_state.current_phase = GamePhase.SETUP
        assert not game_state.game_started

        # 玩家回合阶段应为已开始
        game_state.current_phase = GamePhase.PLAYER_TURN
        assert game_state.game_started

    def test_serialization_round_trip(self):
        """测试序列化往返"""
        # 创建游戏状态
        original = GameState(session_id="test_session")

        # 添加玩家
        player = PlayerState(
            player_id="player_001",
            user_id="user_123",
            player_color=PlayerColor.RED,
            display_name="测试玩家",
            resources=ResourceSet(money=15, workers=2),
            victory_points=10
        )
        original.players = [player]
        original.player_order = [0]

        # 序列化到字典
        state_dict = original.to_dict()

        # 从字典反序列化
        restored = GameState.from_dict(state_dict)

        # 验证数据一致性
        assert restored.session_id == original.session_id
        assert len(restored.players) == len(original.players)
        assert restored.players[0].player_id == original.players[0].player_id
        assert restored.players[0].resources.money == original.players[0].resources.money

    def test_clone_method(self):
        """测试克隆方法"""
        original = GameState(session_id="test_session")

        # 添加玩家
        player = PlayerState(
            player_id="player_001",
            user_id="user_123",
            player_color=PlayerColor.RED,
            display_name="测试玩家",
            resources=ResourceSet(money=15, workers=2)
        )
        original.players = [player]

        cloned = original.clone()

        # 验证基础数据相同
        assert cloned.session_id == original.session_id
        assert cloned.current_phase == original.current_phase
        assert cloned.version == original.version

        # 验证是深拷贝（修改克隆体不影响原对象）
        cloned.players[0].resources.money = 999
        assert original.players[0].resources.money == 15  # 原对象不应改变

        cloned.current_round = 5
        assert original.current_round == 0  # 原对象不应改变

    def test_increment_version(self):
        """测试版本号递增"""
        game_state = GameState(session_id="test_session")
        original_version = game_state.version
        original_time = game_state.last_updated

        game_state.increment_version()

        assert game_state.version == original_version + 1
        assert game_state.last_updated > original_time

    def test_get_player_by_id(self):
        """测试根据ID获取玩家"""
        game_state = GameState(session_id="test_session")

        # 添加玩家
        player = PlayerState(
            player_id="player_001",
            user_id="user_123",
            player_color=PlayerColor.RED,
            display_name="测试玩家",
            resources=ResourceSet(money=15, workers=2)
        )
        game_state.players = [player]

        # 测试存在的玩家
        found_player = game_state.get_player_by_id("player_001")
        assert found_player is not None
        assert found_player.player_id == "player_001"
        assert found_player.display_name == "测试玩家"

        # 测试不存在的玩家
        found_player = game_state.get_player_by_id("non_existent")
        assert found_player is None

    def test_get_player_index(self):
        """测试获取玩家索引"""
        game_state = GameState(session_id="test_session")

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

        # 测试存在的玩家
        index = game_state.get_player_index("player_001")
        assert index == 0

        index = game_state.get_player_index("player_002")
        assert index == 1

        # 测试不存在的玩家
        index = game_state.get_player_index("non_existent")
        assert index is None