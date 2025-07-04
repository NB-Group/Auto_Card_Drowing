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
                max_wait_time = 1000  # 最多等待2分钟
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
            
            # AI图片处理：进一步缩小尺寸，避免图片过大
            original_width, original_height = ai_image.size
            
            # 计算合适的尺寸：适应卡牌宽度，左侧收窄3px
            available_width = bg_width - 85  # 左边距44px，右边距41px
            
            if original_width > available_width:
                # 需要缩放以适应宽度
                scale = available_width / original_width
                final_target_width = available_width
                final_target_height = int(original_height * scale)
                ai_image_resized = ai_image.resize((final_target_width, final_target_height), Image.Resampling.LANCZOS)
                crop_width = final_target_width
            else:
                # 原图已经够小，缩小更多
                final_target_width = int(original_width * 0.75)  # 缩小到75%
                final_target_height = int(original_height * 0.75)
                ai_image_resized = ai_image.resize((final_target_width, final_target_height), Image.Resampling.LANCZOS)
                crop_width = final_target_width
            
            # 无需额外裁剪，直接使用处理后的图片
            ai_image_cropped = ai_image_resized
            
            # 添加轻微高斯模糊
            ai_image_blurred = ai_image_cropped.filter(ImageFilter.GaussianBlur(radius=0.8))
              
            # 向右偏移定位（准备渐变粘贴）
            ai_x = (bg_width - crop_width) // 2 + 3  # 向右偏移3px
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
            
            # 根据卡牌主题色确定emoji颜色（使用更和谐的颜色）
            color_theme = card_data.get('color_theme', '')
            
            # 使用更温和、更协调的颜色方案
            if '黑金' in color_theme or '墨' in color_theme:
                emoji_color = '#FFD700'  # 亮金色
            elif '深红' in color_theme or '红' in color_theme:
                emoji_color = '#DC143C'  # 猩红色
            elif '蓝' in color_theme:
                emoji_color = '#4169E1'  # 皇家蓝
            elif '银' in color_theme or '灰' in color_theme:
                emoji_color = '#C0C0C0'  # 银色
            elif '紫' in color_theme:
                emoji_color = '#9370DB'  # 中紫色
            elif '绿' in color_theme:
                emoji_color = '#32CD32'  # 柠檬绿
            elif '橙' in color_theme:
                emoji_color = '#FF8C00'  # 暗橙色
            elif '古铜' in color_theme or '褐' in color_theme:
                emoji_color = '#CD853F'  # 秘鲁色
            elif '青' in color_theme:
                emoji_color = '#40E0D0'  # 绿松石色
            elif '黄' in color_theme:
                emoji_color = '#FFD700'  # 金色
            else:
                emoji_color = '#F0E68C'  # 卡其色（温和的默认色）
            
            # 卡牌名称和图标布局优化
            card_name = card_data.get('card_name', '')
            
            # 基于title实际内容区域的中心点
            title_content_center_x = title_x + title_content_bbox[0] + title_content_width // 2
            title_content_center_y = title_y + title_content_bbox[1] + title_content_height // 2
            
            # 计算文字尺寸
            name_bbox = draw.textbbox((0, 0), card_name, font=font_title)
            name_width = name_bbox[2] - name_bbox[0]
            name_height = name_bbox[3] - name_bbox[1]
            
            # 文字完全居中
            name_x = title_content_center_x - name_width // 2
            name_y = title_content_center_y - name_height // 2
            
            # 绘制卡牌名称（先绘制文字）
            draw.text((name_x, name_y), card_name, fill='white', font=font_title)
            
            # 如果有emoji，在文字右边绘制
            if emoji:
                emoji_bbox = draw.textbbox((0, 0), emoji, font=font_emoji)
                emoji_width = emoji_bbox[2] - emoji_bbox[0]
                emoji_height = emoji_bbox[3] - emoji_bbox[1]
                
                # emoji位置：文字右边 + 间距
                emoji_spacing = 15  # 增加间距避免重叠
                emoji_x = name_x + name_width + emoji_spacing
                
                # emoji垂直居中对齐（手动添加偏移量调整居中）
                emoji_y_offset = 10  # 手动偏移量，向下调整17像素
                emoji_y = title_content_center_y - emoji_height // 2 + emoji_y_offset
                
                # 绘制emoji
                draw.text((emoji_x, emoji_y), emoji, fill=emoji_color, font=font_emoji)
                
                ColorLogger.compose(f"添加卡牌标题: {card_name} {emoji} (颜色: {emoji_color})")
                ColorLogger.compose(f"布局 - 文字位置: ({name_x}, {name_y}), emoji位置: ({emoji_x}, {emoji_y}) [向下偏移: {emoji_y_offset}px]")
                ColorLogger.compose(f"主图位置: ai_x={ai_x} (右偏移3px), 边距: 左44px右41px")
            else:
                ColorLogger.compose(f"添加卡牌标题: {card_name}")
                ColorLogger.compose(f"布局 - 文字位置: ({name_x}, {name_y})")
                ColorLogger.compose(f"主图位置: ai_x={ai_x} (右偏移3px), 边距: 左44px右41px")
            
            # --- 优化底栏描述文字布局 ---
            description = card_data.get('description', '')
            
            # 计算可用区域（大幅增加左右边距）
            text_margin = 35  # 大幅增加左右边距到35px
            available_text_width = intro_width - (text_margin * 2)
            
            ColorLogger.compose(f"底栏可用宽度: {available_text_width}px (总宽度: {intro_width}px, 边距: {text_margin}px)")
            
            # 智能换行
            def smart_wrap_text(text, font, max_width):
                """更智能的文本换行，正确处理中英文"""
                lines = []
                current_line = ""

                for char in text:
                    if font.getlength(current_line + char) <= max_width:
                        current_line += char
                    else:
                        lines.append(current_line)
                        current_line = char
                
                if current_line:
                    lines.append(current_line)
                
                # 获取字体高度
                try:
                    line_height = font.getbbox("A")[3]
                except AttributeError:
                    # 备用方案
                    line_height = font.getsize("A")[1]

                return lines, line_height

            # 根据计算出的可用宽度进行换行
            description_lines, line_height = smart_wrap_text(description, font_desc, available_text_width)
            
            # 计算文字总高度
            total_text_height = len(description_lines) * line_height + (len(description_lines) - 1) * line_height
            
            # 垂直居中
            start_y = intro_y + (intro_height - total_text_height) // 2
            
            # 绘制每一行文字
            for i, line in enumerate(description_lines):
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
        cards_to_generate = self.load_cards_config()
        if not cards_to_generate:
            ColorLogger.error("没有要生成的卡牌，程序退出")
            return

        # ================================================================
        # 设置从第几张卡牌开始生成（基于列表中的顺序，从1开始计数）
        # 修改此数字以从不同的卡牌开始，并会覆盖已生成的文件
        start_from_card = 12 
        # ================================================================
        
        total_cards = len(cards_to_generate)
        if start_from_card > total_cards:
            ColorLogger.error(f"起始卡牌号 ({start_from_card}) 大于总卡牌数 ({total_cards})，程序退出。")
            return

        ColorLogger.header(f"将从第 {start_from_card} 张卡牌开始覆盖生成，直到第 {total_cards} 张。")
        
        generated_count = 0
        
        # 使用1-based的索引来方便匹配 start_from_card
        for i, card_data in enumerate(cards_to_generate, 1):
            # 如果当前卡牌编号小于指定的起始编号，则跳过
            if i < start_from_card:
                continue

            card_name = card_data.get("card_name", f"未知卡牌_{i}")
            ColorLogger.header(f"正在处理卡牌 {i}/{total_cards}: {card_name}")

            try:
                await self.generate_single_card(card_data)
                generated_count += 1
                ColorLogger.success(f"成功生成或覆盖卡牌: {card_name}")
            except Exception as e:
                ColorLogger.error(f"生成卡牌 '{card_name}' 时发生错误: {e}")
                ColorLogger.warning("将在5秒后继续处理下一张卡牌...")
                await asyncio.sleep(5)
            
            # 计算并显示本次任务的进度
            cards_to_process_count = total_cards - start_from_card + 1
            current_card_in_task = i - start_from_card + 1
            ColorLogger.header(f"本次任务进度: {current_card_in_task}/{cards_to_process_count}")

        ColorLogger.header(f"生成完成！本次任务成功生成/覆盖 {generated_count} 张卡牌")

async def main():
    generator = CardGenerator()
    await generator.generate_all_cards()

if __name__ == "__main__":
    asyncio.run(main())
