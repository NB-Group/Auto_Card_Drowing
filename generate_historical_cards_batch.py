#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成历史人物卡牌脚本 - 云端Copilot + 参考图片 + AI写字
按国家顺序生成，秦国人物穿黑衣
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from card_generator import CardGenerator

# 历史人物数据 - 按国家分组，秦国在前
HISTORICAL_CHARACTERS = {
    # 秦国（先秦国，穿黑衣）
    "秦国": [
        {
            'name': '商鞅',
            'skill_name': '商鞅变法',
            'game_skill': '对自己国家进行全面改革，在接下来的2回合内，每一回合经济额外提升3，军事提升3，但同时会使关于触及贵族权益的变法卡牌效果减半。',
            'description': '战国时期著名政治家、改革家。在秦孝公的支持下，商鞅在秦国推行变法，包括废井田、开阡陌、重农桑、奖军功等一系列措施，使秦国从一个西部弱国逐渐崛起为强国。',
            'historical_source': '《史记·商君列传》'
        },
        {
            'name': '白起',
            'skill_name': '长平杀戮',
            'game_skill': '对敌方任意一骑兵、步兵发动攻击时，若敌方军队生命力多于自己，可反击一半伤害。',
            'description': '战国时期秦国名将，战国四大名将之首。一生征战无数，为秦国统一六国做出巨大贡献，尤其是在长平之战中，大破赵军，坑杀赵军降卒四十万，令六国闻风丧胆。',
            'historical_source': '《史记·白起王翦列传》'
        },
        {
            'name': '张仪',
            'skill_name': '连横破合',
            'game_skill': '会盟阶段，可选择一个国家有40%概率与秦国结盟。',
            'description': '战国时期著名纵横家，首创连横之术。他凭借卓越的口才和智慧，游走于各国之间，成功破解六国合纵抗秦的策略，为秦国的扩张创造有利的外交环境。',
            'historical_source': '《史记·张仪列传》'
        },
        {
            'name': '吕不韦',
            'skill_name': '吕氏春秋',
            'game_skill': '可获得3春秋通宝，变法效果翻倍。',
            'description': '战国末年秦国丞相，著名商人、政治家。他组织门客编写《吕氏春秋》，涵盖儒、道、法等诸家思想，对秦国的文化和政治发展产生重要影响。',
            'historical_source': '《史记·吕不韦列传》'
        },
        {
            'name': '李斯',
            'skill_name': '书同文策',
            'game_skill': '在经济为15时增加政治属性2、春秋通宝5。',
            'description': '秦朝丞相，著名政治家、文学家和书法家。他协助秦始皇统一六国后，推行统一文字、度量衡等政策，对中国历史的发展产生了深远影响。',
            'historical_source': '《史记·李斯列传》'
        },
        {
            'name': '蒙恬',
            'skill_name': '长城御敌',
            'game_skill': '在北方边境布置防线，当敌方骑兵部队进攻时，可使敌方骑兵的攻击力减半。',
            'description': '秦朝名将，为秦朝北疆的稳定做出重要贡献。他率领三十万大军北击匈奴，收复河南地，主持修建万里长城和九州直道，大大加强了秦朝对北方的控制。',
            'historical_source': '《史记·蒙恬列传》'
        },
        {
            'name': '秦始皇嬴政',
            'skill_name': '千古一帝',
            'game_skill': '可发动"统一战争"，对敌方所有未结盟国家同时发动攻击，在战争期间，每一回合自己所有攻击力翻倍生命力翻倍，战胜直接游戏胜利，战败没有任何损失。经济卡牌额外可抽取2张，政治加2。',
            'description': '秦朝开国皇帝，中国历史上第一位称皇帝的君主。他统一六国，建立中国历史上第一个大一统王朝，推行一系列统一措施，如统一文字、货币、度量衡等，对中国历史的发展产生了深远且不可磨灭的影响。',
            'historical_source': '《史记·秦始皇本纪》'
        },
        {
            'name': '范雎',
            'skill_name': '远交近攻',
            'game_skill': '在接下来的3回合内，与其他国家结盟成功率提升50%，对结盟国家发动攻击时，可获得额外的初始生命力2。',
            'description': '战国时期秦国丞相，著名政治家、谋略家。他向秦昭襄王提出"远交近攻"的策略，帮助秦国逐步削弱六国势力，为秦国的统一大业奠定坚实的战略基础。',
            'historical_source': '《史记·范雎蔡泽列传》'
        }
    ],

    # 韩国
    "韩国": [
        {
            'name': '韩非',
            'skill_name': '法家之智',
            'game_skill': '变法效果加倍。',
            'description': '韩国贵族，法家思想集大成者，著有《韩非子》，主张以法治国，强调君主集权。',
            'historical_source': '《史记·老子韩非列传》'
        },
        {
            'name': '申不害',
            'skill_name': '术治之术',
            'game_skill': '随机偷取敌方一张军事卡。',
            'description': '韩国的改革家，在韩为相期间，推行"术"治，加强了君主集权，使韩国一度强盛。',
            'historical_source': '《史记·老子韩非列传》'
        },
        {
            'name': '聂政',
            'skill_name': '刺客绝杀',
            'game_skill': '对敌方骑兵造成2伤害。',
            'description': '战国时期著名刺客，为报答严仲子知遇之恩，孤身一人刺杀韩相侠累。',
            'historical_source': '《史记·刺客列传》'
        },
        {
            'name': '卫庄',
            'skill_name': '流沙之主',
            'game_skill': '对敌方任意一军事卡效果减半。',
            'description': '韩国人，纵横家，"流沙"组织首领，剑术高超。',
            'historical_source': '在《史记》等史料基础上'
        },
        {
            'name': '张良',
            'skill_name': '谋圣之略',
            'game_skill': '可指定一名自己方角色，使其本回合伤害或经济效果翻倍。',
            'description': '韩国贵族后裔，后辅佐刘邦建立汉朝，是著名的谋士。',
            'historical_source': '《史记·留侯世家》'
        },
        {
            'name': '韩宇',
            'skill_name': '红莲之君',
            'game_skill': '回复自己一军事人物卡的生命值。',
            'description': '韩国公子，韩非的兄长，性格复杂，在韩国宫廷斗争中扮演重要角色。',
            'historical_source': '基于《史记》等史料的相关衍生作品'
        },
        {
            'name': '张开地',
            'skill_name': '辅国之臣',
            'game_skill': '增加自己场上所有卡牌防御 即无法被攻击。',
            'description': '韩国三朝元老，张平之父，张良之祖父，在韩国政坛具有重要地位。',
            'historical_source': '《史记》等相关史料'
        },
        {
            'name': '张平',
            'skill_name': '守土之责',
            'game_skill': '军事阶段结束可不被灭国。',
            'description': '韩国丞相，张开地之子，张良之父，致力于保卫韩国领土。',
            'historical_source': '《史记》等相关史料'
        }
    ],

    # 赵国
    "赵国": [
        {
            'name': '赵武灵王',
            'skill_name': '胡服骑射',
            'game_skill': '提升自己骑兵单位的攻击力至3。',
            'description': '赵国君主，推行"胡服骑射"改革，使赵国军事力量大增，拓展了领土。',
            'historical_source': '《史记·赵世家》'
        },
        {
            'name': '廉颇',
            'skill_name': '老将出马',
            'game_skill': '使敌方一军事人物陷入眩晕状态 即无法行动。',
            'description': '赵国名将，勇猛善战，与蔺相如上演了"将相和"的佳话，多次击败秦军。',
            'historical_source': '《史记·廉颇蔺相如列传》'
        },
        {
            'name': '李牧',
            'skill_name': '北境守护',
            'game_skill': '对敌方一军事人物的攻击造成反弹。',
            'description': '战国四大名将之一，长期驻守赵国北部边境，抵御匈奴，后又多次击败秦军。',
            'historical_source': '《史记·廉颇蔺相如列传》'
        },
        {
            'name': '蔺相如',
            'skill_name': '完璧归赵',
            'game_skill': '可从敌方手中夺回一张战时军事卡，并增加一点政治属性。',
            'description': '赵国上卿，凭借智慧和勇气，在"完璧归赵""渑池之会"等事件中维护了赵国尊严。',
            'historical_source': '《史记·廉颇蔺相如列传》'
        },
        {
            'name': '赵奢',
            'skill_name': '阏与之胜',
            'game_skill': '对敌方骑兵造成2伤害。',
            'description': '赵国名将，在阏与之战中击败秦军，因战功卓著被封为马服君。',
            'historical_source': '《史记·廉颇蔺相如列传》'
        },
        {
            'name': '平原君赵胜',
            'skill_name': '门客三千',
            'game_skill': '可额外抽取三张手牌战时军事卡，并随机使一张自己国家经济卡牌效果翻倍。',
            'description': '赵国公子，战国四公子之一，礼贤下士，门下食客众多，曾组织合纵抗秦。',
            'historical_source': '《史记·平原君虞卿列传》'
        },
        {
            'name': '赵括',
            'skill_name': '纸上谈兵',
            'game_skill': '对敌方全体造成3伤害，但自身也会损失1生命力。',
            'description': '赵国将领，熟读兵书却缺乏实战经验，在长平之战中被秦军大败。',
            'historical_source': '《史记·廉颇蔺相如列传》'
        },
        {
            'name': '毛遂',
            'skill_name': '自荐之勇',
            'game_skill': '立即获得一个额外的行动回合和2张经济卡牌。',
            'description': '平原君赵胜的门客，在赵国出使楚国时，自荐前往，成功说服楚王合纵抗秦。',
            'historical_source': '《史记·平原君虞卿列传》'
        }
    ],

    # 魏国
    "魏国": [
        {
            'name': '魏文侯',
            'skill_name': '文侯之治',
            'game_skill': '增加自己国家生命力2。',
            'description': '魏国开国君主，礼贤下士，任用李悝、吴起等进行改革，使魏国成为战国初期的强国。',
            'historical_source': '《史记·魏世家》'
        },
        {
            'name': '吴起',
            'skill_name': '魏武卒之威',
            'game_skill': '额外获得1张骑兵卡对敌方造成高额伤害。',
            'description': '战国初期军事家、政治家，在魏国创建了魏武卒，多次击败秦军，后到楚国进行变法。',
            'historical_source': '《史记·孙子吴起列传》'
        },
        {
            'name': '李悝',
            'skill_name': '变法之始',
            'game_skill': '增加2张战前经济卡。',
            'description': '魏国丞相，法家代表人物，主持了魏国的变法运动，制定了《法经》。',
            'historical_source': '《史记·平准书》等'
        },
        {
            'name': '庞涓',
            'skill_name': '桂陵之战',
            'game_skill': '在接下来的1回合内敌方所有攻击减半。',
            'description': '魏国名将，与孙膑同门，因嫉妒孙膑陷害其致残，后在桂陵之战和马陵之战中败于孙膑。',
            'historical_source': '《史记·孙子吴起列传》'
        },
        {
            'name': '信陵君魏无忌',
            'skill_name': '窃符救赵',
            'game_skill': '可恢复一张已被击败的卡牌。',
            'description': '战国四公子之一，魏昭王少子，魏安釐王异母弟，曾窃符救赵，两次击败秦军。',
            'historical_source': '《史记·魏公子列传》'
        },
        {
            'name': '乐羊',
            'skill_name': '中山之战',
            'game_skill': '使敌方的初始生命力减2。',
            'description': '魏国名将，乐毅的祖先，曾率军攻打中山国，取得胜利。',
            'historical_source': '《史记·乐毅列传》'
        },
        {
            'name': '西门豹',
            'skill_name': '河伯娶妻',
            'game_skill': '获得2点政治属性。',
            'description': '魏国邺令，以智慧和果断著称，破除了当地"河伯娶妻"的迷信，并主持修建了水利工程。',
            'historical_source': '《史记·滑稽列传》'
        },
        {
            'name': '公孙衍',
            'skill_name': '合纵连横',
            'game_skill': '可抽取1张未参战国家的卡牌。',
            'description': '魏国纵横家，主张合纵抗秦，曾佩五国相印，组织合纵联盟。',
            'historical_source': '《史记·张仪列传》'
        }
    ],

    # 楚国
    "楚国": [
        {
            'name': '屈原',
            'skill_name': '楚辞之魂',
            'game_skill': '获得5春秋通宝。',
            'description': '战国时期楚国诗人、政治家，他的作品对后世文学产生了深远影响。',
            'historical_source': '《史记·屈原贾生列传》'
        },
        {
            'name': '楚庄王',
            'skill_name': '一鸣惊人',
            'game_skill': '在国家处于10生命力使，可使己方全体卡牌的攻击力翻倍2回合。',
            'description': '春秋时期楚国国君，春秋五霸之一，在位期间楚国国力强盛。',
            'historical_source': '《史记·楚世家》'
        },
        {
            'name': '春申君黄歇',
            'skill_name': '战国四公子之智',
            'game_skill': '可抽取一名未参战国家人物或道具加入自己阵营。',
            'description': '战国四公子之一，楚考烈王时期的丞相，曾组织合纵抗秦，门下食客众多。',
            'historical_source': '《史记·春申君列传》'
        },
        {
            'name': '吴起',
            'skill_name': '吴起变法',
            'game_skill': '变法效果翻倍。',
            'description': '在楚国时进行变法，增强了楚国的国力，但最终因变法触动贵族利益而被杀。',
            'historical_source': '《史记·孙子吴起列传》'
        },
        {
            'name': '项燕',
            'skill_name': '楚国之盾',
            'game_skill': '提升自己全体军事人物的生命力2，与秦国战斗卡牌的防御提升至3。',
            'description': '楚国名将，项氏家族世代为楚将，在秦灭楚之战中，率领楚军抵抗秦军。',
            'historical_source': '《史记·项羽本纪》'
        },
        {
            'name': '孙叔敖',
            'skill_name': '水利之兴',
            'game_skill': '修建水利工程，提升经济属性3。',
            'description': '楚国令尹，主持修建了芍陂等水利工程，促进了楚国农业发展。',
            'historical_source': '《史记·循吏列传》'
        },
        {
            'name': '伍子胥',
            'skill_name': '复仇之怒',
            'game_skill': '对敌方全体在场人物造成自己国家生命力一半的攻击。',
            'description': '楚国人，后逃到吴国，辅佐吴王阖闾成就霸业，以报楚国杀父之仇。',
            'historical_source': '《史记·伍子胥列传》'
        },
        {
            'name': '庄蹻',
            'skill_name': '庄蹻起义',
            'game_skill': '提升3军事属性，可获得1张军事卡牌，但会降低2经济值。',
            'description': '楚国将领，后率领起义军反抗楚国统治，曾一度攻占楚国都城郢。',
            'historical_source': '《史记·西南夷列传》'
        }
    ],

    # 燕国
    "燕国": [
        {
            'name': '燕昭王',
            'skill_name': '千金买骨',
            'game_skill': '可随机抽取2张经济卡牌。',
            'description': '燕国国君，即位后广纳贤才，使燕国得以振兴，曾派乐毅率五国联军攻打齐国。',
            'historical_source': '《史记·燕世家》'
        },
        {
            'name': '乐毅',
            'skill_name': '五国伐齐',
            'game_skill': '与齐国战斗时，使齐国卡牌的军事道具卡效果减半2回合。',
            'description': '燕国名将，率领燕、赵、韩、魏、楚五国联军攻打齐国，连下七十余城。',
            'historical_source': '《史记·乐毅列传》'
        },
        {
            'name': '荆轲',
            'skill_name': '图穷匕见',
            'game_skill': '对敌方军事人物卡牌发动一次必死攻击，但自身也有一定几率会死亡（初始为50％，取决于太子丹）。',
            'description': '著名刺客，受燕太子丹之托，前往秦国刺杀秦始皇，最终行刺失败。',
            'historical_source': '《史记·刺客列传》'
        },
        {
            'name': '太子丹',
            'skill_name': '燕丹刺秦',
            'game_skill': '制定刺秦计划，可使荆轲卡牌的死亡率降低20％）。',
            'description': '燕国太子，为阻止秦国的兼并，策划了荆轲刺秦事件。',
            'historical_source': '《史记·刺客列传》'
        },
        {
            'name': '郭隗',
            'skill_name': '招贤之策',
            'game_skill': '抽取的一位经济或军事人物效果翻倍。',
            'description': '燕国大臣，向燕昭王提出"千金买骨"的计策，帮助燕国招揽人才。',
            'historical_source': '《史记·燕世家》'
        },
        {
            'name': '高渐离',
            'skill_name': '筑击秦王',
            'game_skill': '使敌方陷入短暂的混乱状态 即无法行动。',
            'description': '荆轲的好友，擅长击筑，荆轲刺秦失败后，他试图以筑击秦始皇，为荆轲报仇。',
            'historical_source': '《史记·刺客列传》'
        },
        {
            'name': '鞠武',
            'skill_name': '合纵之策',
            'game_skill': '可与其他国家结成联盟，共同对抗敌国2回合。',
            'description': '燕国太子丹的太傅，主张联合各国对抗秦国。',
            'historical_source': '《史记·刺客列传》'
        },
        {
            'name': '骑劫',
            'skill_name': '纸上谈兵',
            'game_skill': '对敌方生命力减半，但有一定几率失败（50％），最终导致自己损失1生命力。',
            'description': '燕国将领，在乐毅伐齐后期接替乐毅指挥，被田单用火牛阵击败。',
            'historical_source': '《史记·乐毅列传》'
        }
    ],

    # 齐国
    "齐国": [
        {
            'name': '孙膑',
            'skill_name': '围魏救赵',
            'game_skill': '使敌方生命力下降20％。',
            'description': '战国时期齐国军事家，孙武后代，著有《孙膑兵法》。曾在桂陵之战和马陵之战中，以奇谋大破魏军，展现出卓越的军事才能。',
            'historical_source': '《史记·孙子吴起列传》'
        },
        {
            'name': '晏婴',
            'skill_name': '舌战群儒',
            'game_skill': '在会盟场景中，可使不想结盟国家提出的结盟要求成功率降低50%，并且有30%概率说服任意一国家改变立场，与自己达成同盟。',
            'description': '春秋时期齐国著名政治家、外交家，以机智善辩、能言善谏闻名。历仕灵公、庄公、景公三朝，多次出使他国，凭借出色的外交才能维护齐国尊严。',
            'historical_source': '《史记·管晏列传》'
        },
        {
            'name': '田单',
            'skill_name': '火牛破阵',
            'game_skill': '当自己生命力低于敌方时，可使敌军2特殊人物直接退场。',
            'description': '战国时期齐国名将，在齐国濒临灭亡之际，于即墨之战中用火牛阵大破燕军，成功收复七十余城，使齐国复国。',
            'historical_source': '《史记·田单列传》'
        },
        {
            'name': '邹忌',
            'skill_name': '讽谏纳贤',
            'game_skill': '军事回合开始时，有50%概率额外获得2张经济或军事卡牌。',
            'description': '战国时期齐国大臣，以讽谏齐威王广开言路而著称。通过巧妙的劝谏方式，使齐威王积极纳谏，齐国得以政治清明，国力逐渐强盛。',
            'historical_source': '《史记·田敬仲完世家》'
        },
        {
            'name': '淳于髡',
            'skill_name': '诙谐谏言',
            'game_skill': '当经济值低于8时恢复春秋通宝10。',
            'description': '战国时期齐国著名的思想家、政治家，以博学多才、滑稽善辩著称。常以诙谐幽默的方式向齐王进谏，多次成功纠正齐王的错误决策。',
            'historical_source': '《史记·滑稽列传》'
        },
        {
            'name': '田穰苴',
            'skill_name': '司马治军',
            'game_skill': '为自己任意一骑兵、步兵进行整顿，即攻击力翻倍同时可以存在两回合。',
            'description': '春秋时期齐国著名军事家，著有《司马法》。他善于治军，曾临危受命，击退晋、燕联军，保卫齐国安全，因功被封为大司马。',
            'historical_source': '《史记·司马穰苴列传》'
        },
        {
            'name': '田横',
            'skill_name': '义不屈从',
            'game_skill': '当国家生命力低于6时，血量开始锁定2回合 即受不到任何攻击。',
            'description': '秦末起义军首领，原齐国贵族。在齐国灭亡后，率五百门客退守海岛。刘邦称帝后，田横不愿臣服，自刎而死，其门客听闻后亦全部自杀，以表忠义。',
            'historical_source': '《史记·田儋列传》'
        }
    ]
}

 # 变法卡、连锁卡与祭祀事件（作为卡牌数据的一部分）
