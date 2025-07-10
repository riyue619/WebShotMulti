import json
import os
import random
import sys
import time
import threading
import queue
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from playwright.sync_api import sync_playwright
import json

# ------------------- 全局变量 -------------------
running = False
threads = []
url_queue = queue.Queue()
result_queue = queue.Queue()
lock = threading.Lock()

# 声明全局UI组件变量（在create_gui中初始化）
root = None
url_text = None
output_dir = None
driver_path = None
thread_count = None
status_var = None
start_button = None
cookie_var = None  # 用于存储复选框状态
stop_button = None
save_config_button = None
progress_text = None
start_time = 0

# ------------------- 业务逻辑方法 -------------------
def delete_cookies(file_path="cookies.json"):
    '''清除历史Cookie'''
    with open(file_path, "w") as f:
        f.write("")
        root.after(0, update_progress, f"历史Cookie已清除")
'''清除历史Cookie'''
def manual_login():
    """手动登录并保存Cookie（从输入框提取第一个URL作为登录页面）"""
    # 从输入框中获取所有URL
    url_text_content = url_text.get("1.0", tk.END).strip()
    urls = [line.strip() for line in url_text_content.split("\n") if line.strip()]

    if not urls:
        messagebox.showerror("错误", "输入框中未找到有效的URL")
        return

    # 提取第一个URL作为登录页面
    login_url = urls[0]
    root.after(0, update_progress, f"准备登录: {login_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 非无头模式，方便用户操作
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(login_url, timeout=10000)
            root.after(0, update_progress, f"已打开登录页面: {page.url}")

            # 替换 input() 为弹窗
            messagebox.showinfo("提示", "请手动登录完成后点击“确定”继续")

            # 用户点击“确定”后继续执行
            cookie_file = os.path.join(output_dir.get(), "cookies.json")
            save_cookies(context, cookie_file)
            root.after(0, update_progress, f"Cookie已保存到: {cookie_file}")

        except Exception as e:
            root.after(0, update_progress, f"登录过程中出错: {e}")
            messagebox.showerror("错误", f"登录失败: {e}")

        finally:
            context.close()
            browser.close()
"""手动登录并保存Cookie（从输入框提取第一个URL作为登录页面）"""
def save_cookies(context, file_path="cookies.json"):
    """保存当前上下文的Cookie到文件"""
    cookies = context.cookies()
    with open(file_path, "w") as f:
        json.dump(cookies, f)
    root.after(0, update_progress, f"Cookie已保存到: {file_path}")
"""保存当前上下文的Cookie到文件"""
def load_cookies(file_path="cookies.json"):
    """从文件加载Cookie"""
    with open(file_path, "r") as f:
        return json.load(f)
"""从文件加载Cookie"""
def process_url():
    """线程任务：处理单个URL的访问、截图（加载Cookie）"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # 加载 Cookie（如果勾选了复选框）
        if cookie_var.get():
            cookie_file = os.path.join(output_dir.get(), "cookies.json")
            try:
                if os.path.exists(cookie_file):
                    cookies = load_cookies(cookie_file)
                    context.add_cookies(cookies)
                    root.after(0, update_progress, f"线程 {threading.current_thread().name} 已加载Cookie")
                else:
                    root.after(0, update_progress, f"未找到Cookie文件: {cookie_file}")
            except Exception as e:
                root.after(0, update_progress, f"加载Cookie失败: {e}")

        page = context.new_page()
        while not url_queue.empty() and running:
            try:
                url = url_queue.get()
                root.after(0, update_progress, f"线程 {threading.current_thread().name} 正在访问: {url}")

                # 访问 URL 并截图
                page.goto(url, timeout=10000)
                time.sleep(1)

                sjc = random.randint(1000, 9999)
                result_filename = os.path.join(result_dir, f"{sjc}.png")
                page.screenshot(path=result_filename)
                root.after(0, update_progress, f"截图已保存: {result_filename}")
                result_queue.put((url, sjc))

            except Exception as e:
                root.after(0, update_progress, f"处理URL时出错: {url} - {str(e)}")
            finally:
                url_queue.task_done()

        context.close()
        browser.close()
"""线程任务：处理单个URL的访问、截图（加载Cookie）"""
def browse_output_dir():
    """浏览并选择输出目录"""
    directory = filedialog.askdirectory(title="选择输出目录")
    if directory:
        output_dir.set(directory)
"""浏览并选择输出目录"""
def update_progress(message):
    """更新进度文本"""
    progress_text.config(state=tk.NORMAL)
    progress_text.insert(tk.END, message + "\n")
    progress_text.see(tk.END)
    progress_text.config(state=tk.DISABLED)
"""更新进度文本"""
def update_status(message):
    """更新状态标签"""
    status_var.set(message)
"""更新状态标签"""
def update_thread_count(count):
    """更新线程数"""
    thread_count.set(count)
"""更新线程数"""
def start_processing():
    """开始处理URL"""
    global running, result_dir, screenshot_dir, timestamp, start_time

    if running:
        return
    url_text_content = url_text.get("1.0", tk.END)
    http_methods = {'GET ', 'POST '}
    urls = []
    for line in url_text_content.split("\n"):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        cleaned_line = stripped_line.lstrip()
        for method in http_methods:
            if cleaned_line.startswith(method):
                cleaned_line = cleaned_line[len(method):].strip()
                break
        urls.append(cleaned_line)

    if not urls:
        messagebox.showerror("错误", "请输入有效的URL")
        return

    output = output_dir.get().replace("\\", "/")
    if not output:
        messagebox.showerror("错误", "请先选择输出目录")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_dir = f"{output}/{timestamp}tp"
    result_dir = f"{output}/result{timestamp}/{timestamp}tp"

    try:
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
    except Exception as e:
        messagebox.showerror("错误", f"创建目录失败: {e}")
        return

    while not url_queue.empty():
        url_queue.get()
    while not result_queue.empty():
        result_queue.get()

    progress_text.config(state=tk.NORMAL)
    progress_text.delete(1.0, tk.END)
    progress_text.config(state=tk.DISABLED)

    try:
        for url in urls:
            url_queue.put(url)

        num_urls = len(urls)
        if num_urls == 0:
            messagebox.showinfo("提示", "URL文件中没有有效的URL")
            return

        update_status(f"共读取 {num_urls} 个URL，准备开始多线程处理...")
        update_progress(f"共读取 {num_urls} 个URL，准备开始多线程处理...")

        try:
            thread_count_val = int(thread_count.get())
            if thread_count_val <= 0:
                thread_count_val = 10
                update_thread_count(10)
        except:
            thread_count_val = 10
            update_thread_count(10)

        running = True
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)

        start_time = time.time()
        for i in range(thread_count_val):
            t = threading.Thread(target=process_url, name=f"线程-{i + 1}")
            t.daemon = True
            t.start()
            threads.append(t)

        result_thread = threading.Thread(target=process_results)
        result_thread.daemon = True
        result_thread.start()

    except Exception as e:
        update_status(f"处理过程出错: {e}")
        messagebox.showerror("错误", f"处理过程出错: {e}")
"""开始处理URL"""
def process_results():
    """处理截图结果并生成HTML"""
    global running

    url_queue.join()
    running = False

    root.after(0, update_status, "所有URL处理完成，开始生成HTML报告...")

    html_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <style>
        .table {
            min-width: 100%; 
            border-collapse: collapse;
            margin: 0 20px;
        }
        .table td, .table th { 
            border: 1px solid #ddd; 
            padding: 0px; 
            text-align: center;
        }
        .half-width {
            width: 50%;
        }
        .url {
            word-break: break-all;
        }
        .tp {
            width: 75%;
        }
    </style>
</head>
<body>
    <table class="table table-striped table-bordered">
        <thead>
            <tr>
                <td>URL</td>
                <td class="tp">截图</td>
            </tr>
        </thead>
        <tbody>
'''

    while not result_queue.empty():
        url, sjc = result_queue.get()
        html_content += f'''
                    <tr>
                        <td class="half-width"><a href="{url}" class="url" target="_blank">{url}</a></td>
                        <td class="half-width"><img src="./{timestamp}tp/{sjc}.png" class="tp"></td>
                    </tr>'''

    html_content += '''
        </tbody>
    </table>
</body>
</html>
'''

    try:
        with lock:
            output__dir = output_dir.get().replace("\\", "/")
            html_file = f"{output__dir}/result{timestamp}/zdh.html"
            os.makedirs(os.path.dirname(html_file), exist_ok=True)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

        root.after(0, update_status, f"HTML报告已生成: {html_file}")
        root.after(0, update_progress, f"HTML报告已生成: {html_file}")

        end_time = time.time()
        root.after(0, update_progress, f"总耗时: {end_time - start_time:.2f} 秒")

    except Exception as e:
        root.after(0, update_status, f"生成HTML报告出错: {e}")
        root.after(0, update_progress, f"生成HTML报告出错: {e}")

    root.after(0, lambda: start_button.config(state=tk.NORMAL))
    root.after(0, lambda: stop_button.config(state=tk.DISABLED))
"""处理截图结果并生成HTML"""
def stop_processing():
    """停止处理"""
    global running
    running = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    update_status("已停止处理")
"""停止处理"""
def get_current_dir():
    """获取当前目录（脚本或程序所在目录）"""
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        return app_dir
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        return app_dir
"""获取当前目录（脚本或程序所在目录）"""
def save_config():
    """保存配置到文件"""
    output = output_dir.get()
    if not output:
        messagebox.showerror("错误", "请先选择输出目录")
        return

    try:
        thread_count_val = int(thread_count.get())
        if thread_count_val <= 0:
            thread_count_val = 10
            update_thread_count(10)
    except:
        thread_count_val = 10
        update_thread_count(10)

    config_file_path = os.path.join(output_dir.get(), "web_screenshot_config.json")
    config = {
        "output_dir": output_dir.get(),
        "thread_count": thread_count.get()
    }
    try:
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("配置成功", f"配置已保存到: {config_file_path}")
    except Exception as e:
        messagebox.showerror("配置错误", f"保存配置失败: {e}")
"""保存配置到文件"""
def load_config():
    """从文件加载配置"""
    config_file_path = os.path.join(output_dir.get(), "web_screenshot_config.json")
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "output_dir" in config:
                    output_dir.set(config["output_dir"])
                if "thread_count" in config:
                    thread_count.set(config["thread_count"])
        except json.JSONDecodeError:
            messagebox.showerror("配置错误", f"配置文件格式错误: {config_file_path}")
        except Exception as e:
            messagebox.showerror("配置错误", f"加载配置失败: {e}")
    else:
        print(f"[CONFIG] 配置文件不存在: {config_file_path}")
"""从文件加载配置"""
# ------------------- UI界面创建方法 -------------------
def create_gui():
    """创建所有UI组件并设置布局"""
    global root, url_text, output_dir, driver_path, thread_count, status_var
    global start_button, stop_button,cookie_var, save_config_button, progress_text

    # 初始化主窗口
    root = tk.Tk()
    root.title("WebShotMulti_3.0(多线程网页截图工具)")
    root.geometry("800x600")
    root.resizable(True, True)

    # 初始化变量
    default_output_dir = get_current_dir()
    output_dir = tk.StringVar(value=default_output_dir)
    thread_count = tk.StringVar(value="10")
    status_var = tk.StringVar(value="就绪")
    cookie_var = tk.BooleanVar(value=False)

    # 顶部框架 - 文件设置
    file_frame = ttk.LabelFrame(root, text="文件设置")
    file_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(file_frame, text="输入URL（每行一个）:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    url_text = tk.Text(file_frame, height=5, width=50)
    url_text.grid(row=0, column=1, padx=5, pady=5)
    url_text.insert(tk.END, "http://bwapp/login.php\nhttp://pikachu/\n或者形如:GET(POST) http://bwapp/login.php")

    ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(file_frame, textvariable=output_dir, width=50).grid(row=1, column=1, padx=5, pady=5)
    ttk.Button(file_frame, text="浏览", command=browse_output_dir).grid(row=1, column=2, padx=5, pady=5)

    # 中部框架 - 线程设置
    thread_frame = ttk.LabelFrame(root, text="参数设置")
    thread_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(thread_frame, text="线程数量:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(thread_frame, textvariable=thread_count, width=5).grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(thread_frame, text="(建议根据电脑性能调整)").grid(row=0, column=2, padx=5, pady=5)

    # 按钮框架
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    start_button = ttk.Button(button_frame, text="开始处理", command=start_processing)
    start_button.pack(side=tk.LEFT, padx=5)


    option_checkbox = ttk.Checkbutton(button_frame, text="携带cookie", variable=cookie_var)
    option_checkbox.pack(side=tk.LEFT, padx=5)

    stop_button = ttk.Button(button_frame, text="停止处理", command=stop_processing, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, padx=5)

    save_config_button = ttk.Button(button_frame, text="保存配置", command=save_config)
    save_config_button.pack(side=tk.LEFT, padx=5)

    login_button = ttk.Button(button_frame, text="手动登录并保存Cookie", command=manual_login)
    login_button.pack(side=tk.LEFT, padx=5)

    # 状态标签（底部状态栏）
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # 进度显示文本框（带滚动条）
    progress_frame = ttk.LabelFrame(root, text="处理进度")
    progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    scrollbar = ttk.Scrollbar(progress_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    progress_text = tk.Text(progress_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, state=tk.DISABLED)
    progress_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=progress_text.yview)
"""创建所有UI组件并设置布局"""
# ------------------- 主程序入口 -------------------
if __name__ == "__main__":
    create_gui()
    notice_message = (
        "注意事项：\n"
        "1. 线程数量建议根据电脑性能调整（推荐5-20之间）。\n"
        "2. 目标URL需能正常访问，否则会提示连接错误。"
    )
    messagebox.showinfo("使用须知", notice_message)
    delete_cookies()
    load_config()
    root.mainloop()