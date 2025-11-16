# 牌堆配置

# 牛牌配置 (50张)
CATTLE_DECK_CONFIG = {
    "card_type": "cattle",
    "total_count": 50,
    "card_prototypes": [
        {
            "name": "普通牛牌",
            "description": "基础牛牌",
            "base_value": 3,
            "cost": 2,
            "count": 30
        },
        {
            "name": "优质牛牌",
            "description": "高价值牛牌",
            "base_value": 5,
            "cost": 4,
            "count": 15
        },
        {
            "name": "珍稀牛牌",
            "description": "稀有高价值牛牌",
            "base_value": 8,
            "cost": 6,
            "special_ability": "double_value",
            "count": 5
        }
    ]
}

# 动作A牌配置 (50张)
ACTION_A_DECK_CONFIG = {
    "card_type": "action_a",
    "total_count": 50,
    "card_prototypes": [
        {
            "name": "水灾",
            "description": "水灾牌",
            "special_ability": "-1",
            "count": 5
        },
        {
            "name": "水灾",
            "description": "水灾牌",
            "special_ability": "-2",
            "count": 5
        },
        {
            "name": "旱灾",
            "description": "旱灾牌",
            "special_ability": "-1",
            "count": 5
        },
        {
            "name": "旱灾",
            "description": "旱灾牌",
            "special_ability": "-2",
            "count": 5
        },
        {
            "name": "落石",
            "description": "落石牌",
            "special_ability": "-1",
            "count": 5
        },
        {
            "name": "落石",
            "description": "落石牌",
            "special_ability": "-2",
            "count": 5
        },
        {
            "name": "蓝帐篷",
            "description": "蓝帐篷",
            "special_ability": "-1",
            "count": 10
        },
        {
            "name": "绿帐篷",
            "description": "绿帐篷",
            "special_ability": "-2",
            "count": 10
        }
    ]
}

# 动作B牌配置 (60张)
ACTION_B_DECK_CONFIG = {
    "card_type": "action_b",
    "total_count": 60,
    "card_prototypes": [
        {
            "name": "牛仔",
            "description": "擅长买牛",
            "count": 20
        },
        {
            "name": "建筑工人",
            "description": "擅长建筑",
            "count": 20
        },
        {
            "name": "司机",
            "description": "擅长驾驶",
            "count": 20
        }
    ]
}

# 动作C牌配置 (60张)
ACTION_C_DECK_CONFIG = {
    "card_type": "action_c",
    "total_count": 60,
    "card_prototypes": [
        {
            "name": "加速卡",
            "description": "加速行动",
            "special_ability": "speed_up",
            "count": 25
        },
        {
            "name": "保护卡",
            "description": "防止负面效果",
            "special_ability": "protection",
            "count": 25
        },
        {
            "name": "复制卡",
            "description": "复制其他卡牌效果",
            "special_ability": "copy_ability",
            "count": 10
        }
    ]
}

# 任务牌配置 (40张)
MISSION_DECK_CONFIG = {
    "card_type": "mission",
    "total_count": 40,
    "card_prototypes": [
        {
            "name": "运输任务",
            "description": "运输货物到指定地点",
            "base_value": 5,
            "metadata": {"type": "transport", "destination": "kansas_city"},
            "count": 15
        },
        {
            "name": "建造任务",
            "description": "建造指定类型建筑",
            "base_value": 8,
            "metadata": {"type": "build", "building_type": "station"},
            "count": 15
        },
        {
            "name": "收集任务",
            "description": "收集特定资源",
            "base_value": 6,
            "metadata": {"type": "collect", "resource": "cattle"},
            "count": 10
        }
    ]
}

# 测试牌配置 (5张)
TEST_DECK_CONFIG = {
    "card_type": "test",
    "total_count": 5,
    "card_prototypes": [
        {
            "name": "测试任务1",
            "description": "测试运输货物到指定地点",
            "base_value": 2,
            "metadata": {"type": "transport", "destination": "kansas_city"},
            "count": 2
        },
        {
            "name": "测试任务2",
            "description": "测试建造指定类型建筑",
            "base_value": 8,
            "metadata": {"type": "build", "building_type": "station"},
            "count": 2
        },
        {
            "name": "测试任务3",
            "description": "测试收集特定资源",
            "base_value": 6,
            # "metadata": {"type": "collect", "resource": "cattle"},
            "count": 1
        }
    ]
}