HISTORICAL_CHARACTERS.update({
    "变法卡": [
        { 'name': '废除井田制', 'skill_name': '废井田', 'game_skill': '经济+3', 'description': '废除井田制（4张）', 'historical_source': '' },
        { 'name': '设立郡县制', 'skill_name': '郡县制', 'game_skill': '经济+3 政治+2', 'description': '设立郡县制（4张）', 'historical_source': '' },
        { 'name': '废除贵族优越权益', 'skill_name': '削贵族', 'game_skill': '经济+4 政治-2', 'description': '废除贵族优越权益（4张）', 'historical_source': '' },
        { 'name': '裁冗官', 'skill_name': '裁冗官', 'game_skill': '经济+1 军事+2', 'description': '裁冗官（4张）', 'historical_source': '' },
        { 'name': '奖励军功', 'skill_name': '奖军功', 'game_skill': '军事+1 政治+2', 'description': '奖励军功（4张）', 'historical_source': '' },
        { 'name': '括招兵', 'skill_name': '招兵', 'game_skill': '经济-1 政治-1 连锁+4', 'description': '括招兵（4张）', 'historical_source': '' },
        { 'name': '加征杂税', 'skill_name': '征税', 'game_skill': '经济+5 政治-1', 'description': '加征杂税（3张）', 'historical_source': '' },
        { 'name': '土地兼并', 'skill_name': '兼并', 'game_skill': '经济+7 政治-4 军事-2', 'description': '土地兼并（2张）', 'historical_source': '' },
        { 'name': '推广牛耕', 'skill_name': '牛耕', 'game_skill': '经济+1 军事+1', 'description': '推广牛耕（4张）', 'historical_source': '' },
        { 'name': '普及铁器农具', 'skill_name': '铁器', 'game_skill': '经济+2', 'description': '普及铁器农具（4张）', 'historical_source': '' },
        { 'name': '精细青铜器', 'skill_name': '青铜', 'game_skill': '经济+1 连锁+3', 'description': '精细青铜器（3张） 使用一切关于铁器后的变法卡后不可使用', 'historical_source': '' },
        { 'name': '钢的运用', 'skill_name': '钢', 'game_skill': '经济+4 连锁+5', 'description': '钢的运用（2张） 前提：使用过铁or青铜变法卡', 'historical_source': '' },
        { 'name': '中医理论奠基', 'skill_name': '中医', 'game_skill': '经济+4 连锁+2', 'description': '中医理论奠基（2张）', 'historical_source': '' },
        { 'name': '支持儒家思想', 'skill_name': '儒学', 'game_skill': '经济+5 政治+4 军事-1', 'description': '支持儒家思想（1张） 不可得兼（一个国家只能用1张）', 'historical_source': '' },
        { 'name': '支持法家思想', 'skill_name': '法学', 'game_skill': '经济-2 连锁+8', 'description': '支持法家思想（1张）', 'historical_source': '' },
        { 'name': '支持道家思想', 'skill_name': '道学', 'game_skill': '经济+5 政治+4 军事-1', 'description': '支持道家思想（1张）', 'historical_source': '' },
        { 'name': '支持兵家思想', 'skill_name': '兵学', 'game_skill': '连锁+5', 'description': '支持兵家思想（1张）', 'historical_source': '' },
        { 'name': '支持墨家思想', 'skill_name': '墨学', 'game_skill': '政治+5 连锁+5', 'description': '支持墨家思想（1张）', 'historical_source': '' },
        { 'name': '支持农家思想', 'skill_name': '农学', 'game_skill': '经济+7 军事-1', 'description': '支持农家思想（1张）', 'historical_source': '' },
        { 'name': '支持制衡家思想', 'skill_name': '制衡', 'game_skill': '经济-1 政治+6', 'description': '支持制衡家思想（1张）', 'historical_source': '' }
    ],
    "连锁卡": [
        { 'name': '贵族官僚阶级反对', 'skill_name': '贵族反对', 'game_skill': '连锁+7', 'description': '贵族官僚阶级反对（7张）', 'historical_source': '' },
        { 'name': '丞相驳回', 'skill_name': '驳回', 'game_skill': '连锁+3', 'description': '丞相驳回（3张）', 'historical_source': '' },
        { 'name': '民愤', 'skill_name': '民愤', 'game_skill': '连锁+6', 'description': '民愤（6张）', 'historical_source': '' },
        { 'name': '万能连锁', 'skill_name': '万能连锁', 'game_skill': '可反制任意变法卡', 'description': '万能连锁（若上家变法可用对应变法卡反制）', 'historical_source': '' }
    ],
    "祭祀": [
        { 'name': '蝗灾', 'skill_name': '蝗灾', 'game_skill': '本回合春秋币获取数-5', 'description': '蔽日垂云铁翼雷，噬尽青畴秉畀炎，赤地无遗警世篇。', 'historical_source': '' },
        { 'name': '暴雨', 'skill_name': '暴雨', 'game_skill': '本回合春秋币小铺价格翻倍', 'description': '黑云翻墨卷千嶂，银箭裂空破九霄，天河倒泻摧城阙，羯鼓声催万壑潮。', 'historical_source': '' },
        { 'name': '大旱', 'skill_name': '大旱', 'game_skill': '本回合变法阶段所有负面buff效果+3', 'description': '赤地千里魃焰炽，川泽竭，禾黍枯，金石焦。', 'historical_source': '' },
        { 'name': '白虹贯日', 'skill_name': '白虹贯日', 'game_skill': '本回合变法阶段不得使用连锁卡', 'description': '白虹贯日，天象示警，昔聂政刺韩傀，荆轲赴秦庭，皆承此异兆。', 'historical_source': '' },
        { 'name': '日食', 'skill_name': '日食', 'game_skill': '所有人三维-5', 'description': '日食之象，赤乌衔蟾宫而蚀影，金环悬昊穹以昭晦，阴阳相薄，晷仪潜移。', 'historical_source': '' },
        { 'name': '春雨贵如油', 'skill_name': '春雨', 'game_skill': '无效果', 'description': '甘霖潜夜，酥雨垂丝而苏群萌，烟笼碧芜以染新翠。', 'historical_source': '' },
        { 'name': '秋高气爽', 'skill_name': '秋高', 'game_skill': '本回合变法正面buff效果+1', 'description': '天高气清，云淡风轻，霜林染赭而寒潭湛碧。', 'historical_source': '' },
        { 'name': '五星连珠', 'skill_name': '五星', 'game_skill': '所有人政治+3', 'description': '五星聚东井，连珠曜霄汉，兆圣主之兴，应天休而彰瑞世', 'historical_source': '' },
        { 'name': '鸾凤和鸣', 'skill_name': '鸾凤', 'game_skill': '所有人获得5春秋币', 'description': '鸾凤和鸣，锵锵其声，兆琴瑟之永谐，应天作而昌世', 'historical_source': '' },
        { 'name': '南蛮入侵', 'skill_name': '南蛮', 'game_skill': '再进行一次祭祀（负面翻倍）', 'description': '南蛮入侵，若再进行一次祭祀，如是负面则翻倍，如是正面则不予理睬', 'historical_source': '' }
    ],

    # 新增：地理环境、税收、思想、道具与历史事件卡
    "地理环境": [
        { 'name': '河流沿岸', 'skill_name': '河流沿岸', 'game_skill': '经济+1', 'description': '河流沿岸国家因灌溉便利和土壤肥沃，农业生产条件优越（农业经济+1）。', 'historical_source': '' },
        { 'name': '山地屏障', 'skill_name': '山地防御', 'game_skill': '军事+1（防御）', 'description': '山地国家凭借天然地形屏障，在防御作战中占据显著优势（军事防御+1）。', 'historical_source': '' },
        { 'name': '黄河流域', 'skill_name': '黄河水运', 'game_skill': '军事+1（机动）', 'description': '黄河流域国家得益于发达的水运系统，在军队调动和后勤补给方面具有战略优势（军事机动+1）。', 'historical_source': '' }
    ],

    "税收机制": [
        { 'name': '税收周期', 'skill_name': '税收规则', 'game_skill': '每两回合上交1点任一属性；未交税: 经济-1 且两回合内禁用经济行动', 'description': '每个国家每两回合需向周王室交纳税收：上交自己任一属性的1点。未按时交税将遭受经济惩罚与外交限制。', 'historical_source': '' },
        { 'name': '税收收益', 'skill_name': '王室收益', 'game_skill': '每收10点税收，周王室任一属性+1；可用税收提升稳定性（+1经济）', 'description': '周王室可用税收进行建设：每收10点税收可提升任一属性1点，或用于增加稳定性从而带来额外经济收益。', 'historical_source': '' }
    ],

    "思想": [
        { 'name': '道家', 'skill_name': '道家', 'game_skill': '政治+2', 'description': '道家：政治+2。', 'historical_source': '' },
        { 'name': '儒家', 'skill_name': '儒家', 'game_skill': '政治+1 经济+1', 'description': '儒家：政治+1，经济+1。', 'historical_source': '' },
        { 'name': '墨家', 'skill_name': '墨家', 'game_skill': '军事+1 经济+1', 'description': '墨家：军事+1，经济+1。', 'historical_source': '' },
        { 'name': '法家', 'skill_name': '法家', 'game_skill': '政治+1 军事+1', 'description': '法家：政治+1，军事+1。', 'historical_source': '' },
        { 'name': '兵家', 'skill_name': '兵家', 'game_skill': '军事+2', 'description': '兵家：军事+2。', 'historical_source': '' }
    ],

    "道具卡": [
        { 'name': '竹简文书', 'skill_name': '竹简', 'game_skill': '免疫一次他国战争行动', 'description': '在农耕道具阶段使用：免疫他国对自己发起的战争。', 'historical_source': '' },
        { 'name': '战车', 'skill_name': '战车', 'game_skill': '军事生命+2', 'description': '在农耕/战时阶段使用：增加军事初始生命力+2。', 'historical_source': '' },
        { 'name': '青铜鼎', 'skill_name': '青铜鼎', 'game_skill': '使对方停止一次行动', 'description': '战时道具卡：使对方停止一次行动。', 'historical_source': '' },
        { 'name': '编钟', 'skill_name': '编钟', 'game_skill': '恢复1点生命', 'description': '战时道具卡：恢复一点国家的生命力。', 'historical_source': '' },
        { 'name': '水利工程', 'skill_name': '水利', 'game_skill': '经济+3', 'description': '科技道具卡：增加经济属性+3。', 'historical_source': '' },
        { 'name': '兵器改良', 'skill_name': '兵器', 'game_skill': '军事+2', 'description': '科技道具卡：提升军事属性+2。', 'historical_source': '' },
        { 'name': '神秘道具', 'skill_name': '神秘', 'game_skill': '产生特殊战场效果', 'description': '特殊道具：在特定情况下使用，产生独特效果，改变局势。', 'historical_source': '' }
    ],

    "历史事件卡": [
        { 'name': '锦囊·历史事件', 'skill_name': '锦囊', 'game_skill': '触发真实历史事件并影响局势', 'description': '历史事件卡（锦囊牌）：引发真实历史事件，影响战局或国家属性。', 'historical_source': '' }
    ]
})

