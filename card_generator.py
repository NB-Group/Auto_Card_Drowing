import json
import asyncio
import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import tempfile

class ColorLogger:
    """炫酷的彩色日志输出类"""
    
    # ANSI颜色代码
    COLORS = {
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'END': '\033[0m'
    }
    
    @classmethod
    def _print_colored(cls, message, color='WHITE', style=''):
        """打印彩色文本"""
        color_code = cls.COLORS.get(color.upper(), cls.COLORS['WHITE'])
        style_code = cls.COLORS.get(style.upper(), '')
        print(f"{style_code}{color_code}{message}{cls.COLORS['END']}")
    
    @classmethod
    def success(cls, message):
        """成功信息 - 绿色"""
        cls._print_colored(f"✅ {message}", 'GREEN', 'BOLD')
    
    @classmethod
    def error(cls, message):
        """错误信息 - 红色"""
        cls._print_colored(f"❌ {message}", 'RED', 'BOLD')
    
    @classmethod
    def warning(cls, message):
        """警告信息 - 黄色"""
        cls._print_colored(f"⚠️  {message}", 'YELLOW', 'BOLD')
    
    @classmethod
    def info(cls, message):
        """信息 - 蓝色"""
        cls._print_colored(f"ℹ️  {message}", 'BLUE')
    
    @classmethod
    def progress(cls, message):
        """进度信息 - 青色"""
        cls._print_colored(f"🚀 {message}", 'CYAN', 'BOLD')
    
    @classmethod
    def generating(cls, message):
        """生成中 - 洋红色"""
        cls._print_colored(f"🎨 {message}", 'MAGENTA', 'BOLD')
    
    @classmethod
    def download(cls, message):
        """下载信息 - 绿色"""
        cls._print_colored(f"📥 {message}", 'GREEN')
    
    @classmethod
    def compose(cls, message):
        """合成信息 - 黄色"""
        cls._print_colored(f"🔧 {message}", 'YELLOW')
    
    @classmethod
    def header(cls, message):
        """标题 - 粗体白色"""
        cls._print_colored(f"\n{'='*50}", 'CYAN')
        cls._print_colored(f"🌟 {message}", 'WHITE', 'BOLD')
        cls._print_colored(f"{'='*50}", 'CYAN')
    
    @classmethod
    def progress_bar(cls, current, total, prefix="", suffix="", length=30):
        """炫酷进度条"""
        percent = int(100 * (current / total))
        filled_length = int(length * current // total)
        
        # 创建进度条
        bar_filled = '█' * filled_length
        bar_empty = '░' * (length - filled_length)
        bar = f"[{bar_filled}{bar_empty}]"
        
        # 创建彩色输出
        color_code = cls.COLORS['CYAN']
        bold_code = cls.COLORS['BOLD']
        end_code = cls.COLORS['END']
        
        # 使用\r实现同行覆盖
        progress_line = f"\r{bold_code}{color_code}🚀 {prefix} {bar} {percent}% {suffix}{end_code}"
        print(progress_line, end='', flush=True)

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
                cards_data = json.load(f)
                ColorLogger.success(f"成功加载 {len(cards_data)} 张卡牌配置")
                return cards_data
        except Exception as e:
            ColorLogger.error(f"读取配置文件失败: {e}")
            return []
    
    async def save_cookies(self, context):
        """保存cookies"""
        try:
            cookies = await context.cookies()
            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            ColorLogger.success("Cookies已保存")
        except Exception as e:
            ColorLogger.error(f"保存Cookies失败: {e}")
    async def load_cookies(self, context):
        """加载cookies"""
        try:
            if os.path.exists(self.cookies_path):
                with open(self.cookies_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                ColorLogger.success("Cookies已加载")
                return True
        except Exception as e:
            ColorLogger.error(f"加载Cookies失败: {e}")
        return False
    
    async def generate_ai_image(self, prompt):
        """使用Playwright生成AI图片"""
        # 添加总体提示词前缀
        base_prompt = "写实融合国风插画风格（参考《清明上河图》的精致线条感与《鬼谷八荒》的色彩层次）。整体色调偏复古，低饱和度，背景带有米黄羊皮纸质感。图片长宽比注意只能是1比1。生成字时请使用标准正楷字。"
        full_prompt = base_prompt + " " + prompt
        
        ColorLogger.generating(f"正在生成AI图片...")
        ColorLogger.info(f"提示词: {prompt}")
        
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
                    ColorLogger.info("导航到Copilot网站...")
                    await page.goto("https://copilot.microsoft.com", timeout=60000)
                    # 等待页面加载
                    await page.wait_for_timeout(3000)
                
                # 检查是否需要登录
                try:
                    # 查找登录按钮或用户头像来判断登录状态
                    login_button = await page.query_selector('button[data-testid="sign-in-button"]')
                    if login_button:
                        ColorLogger.warning("检测到未登录状态，请在浏览器中登录...")
                        ColorLogger.warning("登录完成后，按回车键继续...")
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
                        ColorLogger.error("未找到输入框，请检查页面状态")
                        return None
                  # 清空输入框并输入新提示词
                await page.fill(input_selector, "")
                await page.type(input_selector, full_prompt, delay=50)
                
                # 发送消息
                await page.keyboard.press('Enter')
                
                # 等待生成开始 - 检查是否有生成指示器
                ColorLogger.progress("等待AI开始生成...")
                try:
                    await page.wait_for_selector('.size-3\\.5.rounded.bg-salmon-550', timeout=10000)
                    ColorLogger.generating("检测到AI正在生成中...")
                except:
                    ColorLogger.info("未检测到生成指示器，继续等待...")
                
                # 等待生成完成 - 生成指示器消失
                max_wait_time = 120  # 最多等待2分钟
                wait_interval = 2
                waited_time = 0
                
                # 显示初始进度条
                ColorLogger.progress_bar(0, max_wait_time, prefix="生成中...", suffix=f"(0s/{max_wait_time}s)")
                
                while waited_time < max_wait_time:
                    try:
                        # 检查是否还在生成
                        generating_indicator = await page.query_selector('.size-3\\.5.rounded.bg-salmon-550')
                        if not generating_indicator:
                            ColorLogger.progress_bar(waited_time, max_wait_time, prefix="生成完成", suffix=f"({waited_time}s/{max_wait_time}s)")
                            print()  # 换行
                            ColorLogger.success("AI生成完成！")
                            break
                    except:
                        pass
                    
                    await page.wait_for_timeout(wait_interval * 1000)
                    waited_time += wait_interval
                    ColorLogger.progress_bar(waited_time, max_wait_time, prefix="生成中...", suffix=f"({waited_time}s/{max_wait_time}s)")
                
                # 如果超时，也要换行
                if waited_time >= max_wait_time:
                    print()  # 换行
                    ColorLogger.warning("等待超时，但继续尝试查找图片...")
                
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
                        ColorLogger.success(f"找到图片URL！")
                        # 下载图片
                        return await self.download_image(img_url)
                    else:
                        ColorLogger.error("未找到图片URL")
                        return None
                else:
                    ColorLogger.error("未找到生成的图片")
                    return None
                    
            except Exception as e:
                ColorLogger.error(f"生成图片时发生错误: {e}")
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
            
            ColorLogger.download("正在下载图片...")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            ColorLogger.success(f"图片下载完成")
            return temp_path
            
        except Exception as e:
            ColorLogger.error(f"下载图片失败: {e}")
            return None
    def compose_card(self, card_data, ai_image_path):
        """合成最终卡牌（优化布局与融合效果）"""
        try:
            ColorLogger.compose("开始合成卡牌...")
            
            # 加载基础图片
            background = Image.open(os.path.join(self.base_img_path, "background.png"))
            title = Image.open(os.path.join(self.base_img_path, "title.png"))
            introduce = Image.open(os.path.join(self.base_img_path, "introduce.png"))
            
            # 加载AI生成的图片
            if ai_image_path and os.path.exists(ai_image_path):
                ai_image = Image.open(ai_image_path)
                ColorLogger.success("AI图片加载成功")
            else:
                ColorLogger.error("AI图片不存在，跳过合成")
                return None
            final_card = background.copy()
            bg_width, bg_height = background.size
            title_width, title_height = title.size
            intro_width, intro_height = introduce.size            
            
            # 获取title的实际内容边界（去除透明部分）
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

            ColorLogger.compose("处理AI图片尺寸...")
            
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
                final_card.paste(introduce, (intro_x, intro_y))            
                
            ColorLogger.compose("应用渐变融合效果...")
            
            # --- 创建平滑的渐变融合效果：消除割裂感 ---
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

            ColorLogger.compose("添加文字信息...")
            
            # --- 文字 ---
            draw = ImageDraw.Draw(final_card)
            # 字体更大
            try:
                font_title = ImageFont.truetype("simhei.ttf", 44)
                font_desc = ImageFont.truetype("simhei.ttf", 24)  # 稍微小一点，为了更好布局
                # 尝试加载支持emoji的字体
                try:
                    font_emoji = ImageFont.truetype("seguiemj.ttf", 40)  # Windows emoji字体
                except:
                    try:
                        font_emoji = ImageFont.truetype("NotoColorEmoji.ttf", 40)  # Linux emoji字体
                    except:
                        font_emoji = font_title  # 回退到标题字体
            except:
                try:
                    font_title = ImageFont.truetype("arial.ttf", 44)
                    font_desc = ImageFont.truetype("arial.ttf", 24)
                    font_emoji = font_title
                except:
                    font_title = ImageFont.load_default()
                    font_desc = ImageFont.load_default()
                    font_emoji = font_title

            # 卡牌类型emoji映射
            card_type_emojis = {
                "国家卡": "🏰",
                "思想卡": "🧠", 
                "变法卡": "⚖️",
                "连锁卡": "🔗",
                "军事卡": "⚔️",
                "经济卡": "💰",
                "道具卡": "🎁",
                "锦囊牌": "📜",
                "祭祀卡": "🙏"
            }
            
            # 获取卡牌类型和对应emoji
            card_group = card_data.get('card_group', '')
            emoji = card_type_emojis.get(card_group, '')
            
            # 根据卡牌主题色确定emoji颜色
            color_theme = card_data.get('color_theme', '')
            emoji_color = 'white'  # 默认白色
            
            # 根据主题色设置深色调emoji颜色
            if '黑金' in color_theme or '墨' in color_theme:
                emoji_color = '#D4AF37'  # 深金色
            elif '深红' in color_theme or '红' in color_theme:
                emoji_color = '#8B0000'  # 深红色
            elif '蓝' in color_theme:
                emoji_color = '#000080'  # 深蓝色
            elif '银' in color_theme or '灰' in color_theme:
                emoji_color = '#696969'  # 深灰色
            elif '紫' in color_theme:
                emoji_color = '#4B0082'  # 深紫色
            elif '绿' in color_theme:
                emoji_color = '#006400'  # 深绿色
            elif '橙' in color_theme:
                emoji_color = '#FF4500'  # 深橙色
            elif '古铜' in color_theme or '褐' in color_theme:
                emoji_color = '#8B4513'  # 深棕色
            elif '青' in color_theme:
                emoji_color = '#008B8B'  # 深青色
            elif '黄' in color_theme:
                emoji_color = '#DAA520'  # 深金黄色
            else:
                emoji_color = '#8B4513'  # 默认深棕色
            
            # 卡牌名称完全居中title的实际内容区域
            card_name = card_data.get('card_name', '')
            
            # 基于title实际内容区域居中
            title_content_center_x = title_x + title_content_bbox[0] + title_content_width // 2
            title_content_center_y = title_y + title_content_bbox[1] + title_content_height // 2
            
            # 先绘制卡牌名称
            name_bbox = draw.textbbox((0, 0), card_name, font=font_title)
            name_width = name_bbox[2] - name_bbox[0]
            name_height = name_bbox[3] - name_bbox[1]
            
            # 如果有emoji，需要计算总宽度
            if emoji:
                emoji_bbox = draw.textbbox((0, 0), emoji, font=font_emoji)
                emoji_width = emoji_bbox[2] - emoji_bbox[0]
                emoji_height = emoji_bbox[3] - emoji_bbox[1]
                total_width = name_width + emoji_width + 10  # 名称+间距+emoji
                
                # 居中计算起始位置
                start_x = title_content_center_x - total_width // 2
                name_y = title_content_center_y - name_height // 2
                
                # 绘制卡牌名称
                draw.text((start_x, name_y), card_name, fill='white', font=font_title)
                
                # 绘制emoji（与文字基线对齐，使用主题色）
                emoji_x = start_x + name_width + 10
                # 计算emoji的垂直对齐位置，让它与文字基线对齐
                emoji_y = name_y + (name_height - emoji_height) // 2
                draw.text((emoji_x, emoji_y), emoji, fill=emoji_color, font=font_emoji)
                
                ColorLogger.compose(f"添加卡牌标题: {card_name} {emoji} (颜色: {emoji_color})")
            else:
                # 没有emoji，直接居中卡牌名称
                name_x = title_content_center_x - name_width // 2
                name_y = title_content_center_y - name_height // 2
                draw.text((name_x, name_y), card_name, fill='white', font=font_title)
                ColorLogger.compose(f"添加卡牌标题: {card_name}")
            
            # --- 优化底栏描述文字布局 ---
            description = card_data.get('description', '')
            
            # 计算可用区域（大幅增加左右边距）
            text_margin = 35  # 大幅增加左右边距到35px
            available_text_width = intro_width - (text_margin * 2)
            
            ColorLogger.compose(f"底栏可用宽度: {available_text_width}px (总宽度: {intro_width}px, 边距: {text_margin}px)")
            
            # 智能换行 - 根据可用宽度计算
            def smart_wrap_text(text, font, max_width):
                """智能文字换行"""
                lines = []
                current_line = ""
                
                for char in text:
                    test_line = current_line + char
                    text_bbox = draw.textbbox((0, 0), test_line, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    
                    if text_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                            current_line = char
                        else:
                            lines.append(char)  # 单个字符也太宽的情况
                
                if current_line:
                    lines.append(current_line)
                
                return lines
            
            # 使用智能换行
            lines = smart_wrap_text(description, font_desc, available_text_width)
            
            # 计算行高和总高度
            line_height = font_desc.size + 6  # 行间距稍微小一点
            total_text_height = len(lines) * line_height - 6  # 最后一行不需要额外间距
            
            # 垂直居中
            start_y = intro_y + (intro_height - total_text_height) // 2
            
            # 绘制每一行文字
            for i, line in enumerate(lines):
                # 计算每行的位置，确保有左右边距
                line_bbox = draw.textbbox((0, 0), line, font=font_desc)
                line_width = line_bbox[2] - line_bbox[0]
                
                # 在有边距的区域内居中
                available_x_start = intro_x + text_margin
                available_x_width = intro_width - (text_margin * 2)
                line_x = available_x_start + (available_x_width - line_width) // 2
                
                ColorLogger.compose(f"第{i+1}行文字位置: x={line_x}, 宽度={line_width}, 边距区域={available_x_start}-{available_x_start + available_x_width}")
                
                # 确保不超出边界（双重保护）
                if line_x < intro_x + text_margin:
                    line_x = intro_x + text_margin
                    ColorLogger.warning(f"第{i+1}行文字超出左边界，调整到: {line_x}")
                elif line_x + line_width > intro_x + intro_width - text_margin:
                    line_x = intro_x + intro_width - text_margin - line_width
                    ColorLogger.warning(f"第{i+1}行文字超出右边界，调整到: {line_x}")
                
                line_y = start_y + i * line_height
                draw.text((line_x, line_y), line, fill='white', font=font_desc)
            
            ColorLogger.success("卡牌合成完成！")
            return final_card
        except Exception as e:
            ColorLogger.error(f"合成卡牌失败: {e}")
            return None
    
    async def generate_single_card(self, card_data):
        """生成单张卡牌"""
        card_name = card_data.get('card_name', 'unknown')
        ai_prompt = card_data.get('ai_prompt', '')
        
        ColorLogger.header(f"开始生成卡牌: {card_name}")
        
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
                ColorLogger.success(f"卡牌生成完成: {output_path}")
                
                # 清理临时文件
                try:
                    os.unlink(ai_image_path)
                    ColorLogger.info("临时文件已清理")
                except:
                    pass
                
                return output_path
            else:
                ColorLogger.error(f"卡牌 {card_name} 合成失败")
        else:
            ColorLogger.error(f"卡牌 {card_name} AI图片生成失败")
        
        return None
    
    async def generate_all_cards(self):
        """生成所有卡牌"""
        ColorLogger.header("春秋杀卡牌生成器 - 启动")
        
        cards_data = self.load_cards_config()
        
        if not cards_data:
            ColorLogger.error("未找到卡牌配置数据")
            return
        
        ColorLogger.progress(f"共找到 {len(cards_data)} 张卡牌需要生成")
        
        success_count = 0
        
        for i, card_data in enumerate(cards_data, 1):
            ColorLogger.progress(f"\n=== 进度: {i}/{len(cards_data)} ===")
            
            result = await self.generate_single_card(card_data)
            if result:
                success_count += 1
            
            # 添加延迟，避免请求过快
            if i < len(cards_data):
                ColorLogger.info("等待5秒后继续...")
                # 使用进度条显示等待过程
                wait_time = 5
                for second in range(wait_time + 1):
                    ColorLogger.progress_bar(second, wait_time, prefix="等待中...", suffix=f"({second}s/{wait_time}s)")
                    if second < wait_time:
                        await asyncio.sleep(1)
                print()  # 换行
        
        ColorLogger.header(f"生成完成！成功生成 {success_count}/{len(cards_data)} 张卡牌")

async def main():
    generator = CardGenerator()
    await generator.generate_all_cards()

if __name__ == "__main__":
    asyncio.run(main())
