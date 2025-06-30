# 春秋杀卡牌生成器 🎮

一个基于AI的自动化卡牌生成工具，专为春秋杀桌游设计。使用Microsoft Copilot AI生成精美的卡牌图片，并自动合成完整的游戏卡牌。

![项目状态](https://img.shields.io/badge/状态-开发中-green)
![Python版本](https://img.shields.io/badge/Python-3.8+-blue)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)

## ✨ 功能特点

### 🎨 **AI驱动的图片生成**
- 使用Microsoft Copilot AI生成高质量卡牌插画
- 国风写实融合风格，参考《清明上河图》精致线条感
- 自动化浏览器操作，无需手动干预

### 🃏 **多类型卡牌支持**
- **🏰 国家卡** - 秦、楚、齐、燕、赵、魏、韩、周王室
- **🧠 思想卡** - 道家、儒家、墨家、法家、兵家
- **⚖️ 变法卡** - 郡县制改革、商鞅变法、胡服骑射等
- **🔗 连锁卡** - 贵族反抗、百姓暴动、宗法势力阻挠等
- **⚔️ 军事卡** - 精锐骑兵、重装步兵、弩兵方阵等
- **💰 经济卡** - 盐铁专营、农业税收、商业贸易等
- **🎁 道具卡** - 青铜鼎、战车、玉玺、名剑
- **📜 锦囊牌** - 城濮之战、合纵连横、远交近攻等
- **🙏 祭祀卡** - 凤鸣岐山、麒麟踏春、蝗灾、大旱等

### 🌈 **智能主题色系统**
- 根据卡牌主题自动选择emoji颜色
- 深色调渲染，与卡牌整体风格协调
- 精细化文字布局和边距控制

### 🚀 **炫酷用户体验**
- 彩色日志输出，实时显示生成进度
- 动态进度条，替代重复的状态信息
- 智能错误处理和自动重试机制

## 📋 系统要求

- **Python 3.8+**
- **Windows 10/11** (推荐)
- **Chrome/Edge浏览器**
- **Microsoft账户** (用于Copilot访问)

## 🛠️ 安装说明

### 1. 克隆项目
```bash
git clone https://github.com/your-username/Auto_Card_Drowing.git
cd Auto_Card_Drowing
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 安装Playwright浏览器
```bash
playwright install chromium
```

### 4. 准备基础图片
确保 `Base_IMG/` 目录下有以下文件：
- `background.png` - 卡牌背景模板
- `title.png` - 标题区域模板  
- `introduce.png` - 描述区域模板

## 🚀 使用方法

### 快速开始
```bash
python card_generator.py
```

### 配置卡牌数据
编辑 `cards.json` 文件来自定义卡牌：

```json
{
  "card_group": "国家卡",
  "card_name": "秦国",
  "color_theme": "黑金",
  "ai_prompt": "秦国旗帜飘扬，背景为函谷关雄关...",
  "description": "军事+1，地形加成：渭水（经济+1），山地（军事防御+1）"
}
```

### 首次运行设置
1. 程序会自动打开浏览器并导航到Copilot
2. 请在浏览器中登录您的Microsoft账户
3. 登录完成后按回车键继续
4. 程序会自动保存登录状态，后续运行无需重复登录

## 📁 项目结构

```
Auto_Card_Drowing/
├── card_generator.py      # 主程序文件
├── cards.json            # 卡牌配置数据
├── requirements.txt      # Python依赖列表
├── Base_IMG/            # 基础模板图片
│   ├── background.png
│   ├── title.png
│   └── introduce.png
├── Generated_Cards/     # 生成的卡牌输出目录
├── browser_data/        # 浏览器数据（被git忽略）
└── README.md           # 项目说明文档
```

## 🎯 核心类和方法

### `ColorLogger` - 彩色日志系统
```python
ColorLogger.success("成功信息")     # ✅ 绿色
ColorLogger.error("错误信息")       # ❌ 红色  
ColorLogger.warning("警告信息")     # ⚠️ 黄色
ColorLogger.progress("进度信息")    # 🚀 青色
ColorLogger.generating("生成中")    # 🎨 洋红色
```

### `CardGenerator` - 主要功能类
- `generate_ai_image()` - AI图片生成
- `compose_card()` - 卡牌合成
- `generate_single_card()` - 单卡生成
- `generate_all_cards()` - 批量生成

## ⚙️ 配置选项

### AI提示词配置
程序会自动为每个AI提示词添加基础前缀：
```
写实融合国风插画风格（参考《清明上河图》的精致线条感与《鬼谷八荒》的色彩层次）。
整体色调偏复古，低饱和度，背景带有米黄羊皮纸质感。图片长宽比注意只能是1比1。
生成字时请使用标准正楷字。
```

### 主题色映射
| 主题色关键词 | Emoji颜色 | 色值 |
|-------------|----------|------|
| 黑金/墨色 | 深金色 | `#D4AF37` |
| 深红/红色 | 深红色 | `#8B0000` |
| 蓝色 | 深蓝色 | `#000080` |
| 紫色 | 深紫色 | `#4B0082` |

## 🐛 常见问题

### Q: 程序提示找不到输入框？
A: 请确保已正确登录Microsoft Copilot，并且页面完全加载。

### Q: AI生成的图片质量不理想？
A: 可以调整 `cards.json` 中的 `ai_prompt` 来优化提示词。

### Q: 生成的卡牌文字布局有问题？
A: 检查 `description` 字段长度，过长的文字会自动换行。

### Q: Emoji不显示颜色？
A: 程序会自动根据 `color_theme` 渲染emoji颜色，确保该字段正确设置。

## 🔧 开发说明

### 添加新卡牌类型
1. 在 `cards.json` 中添加新的卡牌数据
2. 在 `card_type_emojis` 字典中添加对应emoji
3. 根据需要在主题色映射中添加新的颜色规则

### 自定义渲染效果
- 修改 `compose_card()` 方法中的布局参数
- 调整字体大小、边距、颜色等视觉元素
- 优化渐变融合效果参数

## 📄 许可证

本项目采用 MIT 许可证。详情请参见 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/your-username/Auto_Card_Drowing/issues)
- 发送邮件至：your.email@example.com

## 🎉 致谢

- Microsoft Copilot - AI图片生成
- Playwright - 浏览器自动化
- Pillow - 图像处理
- 春秋杀游戏社区 - 灵感来源

---

⭐ 如果这个项目对你有帮助，请给它一个星标！ 