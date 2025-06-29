import json
import asyncio
import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import tempfile

class CardGenerator:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.base_img_path = os.path.join(self.base_path, "Base_IMG")
        self.output_path = os.path.join(self.base_path, "Generated_Cards")
        self.user_data_path = os.path.join(self.base_path, "browser_data")
        self.cookies_path = os.path.join(self.base_path, "cookies.json")
        
        # 创建必要的目录
        for path in [self.output_path, self.user_data_path]:
            if not os.path.exists(path):
                os.makedirs(path)
    def load_cards_config(self):
        """读取卡牌配置文件"""
        config_path = os.path.join(self.base_path, "cards.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return []
    
    async def save_cookies(self, context):
        """保存cookies"""
        try:
            cookies = await context.cookies()
            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print("Cookies已保存")
        except Exception as e:
            print(f"保存Cookies失败: {e}")
    async def load_cookies(self, context):
        """加载cookies"""
        try:
            if os.path.exists(self.cookies_path):
                with open(self.cookies_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                print("Cookies已加载")
                return True
        except Exception as e:
            print(f"加载Cookies失败: {e}")
        return False
    
    async def generate_ai_image(self, prompt):
        """使用Playwright生成AI图片"""
        # 添加总体提示词前缀
        base_prompt = "写实融合国风插画风格（参考《清明上河图》的精致线条感与《鬼谷八荒》的色彩层次）。整体色调偏复古，低饱和度，背景带有米黄羊皮纸质感。图片长宽比注意只能是1比1。生成字时请使用标准正楷字。"
        full_prompt = base_prompt + " " + prompt
        
        print(f"正在生成图片，完整提示词: {full_prompt}")
        
        async with async_playwright() as p:
            # 启动浏览器，使用持久化用户数据目录
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_path,
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            try:
                # 如果没有打开的页面，创建新页面
                if len(browser.pages) == 0:
                    page = await browser.new_page()
                else:
                    page = browser.pages[0]
                
                # 检查是否已经在Copilot页面，如果不是则导航
                current_url = page.url
                if 'copilot.microsoft.com' not in current_url:
                    print("导航到Copilot网站...")
                    await page.goto("https://copilot.microsoft.com", timeout=60000)
                    # 等待页面加载
                    await page.wait_for_timeout(3000)
                
                # 检查是否需要登录
                try:
                    # 查找登录按钮或用户头像来判断登录状态
                    login_button = await page.query_selector('button[data-testid="sign-in-button"]')
                    if login_button:
                        print("检测到未登录状态，请在浏览器中登录...")
                        print("登录完成后，按回车键继续...")
                        input("按回车键继续...")
                except:
                    pass
                
                # 等待页面完全加载
                await page.wait_for_timeout(2000)
                
                # 定位输入框并输入提示词
                input_selector = 'textarea[data-testid="composer-input"]'
                try:
                    await page.wait_for_selector(input_selector, timeout=30000)
                except:
                    # 如果找不到指定的输入框，尝试其他可能的选择器
                    alternative_selectors = [
                        'textarea[placeholder*="消息"]',
                        'textarea[placeholder*="Message"]',
                        'textarea#userInput',
                        'textarea[role="textbox"]'
                    ]
                    
                    for selector in alternative_selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                            input_selector = selector
                            break
                        except:
                            continue
                    else:
                        print("未找到输入框，请检查页面状态")
                        return None
                  # 清空输入框并输入新提示词
                await page.fill(input_selector, "")
                await page.type(input_selector, full_prompt, delay=50)
                
                # 发送消息
                await page.keyboard.press('Enter')
                
                # 等待生成开始 - 检查是否有生成指示器
                print("等待AI开始生成...")
                try:
                    await page.wait_for_selector('.size-3\\.5.rounded.bg-salmon-550', timeout=10000)
                    print("检测到AI正在生成...")
                except:
                    print("未检测到生成指示器，继续等待...")
                
                # 等待生成完成 - 生成指示器消失
                max_wait_time = 120  # 最多等待2分钟
                wait_interval = 2
                waited_time = 0
                
                while waited_time < max_wait_time:
                    try:
                        # 检查是否还在生成
                        generating_indicator = await page.query_selector('.size-3\\.5.rounded.bg-salmon-550')
                        if not generating_indicator:
                            print("AI生成完成")
                            break
                    except:
                        pass
                    
                    await page.wait_for_timeout(wait_interval * 1000)
                    waited_time += wait_interval
                    print(f"等待中... ({waited_time}s/{max_wait_time}s)")
                
                # 等待图片出现
                await page.wait_for_timeout(3000)
                
                # 查找生成的图片
                img_selectors = [
                    'div.w-full.max-w-96.rounded-2xl img',
                    'img[alt*="生成"]',
                    'img[alt*="Generated"]',
                    'div.rounded-2xl img',
                    'div[class*="aspect-auto"] img'
                ]
                
                img_element = None
                for selector in img_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=10000)
                        img_elements = await page.query_selector_all(selector)
                        if img_elements:
                            img_element = img_elements[-1]  # 获取最新的图片
                            break
                    except:
                        continue
                
                if img_element:
                    img_url = await img_element.get_attribute('src')
                    
                    if img_url:
                        print(f"找到图片URL: {img_url}")
                        # 下载图片
                        return await self.download_image(img_url)
                    else:
                        print("未找到图片URL")
                        return None
                else:
                    print("未找到生成的图片")
                    return None
                    
            except Exception as e:
                print(f"生成图片时发生错误: {e}")
                return None
            finally:
                # 不关闭浏览器，保持会话
                pass
    
    async def download_image(self, url):
        """下载图片"""
        try:
            # 处理相对URL
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://bing.com' + url
            
            print(f"正在下载图片: {url}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            print(f"图片下载完成: {temp_path}")
            return temp_path
            
        except Exception as e:
            print(f"下载图片失败: {e}")
            return None
    def compose_card(self, card_data, ai_image_path):
        """合成最终卡牌（优化布局与融合效果）"""
        try:
            # 加载基础图片
            background = Image.open(os.path.join(self.base_img_path, "background.png"))
            title = Image.open(os.path.join(self.base_img_path, "title.png"))
            introduce = Image.open(os.path.join(self.base_img_path, "introduce.png"))
            
            # 加载AI生成的图片
            if ai_image_path and os.path.exists(ai_image_path):
                ai_image = Image.open(ai_image_path)
            else:
                print("AI图片不存在，跳过合成")
                return None
            final_card = background.copy()
            bg_width, bg_height = background.size
            title_width, title_height = title.size
            intro_width, intro_height = introduce.size            # 获取title的实际内容边界（去除透明部分）
            def get_content_bbox(img):
                """获取图片非透明内容的边界框"""
                if img.mode != 'RGBA':
                    return (0, 0, img.width, img.height)
                
                # 获取alpha通道
                alpha = img.split()[-1]
                bbox = alpha.getbbox()
                return bbox if bbox else (0, 0, img.width, img.height)
            
            title_content_bbox = get_content_bbox(title)
            title_content_width = title_content_bbox[2] - title_content_bbox[0]
            title_content_height = title_content_bbox[3] - title_content_bbox[1]
            
            # title位置：基于实际内容居中，再往下20px
            title_x = (bg_width - title_content_width) // 2 - title_content_bbox[0]
            title_y = 50  # 原30+20
            if title.mode == 'RGBA':
                final_card.paste(title, (title_x, title_y), title)
            else:
                final_card.paste(title, (title_x, title_y))

            # AI图片处理：两步缩放 - 先缩小40px，再精确定位
            # 第一步：缩小40px（等比例）
            original_width, original_height = ai_image.size
            first_target_width = original_width - 40
            first_target_height = original_height - 40
            ai_image_first_scale = ai_image.resize((first_target_width, first_target_height), Image.Resampling.LANCZOS)
              # 第二步：适应卡牌大小，去除左右多余像素
            available_width = bg_width - 6  # 左右各留3px
            if first_target_width > available_width:
                scale = available_width / first_target_width
                second_target_width = available_width
                second_target_height = int(first_target_height * scale)
                ai_image_second_scale = ai_image_first_scale.resize((second_target_width, second_target_height), Image.Resampling.LANCZOS)
            else:
                ai_image_second_scale = ai_image_first_scale
                second_target_width = first_target_width
                second_target_height = first_target_height
              # 第三步：再缩小10%
            final_target_width = int(second_target_width * 0.9)
            final_target_height = int(second_target_height * 0.9)
            ai_image_resized = ai_image_second_scale.resize((final_target_width, final_target_height), Image.Resampling.LANCZOS)
            
            # 第四步：左右各削掉5px
            crop_width = final_target_width - 10  # 左右各去5px
            crop_left = 5
            ai_image_cropped = ai_image_resized.crop((crop_left, 0, crop_left + crop_width, final_target_height))
            
            # 添加轻微高斯模糊
            ai_image_blurred = ai_image_cropped.filter(ImageFilter.GaussianBlur(radius=0.8))
              # 居中定位（准备渐变粘贴）
            ai_x = (bg_width - crop_width) // 2
            ai_y = title_y + title_height + 20
            # 注意：AI图片不在这里直接粘贴，而是通过下面的渐变融合方式

            # introduce粘贴
            intro_x = (bg_width - intro_width) // 2
            intro_y = bg_height - intro_height - 20
            if introduce.mode == 'RGBA':
                final_card.paste(introduce, (intro_x, intro_y), introduce)
            else:
                final_card.paste(introduce, (intro_x, intro_y))            # --- 创建平滑的渐变融合效果：消除割裂感 ---
            # 不再使用模糊带，而是使用alpha渐变来实现平滑融合
            
            # 先移除AI图片的直接粘贴，改为分段渐变粘贴
            fade_height = 20  # 渐变区域高度
            
            # 1. 粘贴AI图片的中间主体部分（非渐变区域）
            middle_start = fade_height
            middle_end = final_target_height - fade_height
            if middle_end > middle_start:
                middle_section = ai_image_blurred.crop((0, middle_start, crop_width, middle_end))
                final_card.paste(middle_section, (ai_x, ai_y + middle_start))
            
            # 2. 创建上边缘渐变融合（从透明到不透明）
            for i in range(fade_height):
                # alpha值从0（透明）渐变到255（不透明）
                alpha = int(255 * (i / (fade_height - 1)))
                
                # 提取AI图片的一行像素
                line = ai_image_blurred.crop((0, i, crop_width, i + 1))
                
                # 创建渐变alpha遮罩
                mask = Image.new('L', (crop_width, 1), alpha)
                
                # 应用alpha遮罩并粘贴
                final_card.paste(line, (ai_x, ai_y + i), mask)
            
            # 3. 创建下边缘渐变融合（从不透明到透明）
            for i in range(fade_height):
                # alpha值从255（不透明）渐变到0（透明）
                alpha = int(255 * ((fade_height - 1 - i) / (fade_height - 1)))
                
                # 提取AI图片底部的一行像素
                source_y = final_target_height - fade_height + i
                line = ai_image_blurred.crop((0, source_y, crop_width, source_y + 1))
                
                # 创建渐变alpha遮罩
                mask = Image.new('L', (crop_width, 1), alpha)
                
                # 应用alpha遮罩并粘贴
                final_card.paste(line, (ai_x, ai_y + source_y), mask)

            # --- 文字 ---
            draw = ImageDraw.Draw(final_card)
            # 字体更大
            try:
                font_title = ImageFont.truetype("simhei.ttf", 44)
                font_desc = ImageFont.truetype("simhei.ttf", 28)
            except:
                try:
                    font_title = ImageFont.truetype("arial.ttf", 44)
                    font_desc = ImageFont.truetype("arial.ttf", 28)
                except:
                    font_title = ImageFont.load_default()
                    font_desc = ImageFont.load_default()            # 卡牌名称完全居中title的实际内容区域
            card_name = card_data.get('card_name', '')
            name_bbox = draw.textbbox((0, 0), card_name, font=font_title)
            name_width = name_bbox[2] - name_bbox[0]
            name_height = name_bbox[3] - name_bbox[1]
            
            # 基于title实际内容区域居中
            title_content_center_x = title_x + title_content_bbox[0] + title_content_width // 2
            title_content_center_y = title_y + title_content_bbox[1] + title_content_height // 2
            
            name_x = title_content_center_x - name_width // 2
            name_y = title_content_center_y - name_height // 2
            
            draw.text((name_x, name_y), card_name, fill='white', font=font_title)
            # 描述文字更大，完全居中introduce区域
            description = card_data.get('description', '')
            max_chars_per_line = 13
            lines = [description[i:i+max_chars_per_line] for i in range(0, len(description), max_chars_per_line)]
            line_height = font_desc.size + 8
            total_text_height = len(lines) * line_height
            start_y = intro_y + (intro_height - total_text_height) // 2
            for i, line in enumerate(lines):
                line_bbox = draw.textbbox((0, 0), line, font=font_desc)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = intro_x + (intro_width - line_width) // 2
                line_y = start_y + i * line_height
                draw.text((line_x, line_y), line, fill='white', font=font_desc)
            return final_card
        except Exception as e:
            print(f"合成卡牌失败: {e}")
            return None
    
    async def generate_single_card(self, card_data):
        """生成单张卡牌"""
        card_name = card_data.get('card_name', 'unknown')
        ai_prompt = card_data.get('ai_prompt', '')
        
        print(f"\n开始生成卡牌: {card_name}")
        
        # 生成AI图片
        ai_image_path = await self.generate_ai_image(ai_prompt)
        
        if ai_image_path:
            # 合成最终卡牌
            final_card = self.compose_card(card_data, ai_image_path)
            
            if final_card:
                # 保存卡牌
                output_filename = f"{card_name}.png"
                output_path = os.path.join(self.output_path, output_filename)
                final_card.save(output_path, 'PNG')
                print(f"卡牌生成完成: {output_path}")
                
                # 清理临时文件
                try:
                    os.unlink(ai_image_path)
                except:
                    pass
                
                return output_path
            else:
                print(f"卡牌 {card_name} 合成失败")
        else:
            print(f"卡牌 {card_name} AI图片生成失败")
        
        return None
    
    async def generate_all_cards(self):
        """生成所有卡牌"""
        cards_data = self.load_cards_config()
        
        if not cards_data:
            print("未找到卡牌配置数据")
            return
        
        print(f"共找到 {len(cards_data)} 张卡牌需要生成")
        
        success_count = 0
        
        for i, card_data in enumerate(cards_data, 1):
            print(f"\n进度: {i}/{len(cards_data)}")
            
            result = await self.generate_single_card(card_data)
            if result:
                success_count += 1
            
            # 添加延迟，避免请求过快
            if i < len(cards_data):
                print("等待5秒后继续...")
                await asyncio.sleep(5)
        
        print(f"\n生成完成！成功生成 {success_count}/{len(cards_data)} 张卡牌")

async def main():
    generator = CardGenerator()
    await generator.generate_all_cards()

if __name__ == "__main__":
    asyncio.run(main())
