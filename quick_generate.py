#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速生成历史人物卡牌脚本
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from card_generator import CardGenerator

async def quick_generate():
    """快速生成历史人物卡牌"""
    print("🚀 快速生成历史人物卡牌")
    print("=" * 50)
    print("🎨 风格：稚嫩手绘风格")
    print("📐 构图：长方形（3:4比例）")
    print("🔲 边框：无边框设计")
    print("🏛️  范围：所有7个国家56位历史人物")
    print("=" * 50)

    generator = CardGenerator()

    try:
        # 生成所有历史人物卡牌（自动@参考图片并上传让AI模仿风格）
        reference_image = "微信图片_20250928182802_712_476.jpg"
        await generator.generate_historical_cards(
            countries=None,  # 所有国家
            style="hand_drawn",  # 稚嫩手绘风格（仍指定长方形，但风格由参考图决定）
            no_border=True,  # 无边框
            reference_image_path=reference_image,
            ai_full_card=True,
            backend="modelscope",  # 使用本地/显卡生成
            aspect_ratio="3:4"
        )
        print("\n✅ 生成完成！所有卡牌已保存到 Generated_Cards/ 目录")
    except KeyboardInterrupt:
        print("\n⚠️  生成被用户中断")
    except Exception as e:
        print(f"\n❌ 生成过程中出现错误: {e}")

if __name__ == "__main__":
    asyncio.run(quick_generate())