async def generate_historical_cards_batch():
    """批量生成历史人物卡牌"""
    print("🚀 批量生成历史人物卡牌")
    print("=" * 50)
    print("🎨 后端：云端Copilot")
    print("📐 构图：长方形（3:4比例）")
    print("🔲 边框：无边框设计")
    print("✍️  文字：AI手写风格")
    print("=" * 50)

    generator = CardGenerator()
    reference_image = "微信图片_20250928182802_712_476.jpg"

    total_cards = sum(len(characters) for characters in HISTORICAL_CHARACTERS.values())
    print(f"📊 总计卡牌数量：{total_cards}")
    print("🏛️  生成顺序：秦国 → 韩国 → 赵国 → 魏国 → 楚国 → 燕国 → 齐国")
    print("=" * 50)

    success_count = 0
    total_processed = 0
    skipped_count = 0

    # 按国家顺序生成
    for country_name, characters in HISTORICAL_CHARACTERS.items():
        print(f"\n🏛️  开始生成 {country_name} ({len(characters)}张卡牌)")

        # 为秦国添加特殊要求
        is_qin = country_name == "秦国"

        for i, character in enumerate(characters, 1):
            total_processed += 1
            try:
                # 输出文件路径（按现有 Generated_Cards 命名规则）
                output_filename = f"{country_name}-{character['name']}.png"
                output_dir = os.path.join(os.path.dirname(__file__), "Generated_Cards")
                output_path = os.path.join(output_dir, output_filename)

                # 若已经生成过则跳过
                if os.path.exists(output_path):
                    skipped_count += 1
                    print(f"⏭️ [{total_processed}/{total_cards}] 跳过 已存在 {output_filename}")
                    continue

                # 生成卡牌数据
                card_data = generator.generate_historical_card_data(character, country_name)

                # 秦国黑衣要求已在generate_historical_card_data方法中处理


                print(f"\n🎯 [{total_processed}/{total_cards}] 生成 {country_name}-{character['name']}")

                # 调用单卡生成方法
                result = await generator.generate_single_card(
                    card_data=card_data,
                    style="hand_drawn",
                    no_border=True,
                    reference_image_path=reference_image,
                    backend="copilot",  # 使用云端
                    aspect_ratio="3:4"
                )

                if result:
                    success_count += 1
                    print(f"✅ {character['name']} 生成完成！")
                else:
                    print(f"❌ {character['name']} 生成失败：返回None")

            except KeyboardInterrupt:
                print(f"\n⚠️  生成被用户中断，已完成 {success_count}/{total_cards} 张卡牌")
                return
            except Exception as e:
                print(f"❌ {character['name']} 生成失败: {e}")
                import traceback
                traceback.print_exc()

        print(f"✅ {country_name} 完成！({success_count - (total_processed - len(characters))}/{len(characters)} 成功)")

    print(f"\n🎉 历史人物卡牌生成完成！成功生成 {success_count}/{total_cards} 张卡牌")
    print("🏛️  秦国人物已按要求穿着黑色衣袍")

if __name__ == "__main__":
    asyncio.run(generate_historical_cards_batch())
