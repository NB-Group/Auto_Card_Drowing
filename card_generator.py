import json
import asyncio
import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
import random
import math
from playwright.async_api import async_playwright
try:
    import torch  # type: ignore
    from modelscope import DiffusionPipeline  # type: ignore
    HAS_MODELSCOPE = True
except Exception as e:
    HAS_MODELSCOPE = False
    # 调试：打印导入失败的具体原因
    print(f"[DEBUG] Failed to import torch/diffusers. HAS_MODELSCOPE set to False. Error: {e}")
from urllib.parse import urlparse
import traceback
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

    def load_historical_characters(self):
        """读取历史人物数据"""
        config_path = os.path.join(self.base_path, "historical_characters.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)
                ColorLogger.success(f"成功加载历史人物数据")
                return characters_data
        except Exception as e:
            ColorLogger.error(f"读取历史人物数据失败: {e}")
            return []

    def generate_historical_card_data(self, character_data, country_name):
        """生成历史人物卡牌数据"""
        name = character_data['name']
        skill_name = character_data['skill_name']
        game_skill = character_data['game_skill']
        description = character_data['description']
        historical_source = character_data['historical_source']

        # 生成AI提示词（要求AI写字迹）
        ai_prompt = (
            f"水性马克笔手绘，稚嫩童趣的中国古风，低饱和复古配色。"
            f"一个战国时期的人物：{country_name}的{name}。"
            f"{'身穿黑色衣袍，' if country_name == '秦国' else ''}"
            f"头肩胸像，服饰考据，构图居中且偏下，人物和文字都往下移动，"
            f"确保文字完全在画面内，不超出任何边框。"
            f"背景简洁，米黄色纸张质感。"
            f"必须使用简体中文，更偏手写感的中文文字：字形略不规则、略有倾斜与连笔，"
            f"但整体工整可读，笔画偏粗，具有马克笔渗化与深浅不均的笔触效果；"
            f"与纸面自然融合，无水印无Logo。"
            f"画面上只有人物名称和技能名称，没有其他文字。"
            f"文字位置控制：所有文字必须在画面中央偏下区域，字体要适中，"
            f"上下留出充足边距，确保文字完全在安全区域内，不超出任何边框。"
            f"排版要求：人物头像和文字整体向下移动，顶部留白充足。"
            f"顶部大标题「{name}」（字体大小适中），"
            f"右侧竖排小标题：『{skill_name}』。"
        )

        # 卡牌数据结构
        card_data = {
            'card_group': '历史人物卡',
            'card_name': f"{country_name}-{name}",
            'color_theme': self.get_country_color_theme(country_name),
            'ai_prompt': ai_prompt,
            'description': f"{skill_name}\n{game_skill}\n{historical_source}",
            'price': '25历史币',
            'country': country_name,
            'character_name': name,
            'ai_writes_text': True  # AI生成字迹
        }

        return card_data

    def get_country_color_theme(self, country_name):
        """根据国家名称获取对应的颜色主题"""
        color_themes = {
            '韩国': '橙金',
            '赵国': '紫金',
            '魏国': '绿金',
            '楚国': '深红金',
            '燕国': '银黑',
            '齐国': '蓝金',
            '秦国': '黑金'
        }
        return color_themes.get(country_name, '墨青金属银')
    
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
    
    async def generate_ai_image_with_reference(self, prompt, reference_image_path):
        """使用参考图片生成AI图片（将图片路径文本直接输入，不弹文件选择器）"""
        ColorLogger.generating("正在生成AI图片（参考图片风格）...")
        ColorLogger.info(f"提示词: {prompt}")
        ColorLogger.info(f"参考图片: {reference_image_path}")

        async with async_playwright() as p:
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
                page = browser.pages[0] if len(browser.pages) else await browser.new_page()

                current_url = page.url
                if 'copilot.microsoft.com' not in current_url:
                    ColorLogger.info("导航到Copilot网站...")
                    await page.goto("https://copilot.microsoft.com", timeout=60000)
                    await page.wait_for_timeout(3000)

                # 登录检测（非阻塞）
                try:
                    login_button = await page.query_selector('button[data-testid="sign-in-button"]')
                    if login_button:
                        ColorLogger.warning("检测到未登录状态，请在浏览器中登录后继续...")
                except:
                    pass

                await page.wait_for_timeout(2000)

                # 输入框
                input_selector = 'textarea[data-testid="composer-input"]'
                try:
                    await page.wait_for_selector(input_selector, timeout=30000)
                except:
                    alternatives = [
                        'textarea[placeholder*="消息"]',
                        'textarea[placeholder*="Message"]',
                        'textarea#userInput',
                        'textarea[role="textbox"]'
                    ]
                    for sel in alternatives:
                        try:
                            await page.wait_for_selector(sel, timeout=5000)
                            input_selector = sel
                            break
                        except:
                            continue
                    else:
                        ColorLogger.error("未找到输入框，请检查页面状态")
                        return None

                # 先点击“+”按钮打开附件菜单 — 使用一组备选选择器以提高兼容性
                try:
                    plus_selectors = [
                        'button[data-testid="plus-button"]',
                        'button[aria-label*="添加"]',
                        'button[title*="添加"]',
                        'button:has(svg[mask*="plus"])',
                        'div[role="button"][data-testid="plus-button"]',
                        # 匹配用户提供的自定义片段 — 查找包含 paperclip 图标或相关 mask-image 的容器
                        'div[style*="paperclip-CMVChwA7.svg"]',
                        'div[style*="/static/cmc/assets/paperclip-CMVChwA7.svg"]',
                        'div[class*="paperclip"]',
                        'div[role="button"][class*="add"]',
                    ]

                    plus_btn = None
                    for sel in plus_selectors:
                        try:
                            plus_btn = await page.wait_for_selector(sel, timeout=2000)
                            if plus_btn:
                                ColorLogger.info(f"找到加号按钮选择器: {sel}")
                                await plus_btn.click()
                                break
                        except Exception:
                            continue

                    if not plus_btn:
                        ColorLogger.warning("未能找到或点击加号按钮（尝试了多种选择器）")
                except Exception as e:
                    ColorLogger.warning(f"点击加号按钮时发生异常: {e}")

                # 点击“上传”按钮，弹出文件选择器并选择图片
                try:
                    # 上传按钮也使用多候选选择器
                    upload_selectors = [
                        'button[data-testid="file-upload-button"]',
                        'input[type="file"]',
                        'button[aria-label*="上传"]',
                        'button[title*="上传"]',
                        'div[role="button"] input[type="file"]',
                        'div[style*="paperclip-CMVChwA7.svg"] input[type="file"]',
                    ]

                    upload_btn = None
                    file_chooser = None
                    for sel in upload_selectors:
                        try:
                            # 如果是直接的 input[type=file]，直接设置 files
                            if sel == 'input[type="file"]' or sel.endswith('input[type="file"]'):
                                input_el = await page.query_selector(sel)
                                if input_el:
                                    abs_path = os.path.abspath(reference_image_path)
                                    await input_el.set_input_files(abs_path)
                                    upload_done = True
                                    ColorLogger.success("已通过 input[type=file] 上传参考图片")
                                    break
                            # 其它情况尝试通过点击触发文件选择器
                            upload_btn = await page.wait_for_selector(sel, timeout=2000)
                            if upload_btn:
                                async with page.expect_file_chooser() as fc_info:
                                    await upload_btn.click()
                                file_chooser = await fc_info.value
                                abs_path = os.path.abspath(reference_image_path)
                                await file_chooser.set_files(abs_path)
                                ColorLogger.success("已通过菜单上传参考图片")
                                break
                        except Exception:
                            continue

                    if not upload_btn and not file_chooser:
                        ColorLogger.warning("未能找到上传控件，上传操作可能失败")
                    # 等待上传完成：先检查上传中的SVG动画，待其消失；或检测到本地blob缩略图
                    await page.wait_for_timeout(500)
                    upload_done = False
                    # 1) 若出现上传动画SVG（典型的 lottie 进度圈），等其消失
                    try:
                        # 先尝试检测动画出现
                        await page.wait_for_selector('svg[viewBox="0 0 800 800"]', timeout=2000)
                        # 再等待动画消失（上传完成）
                        await page.wait_for_selector('svg[viewBox="0 0 800 800"]', state='detached', timeout=20000)
                        upload_done = True
                    except:
                        pass
                    # 2) 或者识别到已附加的blob缩略图
                    if not upload_done:
                        for sel in ['img[src^="blob:"]', 'div [src^="blob:"]', 'div[role="img"][style*="blob:"]']:
                            try:
                                await page.wait_for_selector(sel, timeout=4000)
                                upload_done = True
                                break
                            except:
                                continue
                    # 3) 兜底再等一会
                    if not upload_done:
                        await page.wait_for_timeout(1500)
                except Exception as e:
                    ColorLogger.warning(f"通过菜单上传失败: {e}")

                # 清空并输入提示词（不再加入@文件名，由上传图片承担风格参考）
                await page.fill(input_selector, "")
                base_text = "请模仿刚上传图片的风格，使用长方形（3:4）构图。"
                # 用fill一次性填入，避免\n触发即时发送
                await page.fill(input_selector, base_text + " " + prompt)

                # 发送
                await page.keyboard.press('Enter')

                # 等待生成
                ColorLogger.progress("等待AI开始生成...")
                try:
                    await page.wait_for_selector('button[data-testid="stop-button"]', timeout=10000)
                    ColorLogger.generating("检测到AI正在生成中...")
                except:
                    ColorLogger.info("未检测到生成指示器，继续等待...")

                max_wait_time = 1000
                wait_interval = 2
                waited_time = 0
                ColorLogger.progress_bar(0, max_wait_time, prefix="生成中...", suffix=f"(0s/{max_wait_time}s)")
                while waited_time < max_wait_time:
                    try:
                        indicator = await page.query_selector('button[data-testid="stop-button"]')
                        if not indicator:
                            ColorLogger.progress_bar(waited_time, max_wait_time, prefix="生成完成", suffix=f"({waited_time}s/{max_wait_time}s)")
                            print()
                            ColorLogger.success("AI生成完成！")
                            break
                    except:
                        pass
                    await page.wait_for_timeout(wait_interval * 1000)
                    waited_time += wait_interval
                    ColorLogger.progress_bar(waited_time, max_wait_time, prefix="生成中...", suffix=f"({waited_time}s/{max_wait_time}s)")

                if waited_time >= max_wait_time:
                    print()
                    ColorLogger.warning("等待超时，但继续尝试查找图片...")

                await page.wait_for_timeout(3000)

                img_selectors = [
                    'div.w-full.max-w-96.rounded-2xl img',
                    'img[alt*="生成"]',
                    'img[alt*="Generated"]',
                    'div.rounded-2xl img',
                    'div[class*="aspect-auto"] img'
                ]
                img_element = None
                for sel in img_selectors:
                    try:
                        await page.wait_for_selector(sel, timeout=10000)
                        imgs = await page.query_selector_all(sel)
                        if imgs:
                            img_element = imgs[-1]
                            break
                    except:
                        continue
                if img_element:
                    img_url = await img_element.get_attribute('src')
                    if img_url:
                        ColorLogger.success("找到图片URL！")
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
                pass
    
    async def generate_ai_image(self, prompt, style="classic", reference_image_path=None, backend: str = "copilot", aspect_ratio: str = "3:4"):
        """使用Playwright生成AI图片

        Args:
            prompt: 原始提示词
            style: 生成风格，"classic"为传统风格，"hand_drawn"为手绘风格
            reference_image_path: 参考图片路径（若提供则使用@图片并上传模仿风格）
            backend: 生成后端，"copilot" 或 "modelscope"
            aspect_ratio: 生成比例，示例："3:4"、"1:1" 等
        """
        # 使用ModelScope本地/显卡生成
        if backend == "modelscope":
            try:
                if not HAS_MODELSCOPE:
                    raise RuntimeError("未安装modelscope/torch，请改用copilot或安装依赖")

                # 缓存目录设在当前目录
                os.environ.setdefault("MODELSCOPE_CACHE", os.path.abspath("./"))

                # 设备与精度
                if torch.cuda.is_available():
                    torch_dtype = torch.bfloat16
                    device = "cuda"
                else:
                    torch_dtype = torch.float32
                    device = "cpu"

                # 分辨率映射 (使用Qwen-Image推荐值)
                ar = {
                    "1:1": (1328, 1328),
                    "16:9": (1664, 928),
                    "9:16": (928, 1664),
                    "4:3": (1472, 1140),
                    "3:4": (1140, 1472),
                    "3:2": (1584, 1056),
                    "2:3": (1056, 1584),
                }
                width, height = ar.get(aspect_ratio, (1140, 1472))

                # 加稳定画质魔法词
                positive_magic = {"en": ", Ultra HD, 4K, cinematic composition.", "zh": ", 超清，4K，电影级构图."}
                # 如果是中文提示就拼接中文后缀
                suffix = positive_magic["zh"] if any(ch > '\u007f' for ch in prompt) else positive_magic["en"]

                model_name = "Qwen/Qwen-Image"
                pipe = DiffusionPipeline.from_pretrained(model_name, torch_dtype=torch_dtype, cache_dir=os.path.abspath("./"))
                pipe = pipe.to(device)
                
                image = pipe(
                    prompt=prompt + suffix,
                    negative_prompt="",
                    width=width,
                    height=height,
                    num_inference_steps=50,
                    true_cfg_scale=4.0,
                    generator=torch.Generator(device=device) # 使用动态随机种子
                ).images[0]

                # 保存到临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    image.save(temp_file.name)
                    return temp_file.name
            except Exception as e:
                tb = traceback.format_exc()
                ColorLogger.error(f"ModelScope生成失败: {e}\n{tb}")
                return None

        # Copilot 后端
        # 若指定参考图片，则走参考图片流程
        if reference_image_path and os.path.exists(reference_image_path):
            return await self.generate_ai_image_with_reference(prompt, reference_image_path)
        # 统一的、稳定的“无文字”手绘风格提示词
        if style == "hand_drawn":
            base_prompt = (
                "中国古风手绘插画，纸本蜡彩+彩铅质感，低饱和复古配色，米黄色羊皮纸背景。"
                "线条略抖动、边缘略糙、阴影轻微颗粒化。画面简洁、人物主体明确，背景留白充足。"
                "严格禁止任何文字、印章、题字、签名、数字、标识。"
                "长方形构图（3:4），头肩胸像为主，构图居中。"
            )
        else:
            base_prompt = (
                "国风插画，低饱和复古色调，米黄色羊皮纸背景，画面干净。"
                "严格禁止任何文字。长方形构图（3:4）。"
            )

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
                # 避免逐字键入导致回车发送：一次性填入
                await page.fill(input_selector, full_prompt)
                
                # 发送消息
                await page.keyboard.press('Enter')
                
                # 等待生成开始 - 检查是否有生成指示器
                ColorLogger.progress("等待AI开始生成...")
                try:
                    # 更新后的按钮选择器
                    await page.wait_for_selector('button[data-testid="stop-button"]', timeout=10000)
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
                        # 检查是否还在生成 - 使用新的选择器
                        generating_indicator = await page.query_selector('button[data-testid="stop-button"]')
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
    def compose_card(self, card_data, ai_image_path, no_border=False):
        """合成最终卡牌（优化布局与融合效果）

        Args:
            card_data: 卡牌数据
            ai_image_path: AI图片路径
            no_border: 是否去除边框
        """
        try:
            ColorLogger.compose("开始合成卡牌...")
            
            card_group = card_data.get('card_group', '基础卡')
            card_name = card_data.get('card_name', '未命名卡牌')
            description = card_data.get('description', '')
            price = card_data.get('price', '')

            # 根据卡牌组别选择背景
            if card_group == "历史人物卡":
                # 历史人物卡直接使用AI生成的图（AI已经写了字，不需要额外绘制）
                return Image.open(ai_image_path).convert("RGBA")
                
            # 创建一张新卡牌
            card = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (255, 255, 255, 0))
            draw = ImageDraw.Draw(card)

            # 加载基础图片
            if no_border:
                # 去除边框模式：创建一个长方形纯色背景（3:4比例）
                # 参考用户图片，卡牌宽度大约是高度的3/4
                card_width = 600  # 宽度
                card_height = 800  # 高度 (4/3 比例)
                background = Image.new('RGBA', (card_width, card_height), (139, 69, 19, 255))  # 棕色背景
            else:
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
            # 对于长方形卡牌（600x800），调整可用宽度
            available_width = bg_width - 60  # 调整边距以适应长方形构图
            
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

            # introduce区域：使用底栏形状作为文本背景（若AI已写字，本区域仅做装饰）
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
            # 加载手写风格字体（回退链）
            def load_font_chain(names, size):
                for name in names:
                    try:
                        return ImageFont.truetype(name, size)
                    except:
                        continue
                return ImageFont.load_default()

            # 适配手写中文字体优先级（可自行将对应ttf放入项目根目录）
            handwriting_candidates = [
                "HanYiZhuYuan.ttf",      # 示例：手写体（需自备）
                "ZCOOLKuaiLe-Regular.ttf",
                "LXGWWenKai-Regular.ttf",
                "simhei.ttf",
                "msyh.ttc",
                "arial.ttf"
            ]

            font_title = load_font_chain(handwriting_candidates, 60)
            font_desc = load_font_chain(handwriting_candidates, 28)

            # 统一：不再使用emoji
            emoji = ''
            
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

            # 渲染手写质感：对文字做微小抖动、多层叠加，并加轻微高斯模糊与噪点
            def render_handwriting_text(base_img, text, position, font, fill=(240, 230, 210)):
                temp = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
                tdraw = ImageDraw.Draw(temp)
                x, y = position
                # 叠加几层轻微偏移
                for i in range(4):
                    dx = random.randint(-1, 1)
                    dy = random.randint(-1, 1)
                    tdraw.text((x + dx, y + dy), text, fill=fill, font=font)
                # 轻微模糊
                blurred = temp.filter(ImageFilter.GaussianBlur(radius=0.35))
                # 叠加少量噪点（以乘法方式压到背景）
                noise = Image.effect_noise(base_img.size, 5).convert('L')
                noise = ImageOps.colorize(noise, (0, 0, 0), (255, 255, 255)).convert('RGBA')
                noise.putalpha(20)
                base_img.alpha_composite(blurred)
                base_img.alpha_composite(noise)

            # 如果AI负责写字，则不额外叠加标题；否则用手写渲染绘制
            if not card_data.get('ai_writes_text'):
                render_handwriting_text(final_card, card_name, (name_x, name_y), font_title, fill=(245, 235, 215))
            
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

            # 计算可用区域（为长方形构图调整边距）
            text_margin = 25  # 调整边距以适应长方形构图
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
            
            # 如果AI负责写字，底栏不再覆盖文本；否则渲染手写说明
            if not card_data.get('ai_writes_text'):
                for i, line in enumerate(description_lines):
                    line_bbox = draw.textbbox((0, 0), line, font=font_desc)
                    line_width = line_bbox[2] - line_bbox[0]

                    available_x_start = intro_x + text_margin
                    available_x_width = intro_width - (text_margin * 2)
                    line_x = available_x_start + (available_x_width - line_width) // 2

                    if line_x < intro_x + text_margin:
                        line_x = intro_x + text_margin
                    elif line_x + line_width > intro_x + intro_width - text_margin:
                        line_x = intro_x + intro_width - text_margin - line_width

                    line_y = start_y + i * line_height
                    render_handwriting_text(final_card, line, (line_x, line_y), font_desc, fill=(240, 230, 210))
            
            ColorLogger.success("卡牌合成完成！")
            return final_card
        except Exception as e:
            ColorLogger.error(f"合成卡牌失败: {e}")
            return None

    def save_full_ai_card(self, ai_image_path, output_path):
        """不做模板合成，直接使用AI整张牌。

        - 统一为3:4比例（600x800）
        - 仅做轻度滤镜，保证观感一致
        - 保持AI生成的完整布局，不进行裁切
        """
        try:
            img = Image.open(ai_image_path).convert('RGBA')
            target_size = (600, 800)

            # 获取原图尺寸
            original_width, original_height = img.size

            # 计算缩放比例，保持宽高比
            target_width, target_height = target_size
            scale = min(target_width / original_width, target_height / original_height)

            # 计算新的尺寸
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            # 缩放图片
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 创建白色背景
            background = Image.new('RGBA', target_size, (255, 255, 255, 255))

            # 居中粘贴（不裁切）
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
            background.paste(resized, (paste_x, paste_y), resized)

            # 极轻模糊，贴合纸面质感
            final_img = background.filter(ImageFilter.GaussianBlur(radius=0.2))
            final_img.save(output_path, 'PNG')
            return True
        except Exception as e:
            ColorLogger.error(f"保存整张AI卡牌失败: {e}")
            return False
    
    async def generate_single_card(self, card_data, style="classic", no_border=False, reference_image_path=None, ai_full_card=False, backend: str = "copilot", aspect_ratio: str = "3:4"):
        """生成单张卡牌

        Args:
            card_data: 卡牌数据
            style: 生成风格，"classic"为传统风格，"hand_drawn"为手绘风格
            no_border: 是否去除边框
        """
        card_name = card_data.get('card_name', 'unknown')
        ai_prompt = card_data.get('ai_prompt', '')

        ColorLogger.header(f"开始生成卡牌: {card_name} (风格: {style})")

        # 生成AI图片
        ai_image_path = await self.generate_ai_image(ai_prompt, style, reference_image_path, backend=backend, aspect_ratio=aspect_ratio)
        
        if ai_image_path:
            output_filename = f"{card_name}.png"
            output_path = os.path.join(self.output_path, output_filename)

            if ai_full_card or card_data.get('ai_writes_text'):
                # 直接保存AI整张牌
                success = self.save_full_ai_card(ai_image_path, output_path)
                if success:
                    ColorLogger.success(f"卡牌生成完成(整张AI): {output_path}")
                    try:
                        os.unlink(ai_image_path)
                        ColorLogger.info("临时文件已清理")
                    except:
                        pass
                    return output_path
                else:
                    ColorLogger.error(f"卡牌 {card_name} 保存失败")
            else:
                # 模板合成
                final_card = self.compose_card(card_data, ai_image_path, no_border=no_border)
                if final_card:
                    final_card.save(output_path, 'PNG')
                    ColorLogger.success(f"卡牌生成完成: {output_path}")
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

    async def generate_historical_cards(self, countries=None, style="hand_drawn", no_border=True, reference_image_path=None, ai_full_card=False, backend: str = "copilot", aspect_ratio: str = "3:4"):
        """生成历史人物卡牌

        Args:
            countries: 要生成的国家列表，如果为None则生成所有国家
            style: 生成风格，"classic"为传统风格，"hand_drawn"为手绘风格
            no_border: 是否去除边框
        """
        historical_data = self.load_historical_characters()
        if not historical_data:
            ColorLogger.error("历史人物数据加载失败")
            return

        # 如果没有指定国家，则生成所有国家
        if countries is None:
            countries = [country['country'] for country in historical_data]

        total_cards = 0
        generated_count = 0

        for country_data in historical_data:
            country_name = country_data['country']
            if country_name not in countries:
                continue

            ColorLogger.header(f"开始生成 {country_name} 历史人物卡牌")

            for character_data in country_data['characters']:
                # 生成卡牌数据
                card_data = self.generate_historical_card_data(character_data, country_name)

                try:
                    await self.generate_single_card(card_data, style=style, no_border=no_border, reference_image_path=reference_image_path, ai_full_card=ai_full_card, backend=backend, aspect_ratio=aspect_ratio)
                    generated_count += 1
                    ColorLogger.success(f"成功生成历史人物卡牌: {card_data['card_name']}")
                except Exception as e:
                    ColorLogger.error(f"生成历史人物卡牌 '{card_data['card_name']}' 时发生错误: {e}")
                    ColorLogger.warning("将在2秒后继续处理下一张卡牌...")
                    await asyncio.sleep(2)

                total_cards += 1

        ColorLogger.header(f"历史人物卡牌生成完成！成功生成 {generated_count}/{total_cards} 张卡牌")

