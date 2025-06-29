import asyncio
from card_generator import CardGenerator

async def test_single_card():
    """测试生成单张卡牌"""
    generator = CardGenerator()
    
    # 加载配置
    cards_data = generator.load_cards_config()
    
    if not cards_data:
        print("未找到卡牌配置数据")
        return
    
    # 选择第一张卡牌进行测试
    test_card = cards_data[0]
    print(f"测试卡牌: {test_card['card_name']}")
    print(f"AI提示词: {test_card['ai_prompt']}")
    
    # 生成卡牌
    result = await generator.generate_single_card(test_card)
    
    if result:
        print(f"测试成功！卡牌保存在: {result}")
    else:
        print("测试失败")

if __name__ == "__main__":
    asyncio.run(test_single_card())
