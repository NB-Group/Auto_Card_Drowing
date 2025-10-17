#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史人物卡牌生成示例
演示如何使用稚嫩手绘风格生成长方形构图的历史人物卡牌
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from card_generator import CardGenerator

async def demo_historical_cards():
    """演示历史人物卡牌生成"""
    print("🎨 历史人物卡牌生成演示")
    print("=" * 50)

    generator = CardGenerator()

    # 示例1：生成韩国和秦国的卡牌（默认稚嫩手绘风格，无边框）
    print("\n📋 示例1：生成韩国和秦国的卡牌")
    print("命令：python card_generator.py historical 韩国,秦国")
    print("特点：稚嫩手绘风格，长方形构图，无边框")

    countries = ["韩国", "秦国"]
    await generator.generate_historical_cards(countries=countries, style="hand_drawn", no_border=True)

    # 示例2：生成所有国家的卡牌
    print("\n📋 示例2：生成所有国家的卡牌")
    print("命令：python card_generator.py historical")
    print("特点：稚嫩手绘风格，长方形构图，无边框")

    # await generator.generate_historical_cards(countries=None, style="hand_drawn", no_border=True)

    # 示例3：传统风格，有边框
    print("\n📋 示例3：传统风格，有边框")
    print("命令：python card_generator.py historical 韩国 classic false")
    print("特点：传统写实风格，正方形构图，有边框")

    # await generator.generate_historical_cards(countries=["韩国"], style="classic", no_border=False)

    print("\n✅ 演示完成！")
    print("\n💡 实际使用时请确保：")
    print("   1. 已登录Microsoft Copilot账户")
    print("   2. 网络连接正常")
    print("   3. 有足够的AI生成额度")
    print("   4. 目标文件夹有写入权限")

if __name__ == "__main__":
    asyncio.run(demo_historical_cards())

