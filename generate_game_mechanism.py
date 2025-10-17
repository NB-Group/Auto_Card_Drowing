#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成道具卡牌脚本 - 云端Copilot + 参考图片 + AI写字
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from card_generator import CardGenerator

# 道具卡牌数据
PROP_CARDS = [
    # 农耕道具卡
    {
        'card_group': '道具卡',
        'card_name': '竹简文书',
        'color_theme': 'green',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为竹简文书道具卡，"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「竹简文书」，"
            "效果：免疫他国对自己发起的战争。"
            "策略应用：适合在经济弱势时使用，以避免被强国侵略。"
        ),
        'description': "农耕道具卡\n效果：免疫他国对自己发起的战争\n策略：经济弱势时使用",
        'price': '农耕道具',
        'country': '通用',
        'character_name': '竹简文书',
        'ai_writes_text': True
    },
    {
        'card_group': '道具卡',
        'card_name': '战车',
        'color_theme': 'red',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为战车道具卡，"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「战车」，"
            "效果：增加军事初始生命力+2。"
            "策略应用：在即将进行的战争前使用，以提升战斗优势。"
        ),
        'description': "农耕道具卡\n效果：增加军事初始生命力+2\n策略：战争前使用",
        'price': '农耕道具',
        'country': '通用',
        'character_name': '战车',
        'ai_writes_text': True
    },

    # 战时道具卡
    {
        'card_group': '道具卡',
        'card_name': '青铜鼎',
        'color_theme': 'yellow',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为青铜鼎道具卡，"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「青铜鼎」，"
            "效果：使对方停止一次行动。"
            "策略应用：可在敌方准备发动攻击时使用，迫使其重新考虑策略。"
        ),
        'description': "战时道具卡\n效果：使对方停止一次行动\n策略：敌方攻击时使用",
        'price': '战时道具',
        'country': '通用',
        'character_name': '青铜鼎',
        'ai_writes_text': True
    },
    {
        'card_group': '道具卡',
        'card_name': '编钟',
        'color_theme': 'blue',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为编钟道具卡，"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「编钟」，"
            "效果：恢复一点国家的生命力。"
            "策略应用：在战斗中受损后使用，以保持战斗力。"
        ),
        'description': "战时道具卡\n效果：恢复一点国家的生命力\n策略：战斗受损后使用",
        'price': '战时道具',
        'country': '通用',
        'character_name': '编钟',
        'ai_writes_text': True
    },

    # 科技道具卡
    {
        'card_group': '道具卡',
        'card_name': '水利工程',
        'color_theme': 'cyan',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为水利工程道具卡，"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「水利工程」，"
            "效果：增加经济属性+3。"
            "策略应用：适合在经济薄弱时使用，快速提升资源产出。"
        ),
        'description': "科技道具卡\n效果：增加经济属性+3\n策略：经济薄弱时使用",
        'price': '科技道具',
        'country': '通用',
        'character_name': '水利工程',
        'ai_writes_text': True
    },
    {
        'card_group': '道具卡',
        'card_name': '兵器改良',
        'color_theme': 'orange',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为兵器改良道具卡，"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「兵器改良」，"
            "效果：提升军事属性+2。"
            "策略应用：在准备发动战争前使用，以确保军队的优势。"
        ),
        'description': "科技道具卡\n效果：提升军事属性+2\n策略：战争前使用",
        'price': '科技道具',
        'country': '通用',
        'character_name': '兵器改良',
        'ai_writes_text': True
    },

    # 特殊道具卡
    {
        'card_group': '道具卡',
        'card_name': '神秘道具',
        'color_theme': 'purple',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为神秘道具卡，"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「神秘道具」，"
            "效果：召唤未知援助，提供战斗优势。"
            "用途：在特定情况下使用，产生独特效果，改变游戏局势。"
        ),
        'description': "特殊道具卡\n效果：召唤未知援助，提供战斗优势\n用途：特定情况下使用",
        'price': '特殊道具',
        'country': '通用',
        'character_name': '神秘道具',
        'ai_writes_text': True
    },

    # 历史事件卡
    {
        'card_group': '道具卡',
        'card_name': '历史事件卡',
        'color_theme': 'gold',
        'ai_prompt': (
            "中国古风手绘卡面，水性马克笔上色，明显笔触、水痕与叠色，"
            "稚嫩童趣手绘风，长方形(3:4)构图。主体为历史事件卡（锦囊牌），"
            "必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            "但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            "与纸面自然融合，无水印无Logo。"
            "文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            "上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。人物头像和文字整体向下移动，顶部留白充足。"
            "排版要求：顶部大标题「历史事件卡」，"
            "效果：引发真实历史事件，影响战局。"
            "用途：改变游戏局势的锦囊牌。"
        ),
        'description': "历史事件卡（锦囊牌）\n效果：引发真实历史事件，影响战局\n用途：改变游戏局势",
        'price': '历史事件',
        'country': '通用',
        'character_name': '历史事件卡',
        'ai_writes_text': True
    }
]

async def generate_prop_cards():
    """生成所有道具卡牌"""
    print("🚀 生成道具卡牌")
    print("=" * 50)
    print("🎨 后端：云端Copilot")
    print("📐 构图：长方形（3:4比例）")
    print("🔲 边框：无边框设计")
    print("✍️  文字：AI手写风格")
    print(f"📊 卡牌数量：{len(PROP_CARDS)}")
    print("=" * 50)

    generator = CardGenerator()
    reference_image = "微信图片_20250928182802_712_476.jpg"

    success_count = 0

    for i, card_data in enumerate(PROP_CARDS, 1):
        try:
            print(f"\n🎯 生成第 {i}/{len(PROP_CARDS)} 张卡牌: {card_data['card_name']}")
            print(f"   卡牌数据: {card_data.get('card_group')} - {card_data.get('card_name')}")

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
                print(f"✅ {card_data['card_name']} 生成完成！保存路径: {result}")
            else:
                print(f"❌ {card_data['card_name']} 生成失败：返回None")

        except KeyboardInterrupt:
            print(f"\n⚠️  生成被用户中断，已完成 {success_count} 张卡牌")
            break
        except Exception as e:
            print(f"❌ {card_data['card_name']} 生成失败: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n🎉 道具卡牌生成完成！成功生成 {success_count}/{len(PROP_CARDS)} 张卡牌")

if __name__ == "__main__":
    asyncio.run(generate_prop_cards())