async def main():
    """主函数：支持多种生成模式"""
    import sys

    generator = CardGenerator()

    # 检查命令行参数
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "historical":
            # 生成历史人物卡牌
            countries_arg = sys.argv[2] if len(sys.argv) > 2 else None
            countries = countries_arg.split(',') if countries_arg else None
            style = sys.argv[3] if len(sys.argv) > 3 else "hand_drawn"
            no_border = sys.argv[4].lower() == "true" if len(sys.argv) > 4 else True
            reference_image = sys.argv[5] if len(sys.argv) > 5 else "微信图片_20250928182802_712_476.jpg"
            ai_full_card = (sys.argv[6].lower() == "true") if len(sys.argv) > 6 else True

            print(f"生成模式: 历史人物卡牌")
            print(f"国家列表: {countries or '所有国家'}")
            print(f"生成风格: {style}")
            print(f"去除边框: {no_border}")

            await generator.generate_historical_cards(countries=countries, style=style, no_border=no_border, reference_image_path=reference_image, ai_full_card=ai_full_card)
        elif mode == "classic":
            # 传统卡牌生成模式
            await generator.generate_all_cards()
        else:
            print("未知的生成模式，支持的模式: historical, classic")
            return
    else:
        # 默认生成传统卡牌
        print("未指定生成模式，默认生成传统卡牌...")
        await generator.generate_all_cards()

if __name__ == "__main__":
    asyncio.run(main())