# config/cards.py

# 公有建筑物牌配置 (7张)
PUBLIC_BUILDING_DECK_CONFIG = {
    "card_type": "public_building",
    "total_count": 7,
    "card_prototypes": [
        {
            "name": "车站",
            "description": "提供移动和建造能力",
            "base_value": 0,
            "cost": 0,
            "special_ability": "提供移动和建造能力",
            "count": 1
        },
        {
            "name": "牧场",
            "description": "提供购买牛群能力",
            "base_value": 0,
            "cost": 0,
            "special_ability": "提供购买牛群能力",
            "count": 1
        },
        {
            "name": "危险建筑",
            "description": "特殊效果建筑",
            "base_value": 0,
            "cost": 0,
            "special_ability": "特殊效果建筑",
            "count": 1
        },
        {
            "name": "电报站",
            "description": "远程通信和交易",
            "base_value": 0,
            "cost": 0,
            "special_ability": "telegraph",
            "count": 1
        },
        {
            "name": "教堂",
            "description": "提供祝福和特殊能力",
            "base_value": 0,
            "cost": 0,
            "special_ability": "church",
            "count": 1
        },
        {
            "name": "银行",
            "description": "金融交易和贷款",
            "base_value": 0,
            "cost": 0,
            "special_ability": "bank",
            "count": 1
        },
        {
            "name": "酒店",
            "description": "休息和恢复",
            "base_value": 0,
            "cost": 0,
            "special_ability": "休息和恢复",
            "count": 1
        }
    ]
}

# 站长标记配置 (7张)
STATION_FLAG_DECK_CONFIG = {
    "card_type": "station_flag",
    "total_count": 7,
    "card_prototypes": [
        {
            "name": "车站",
            "description": "提供移动和建造能力",
            "base_value": 0,
            "cost": 0,
            "special_ability": "提供移动和建造能力",
            "count": 1
        },
        {
            "name": "牧场",
            "description": "提供购买牛群能力",
            "base_value": 0,
            "cost": 0,
            "special_ability": "提供购买牛群能力",
            "count": 1
        },
        {
            "name": "危险建筑",
            "description": "特殊效果建筑",
            "base_value": 0,
            "cost": 0,
            "special_ability": "特殊效果建筑",
            "count": 1
        },
        {
            "name": "电报站",
            "description": "远程通信和交易",
            "base_value": 0,
            "cost": 0,
            "special_ability": "telegraph",
            "count": 1
        },
        {
            "name": "教堂",
            "description": "提供祝福和特殊能力",
            "base_value": 0,
            "cost": 0,
            "special_ability": "church",
            "count": 1
        },
        {
            "name": "银行",
            "description": "金融交易和贷款",
            "base_value": 0,
            "cost": 0,
            "special_ability": "bank",
            "count": 1
        },
        {
            "name": "酒店",
            "description": "休息和恢复",
            "base_value": 0,
            "cost": 0,
            "special_ability": "休息和恢复",
            "count": 1
        }
    ]
}

# 所有牌堆配置
DECK_CONFIGS = {
    "cattle": CATTLE_DECK_CONFIG,
    "action_a": ACTION_A_DECK_CONFIG,
    "action_b": ACTION_B_DECK_CONFIG,
    "action_c": ACTION_C_DECK_CONFIG,
    "mission": MISSION_DECK_CONFIG,
    "test": TEST_DECK_CONFIG,
    "public_building": PUBLIC_BUILDING_DECK_CONFIG,
    "station_flag": STATION_FLAG_DECK_CONFIG
}

# 地图节点配置 - 需要放置公有建筑物的节点
PUBLIC_BUILDING_NODES = [1, 5, 9, 10, 12, 15, 17]

