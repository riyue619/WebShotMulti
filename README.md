# WebShotMulti_3.0 - 多线程网页截图工具

WebShotMulti_3.0 是一款基于 Python 开发的多线程网页截图工具，支持批量输入 URL 并自动生成截图报告。通过图形化界面操作，可灵活设置线程数量、输出目录和浏览器驱动路径，适用于网页批量截图、网站状态检查等场景。
## 补充

使用的是python的selenium自动化，没有使用playwright自动化 虽然说playwright环境配置起来比较简单，但是我感觉playwright截图速度没有selenium快 所以先来无事就用selenium写了一个自动站点探测的小工具
## 功能特点

- **多线程处理**：支持自定义线程数量，高效批量处理多个 URL
- **智能 URL 解析**：自动识别并移除 URL 中可能包含的 HTTP 方法前缀（如 GET、POST）
- **错误处理**：针对网络错误、连接被拒绝等情况提供详细提示
- **结果报告**：自动生成 HTML 报告，展示所有 URL 及其对应截图
- **配置保存**：支持保存/加载配置，避免重复设置
- **无头模式**：使用 Chrome 无头模式运行，不显示浏览器窗口


## 界面说明

####
![屏幕截图 2025-07-09 142726](https://github.com/user-attachments/assets/291cb913-1e5a-498b-816d-14e08c8465c9)
####
![image](https://github.com/user-attachments/assets/287daf7d-c145-4e39-8d6c-fe71bd700918)
####
![image](https://github.com/user-attachments/assets/697c52ef-3a84-453f-89f2-547fc0d02485)


1. **文件设置区**：
   - 输入 URL（每行一个，支持带 HTTP 方法前缀的格式）
   - 设置截图输出目录

2. **参数设置区**：
   - 调整线程数量（建议 5-20 之间，根据电脑性能调整）
   - 指定 Chrome 浏览器驱动路径

3. **控制按钮**：
   - 开始处理：启动多线程截图任务
   - 停止处理：中断当前截图任务
   - 保存配置：保存当前设置（输出目录、驱动路径、线程数）

4. **进度显示区**：实时展示各线程处理状态和结果


## 使用步骤

1. **准备工作**：
   - 安装 Chrome 浏览器
   - !!!!下载与 Chrome 版本匹配的ChromeDrive !!![[ChromeDriver](https://sites.google.com/chromium.org/driver/)](https://googlechromelabs.github.io/chrome-for-testing/#stable)
####
![image](https://github.com/user-attachments/assets/4d476038-9663-4456-97a4-0a2d66be58cd)
####
选择驱动路径
![image](https://github.com/user-attachments/assets/3acb5f29-5682-4ceb-a92e-6e680b495fc6)

   - 确保 Python 环境已安装（3.6+ 版本）
   - 

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
