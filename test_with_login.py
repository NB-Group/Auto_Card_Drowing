#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from card_generator import CardGenerator

async def test_login_and_generate():
    """测试登录状态并生成单张卡牌"""
    generator = CardGenerator()
    
    # 读取配置
    cards_data = generator.load_cards_config()
    if not cards_data:
        print("未找到卡牌配置")
        return
    
    # 选择第一张卡牌进行测试
    test_card = cards_data[0]
    print(f"测试卡牌: {test_card['card_name']}")
    print(f"AI提示词: {test_card['ai_prompt']}")
    
    # 生成卡牌
    result = await generator.generate_single_card(test_card)
    
    if result:
        print(f"测试成功！卡牌已保存到: {result}")
    else:
        print("测试失败！")

def main():
    print("开始测试卡牌生成系统（带登录状态保持）")
    print("=" * 50)
    
    try:
        asyncio.run(test_login_and_generate())
    except KeyboardInterrupt:
        print("\n用户中断了程序")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
