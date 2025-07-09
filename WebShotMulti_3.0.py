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
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ------------------- 全局变量 -------------------
running = False
threads = []
url_queue = queue.Queue()
result_queue = queue.Queue()
lock = threading.Lock()
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('ignore-certificate-errors')

# 声明全局UI组件变量（在create_gui中初始化）
root = None
url_text = None
output_dir = None
driver_path = None
thread_count = None
status_var = None
start_button = None
stop_button = None
save_config_button = None
progress_text = None
start_time = 0


# ------------------- 业务逻辑方法 -------------------
def process_url():
    """线程任务：处理单个URL的访问、截图"""
    driver = webdriver.Chrome(service=Service(executable_path=path), options=chrome_options)
    while not url_queue.empty() and running:
        try:
            url = url_queue.get()
            root.after(0, update_progress, f"线程 {threading.current_thread().name} 正在访问: {url}")

            # 访问URL
            driver.get(url)
            time.sleep(1)  # 等待页面加载稳定

            # 截图逻辑
            sjc = random.randint(1000, 9999)
            result_filename = f"{result_dir}/{sjc}.png"
            if driver.save_screenshot(result_filename):
                root.after(0, update_progress, f"截图已保存: {result_filename}")
                result_queue.put((url, sjc))
            else:
                root.after(0, update_progress, f"截图失败: {url}")

        except WebDriverException as e:
            # 精准匹配 "net::ERR_CONNECTION_REFUSED" 错误
            if "net::ERR_CONNECTION_REFUSED" in str(e):
                root.after(0, update_progress, f"连接被拒绝: {url}（可能是服务器未启动或URL无效）")
            # 处理其他网络相关错误
            elif "connection" in str(e).lower() or "timeout" in str(e).lower():
                root.after(0, update_progress, f"网络错误: {url} - {str(e).splitlines()[0]}")  # 只显示错误摘要
            else:
                root.after(0, update_progress, f"浏览器驱动错误: {url} - {str(e).splitlines()[0]}")

        except Exception as e:
            root.after(0, update_progress, f"处理URL时出错: {url} - {str(e)}")

        finally:
            url_queue.task_done()

    driver.quit()
"""线程任务：处理单个URL的访问、截图"""


"""线程任务：处理单个URL的访问、截图"""

def browse_output_dir():
    """浏览并选择输出目录"""
    directory = filedialog.askdirectory(title="选择输出目录")
    if directory:
        output_dir.set(directory)
"""浏览并选择输出目录"""

def driver_dir():
    """选择浏览器驱动程序"""
    file_path = filedialog.askopenfilename(
        title="选择浏览器驱动程序",
        filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
    )
    if file_path:
        driver_path.set(file_path)
        file_path = file_path.replace("/", "\\")
        global path
        path = file_path
"""选择浏览器驱动程序"""

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
    # 处理每一行：先去左侧空格，再检查是否以HTTP方法开头，是则移除前缀
    urls = []
    for line in url_text_content.split("\n"):
        stripped_line = line.strip()
        if not stripped_line:
            continue  # 跳过空行
        # 去除行首可能的空白后检查前缀
        cleaned_line = stripped_line.lstrip()
        for method in http_methods:
            if cleaned_line.startswith(method):
                # 移除HTTP方法前缀（保留原URL的大小写和格式）
                cleaned_line = cleaned_line[len(method):].strip()
                break  # 找到匹配的方法后跳出循环
        urls.append(cleaned_line)

    if not urls:
        messagebox.showerror("错误", "请输入有效的URL")
        return

    output = output_dir.get().replace("\\", "/")
    if not output:
        messagebox.showerror("错误", "请先选择输出目录")
        return

    driver = driver_path.get()
    if not  driver:
        messagebox.showerror("错误","请选择浏览器驱动路径")
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
        # 打包后的环境（PyInstaller 等工具会设置 sys.frozen 为 True）
        app_dir = os.path.dirname(sys.executable)
        return app_dir
    else:
        # 未打包的开发环境（.py 文件运行时）
        app_dir = os.path.dirname(os.path.abspath(__file__))
        return app_dir
"""获取当前目录（脚本或程序所在目录）"""

def save_config():
    """保存配置到文件"""
    output = output_dir.get()
    if not output:
        messagebox.showerror("错误", "请先选择输出目录")
        return

    driver = driver_path.get()
    if not driver:
        messagebox.showerror("错误", "请选择浏览器驱动路径")
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
        "driver_path": driver_path.get(),
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
        # 检查配置文件是否存在
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "output_dir" in config:
                    output_dir.set(config["output_dir"])
                if "driver_path" in config:
                    driver_path.set(config["driver_path"])
                    global path
                    path = config["driver_path"]
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
    global start_button, stop_button,save_config_button, progress_text

    # 初始化主窗口
    root = tk.Tk()
    root.title("WebShotMulti_3.0(多线程网页截图工具)")
    root.geometry("800x600")
    root.resizable(True, True)

    # 初始化变量
    default_output_dir = get_current_dir()
    output_dir = tk.StringVar(value=default_output_dir)
    driver_path = tk.StringVar()
    thread_count = tk.StringVar(value="10")
    status_var = tk.StringVar(value="就绪")

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

    ttk.Label(thread_frame, text="浏览器驱动目录:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(thread_frame, textvariable=driver_path, width=50).grid(row=1, column=1, padx=5, pady=5)
    ttk.Button(thread_frame, text="浏览", command=driver_dir).grid(row=1, column=2, padx=5, pady=5)

    # 按钮框架
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    start_button = ttk.Button(button_frame, text="开始处理", command=start_processing)
    start_button.pack(side=tk.LEFT, padx=5)

    stop_button = ttk.Button(button_frame, text="停止处理", command=stop_processing, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, padx=5)

    save_config_button = ttk.Button(button_frame, text="保存配置", command=save_config)
    save_config_button.pack(side=tk.LEFT, padx=5)

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
    create_gui()  # 调用UI创建方法
    notice_message = (
        "注意事项：\n"
        "1. 请确保浏览器驱动（ChromeDriver）版本与本地Chrome浏览器版本匹配\n"
        "2. 线程数量建议根据电脑性能调整（推荐5-20之间）\n"
        "3. 目标URL需能正常访问，否则会提示连接错误"
    )
    messagebox.showinfo("使用须知", notice_message)  # 弹窗显示注意信息
    load_config()
    root.mainloop()  # 启动主事件循环
