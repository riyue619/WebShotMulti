# WebShotMulti_4.0 - 多线程网页截图工具

WebShotMulti_4.0 是一款基于 Python 开发的多线程网页截图工具，支持批量输入 URL 并自动生成截图报告。通过图形化界面操作，可灵活设置线程数量、输出目录和浏览器驱动路径，适用于网页批量截图、网站状态检查等场景。
## 补充
手动登录，程序会将输入框内第一个url作为登录页面的url
## 更新说明
- **Cookie管理**：可以手动登录，登录后保存Cookie 携带Cookie后截图
- **配置简化**： 4.0版本使用了 Playwright自动化库 无需手动下载浏览器以及相同版本的浏览器驱动 可以使用命令安装浏览器 相比3.0 使用 Selenium 自动化库配置简单
## 功能特点

- **多线程处理**：支持自定义线程数量，提高批量截图效率
- **Cookie管理**：支持手动登录并保存Cookie，实现带登录状态访问
- **批量URL处理**：可同时处理多个URL，自动忽略空行和无效格式
- **HTML报告生成**：自动将截图结果整理为HTML报告，方便查看
- **配置保存**：支持保存配置信息，下次使用无需重新设置
- **进度实时显示**：实时展示处理进度和状态信息
- **智能 URL 解析**：自动识别并移除 URL 中可能包含的 HTTP 方法前缀（如 GET、POST）


## 界面说明

####
<img width="1002" height="781" alt="image" src="https://github.com/user-attachments/assets/2c39cc2a-0875-444d-a034-4c432c9c663c" />
####
<img width="1002" height="802" alt="image" src="https://github.com/user-attachments/assets/8be0b9ba-57bf-41f0-b9ef-df407c1b1e1f" />
####
<img width="1800" height="890" alt="image" src="https://github.com/user-attachments/assets/b91bc01d-6b43-4d5b-914e-f302171a24a3" />
####
<img width="992" height="782" alt="image" src="https://github.com/user-attachments/assets/0d28d37c-306a-44a9-bd5d-ef65606d6f8e" />
####
<img width="1798" height="905" alt="image" src="https://github.com/user-attachments/assets/99f59659-f782-4d20-92ac-daa3b34d754e" />



1. **文件设置区**：
   - 输入 URL（每行一个，支持带 HTTP 方法前缀的格式）
   - 设置截图输出目录

2. **参数设置区**：
   - 调整线程数量（建议 5-20 之间，根据电脑性能调整）


3. **控制按钮**：
   - 开始处理：启动多线程截图任务
   - 停止处理：中断当前截图任务
   - 保存配置：保存当前设置（输出目录、线程数）
   - 手动登录并保存Cookie:手动登录并保存Cookie，后续使用保存的Cookie访问后续url

4. **进度显示区**：实时展示各线程处理状态和结果


## 安装说明

### 前置依赖

- Python 3.7+
- 所需Python库：
  - playwright

### 安装步骤

1. 克隆或下载本项目代码解压
2. 安装依赖库：
   ```bash
   pip install playwright
####
<img width="1877" height="997" alt="image" src="https://github.com/user-attachments/assets/5deb86ee-9ddd-47e2-907f-f91180536cd2" />
3.playwright安装
   ```bash
  playwright install chromium
####
<img width="1475" height="755" alt="image" src="https://github.com/user-attachments/assets/19daddd7-a913-4d3f-892f-2688b69fba36" />
4.点击启动
####
<img width="1563" height="765" alt="image" src="https://github.com/user-attachments/assets/a7bd9336-e462-4940-a732-a13991321bdf" />




