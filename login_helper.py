#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from playwright.async_api import async_playwright

class LoginHelper:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.user_data_path = os.path.join(self.base_path, "browser_data")
        
        # 创建用户数据目录
        if not os.path.exists(self.user_data_path):
            os.makedirs(self.user_data_path)
    
    async def setup_login(self):
        """交互式设置登录状态"""
        print("正在启动浏览器进行登录设置...")
        
        async with async_playwright() as p:
            # 启动持久化浏览器上下文
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_path,
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security'
                ]
            )
            
            try:
                # 创建新页面或使用现有页面
                if len(browser.pages) == 0:
                    page = await browser.new_page()
                else:
                    page = browser.pages[0]
                
                # 访问Copilot网站
                print("正在访问 Copilot 网站...")
                await page.goto("https://copilot.microsoft.com", timeout=60000)
                
                # 等待页面加载
                await page.wait_for_timeout(3000)
                
                print("\n" + "="*60)
                print("请在浏览器中完成以下步骤:")
                print("1. 如果需要，请点击登录按钮")
                print("2. 输入您的Microsoft账号信息")
                print("3. 完成登录过程")
                print("4. 确保可以看到Copilot的输入框")
                print("5. 可以尝试输入一个测试消息确认功能正常")
                print("="*60)
                
                # 等待用户确认登录完成
                input("\n登录完成后，按回车键继续...")
                
                # 验证登录状态
                await self.verify_login_status(page)
                
                print("\n登录状态设置完成！")
                print("浏览器会话已保存，下次运行时会自动使用此登录状态。")
                
                # 保持浏览器打开一段时间，让用户确认
                print("\n浏览器将在10秒后关闭...")
                await page.wait_for_timeout(10000)
                
            except Exception as e:
                print(f"设置登录状态时发生错误: {e}")
            finally:
                await browser.close()
    
    async def verify_login_status(self, page):
        """验证登录状态"""
        try:
            # 检查是否存在输入框
            input_selectors = [
                'textarea[data-testid="composer-input"]',
                'textarea[placeholder*="消息"]',
                'textarea[placeholder*="Message"]',
                'textarea#userInput',
                'textarea[role="textbox"]'
            ]
            
            found_input = False
            for selector in input_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        print(f"✓ 找到输入框: {selector}")
                        found_input = True
                        break
                except:
                    continue
            
            if not found_input:
                print("⚠ 警告: 未找到输入框，可能需要重新登录")
            
            # 检查是否有登录按钮（如果有，说明未登录）
            login_selectors = [
                'button[data-testid="sign-in-button"]',
                'a[href*="login"]',
                'button:has-text("登录")',
                'button:has-text("Sign in")'
            ]
            
            for selector in login_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print("⚠ 警告: 检测到登录按钮，可能未完全登录")
                        return False
                except:
                    continue
            
            print("✓ 登录状态验证通过")
            return True
            
        except Exception as e:
            print(f"验证登录状态时发生错误: {e}")
            return False

async def main():
    print("Copilot 登录助手")
    print("=" * 30)
    
    helper = LoginHelper()
    await helper.setup_login()

if __name__ == "__main__":
    asyncio.run(main())
