from enum import Enum

class GamePhase(Enum):
    """游戏阶段枚举"""
    SETUP = "setup"           # 游戏设置阶段
    PLAYER_TURN = "player_turn"  # 玩家回合
    CATTLE_SALE = "cattle_sale"  # 卖牛阶段
    END_GAME = "end_game"     # 游戏结束

class PlayerColor(Enum):
    """玩家颜色枚举"""
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PURPLE = "purple"
    ORANGE = "orange"

class ActionType(Enum):
    """行动类型枚举"""
    MOVE = "move"             # 移动
    HIRE_WORKER = "hire_worker"  # 雇佣工人
    BUILD = "build"           # 建造建筑
    BUY_CATTLE = "buy_cattle"  # 购买牛牌
    SELL_CATTLE = "sell_cattle"  # 卖出牛群
    USE_ABILITY = "use_ability"  # 使用能力



class WorkerType(Enum):
    """工人类型枚举"""
    DRIVER = "driver"      # 司机
    COWBOY = "cowboy"     # 牛仔
    BUILDER = "builder"   # 建筑工人

class CardType(Enum):
    """牌类型枚举"""
    CATTLE = "cattle"  # 牛牌
    ACTION_A = "action_a"  # 动作A牌
    ACTION_B = "action_b"  # 动作B牌
    ACTION_C = "action_c"  # 动作C牌
    MISSION = "mission"  # 任务牌
    TEST= "test"  # 测试牌
    PUBLIC_BUILDING = "public_building"  # 公有建筑物牌
    STATION_FLAG = "station_flag"  # 站长标记






