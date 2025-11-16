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


class AuxiliaryAbility(Enum):
    GOLD_1 = "gold_1"      # 1金币
    GOLD_2 = "gold_2"      # 2金币
    DRAW_1 = "draw_1"  # 抽1张牌
    DRAW_2 = "draw_2"  # 抽2张牌
    REVERSE_1 = "reverse_1"  # 倒车1次
    REVERSE_2 = "reverse_2"  # 倒车2次
    FORWARD_1 = "forward_1"  # 开车1次
    FORWARD_2 = "forward_2"  # 开车2次
    DROP_1 = "drop_1"  # 掉1张牌
    DROP_2 = "drop_2"  # 掉2张牌
    SPEED_1 = "speed_1"  # 速度+1
    SPEED_2 = "speed_2"  # 速度+2
    # 手牌容量+1
    CARD_CAPACITY_1 = "card_capacity_1"
    # 手牌容量+2
    CARD_CAPACITY_2 = "card_capacity_2"
    # 荣誉上限+1
    HONOR_LIMIT_1 = "honor_limit_1"
    # 荣誉上限+2
    HONOR_LIMIT_2 = "honor_limit_2"











