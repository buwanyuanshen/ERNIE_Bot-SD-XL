# -*- coding: utf-8 -*-
import base64
import hashlib
import random
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import json
import os

CONFIG_FILE = "paint_config.json"

def get_access_token(api_key, secret_key):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    return str(requests.post(url, params=params).json().get("access_token"))

def show_image(index):
    if 0 <= index < len(image_files):
        img = Image.open(image_files[index])
        img = img.resize((576, 576))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img
        image_index_label.config(text=f"Image {index + 1} of {len(image_files)}")

def next_image():
    global current_image_index
    if current_image_index < len(image_files) - 1:
        current_image_index += 1
        show_image(current_image_index)

def previous_image():
    global current_image_index
    if current_image_index > 0:
        current_image_index -= 1
        show_image(current_image_index)
def generate_image_thread():
    generate_button.config(state=tk.DISABLED)  # 禁用生成按钮以防止多次点击
    generate_image()  # 在新线程中执行生成图片的耗时任务
    generate_button.config(state=tk.NORMAL)  # 重新启用生成按钮

def on_generate_button_click():
    # 创建一个新线程来执行 generate_image_thread 函数
    generator_thread = threading.Thread(target=generate_image_thread)
    generator_thread.start()

def generate_image():
    global current_image_index
    global image_files

    image_files.clear()
    current_image_index = 0

    api_key = api_key_entry.get()
    secret_key = secret_key_entry.get()
    prompt_text = prompt_entry.get()
    negative_prompt_text = negative_prompt_entry.get()
    size_value = size_combobox.get()
    steps_value = int(steps_entry.get())
    n_value = int(n_var.get())
    seed_value = int(seed_entry.get())
    cfg_scale_value = int(cfg_scale_entry.get())
    style_value = style_combobox.get()
    access_token = get_access_token(api_key, secret_key)
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/text2image/sd_xl"
    params = {
        'access_token': access_token
    }
    headers = {
        'Content-Type': 'application/json',
    }
    data = json.dumps({
        "prompt": prompt_text,
        "negative_prompt": negative_prompt_text,
        "size": size_value,
        "steps": steps_value,
        "n": n_value,
        "sampler_index": sampler_var.get(),
        "seed": seed_value,
        "cfg_scale": cfg_scale_value,
        "style": style_value
    })
    response = requests.post(url, headers=headers, params=params, data=data)

    response_data = response.json()

    if "data" in response_data:
        for i, img_data in enumerate(response_data["data"]):
            image_data = img_data["b64_image"]
            image_bytes = base64.b64decode(image_data)

            # 使用哈希函数生成文件名
            hash_object = hashlib.md5(prompt_text.encode())
            file_name = hash_object.hexdigest()[:10] + f"_{i + 1}.jpg"

            with open(file_name, "wb") as file:
                file.write(image_bytes)

            image_files.append(file_name)

            result_label.config(text=f"Image {i + 1} saved as {file_name}")
        if image_files:
            show_image(0)
    else:
        result_label.config(text="No image data found in the response.")

def toggle_password():
    if api_key_entry.cget('show') == '':
        api_key_entry.config(show='*')
        secret_key_entry.config(show='*')
    else:
        api_key_entry.config(show='')
        secret_key_entry.config(show='')

def save_config():
    config = {
        "api_key": api_key_entry.get(),
        "secret_key": secret_key_entry.get(),
        "sampler_index": sampler_var.get(),
        "size": size_var.get(),
        "n": n_var.get(),
        "steps": steps_entry.get(),
        "prompt": prompt_entry.get(),
        "negative_prompt": negative_prompt_entry.get(),
        "seed": seed_entry.get(),
        "cfg_scale": cfg_scale_entry.get(),
        "style": style_var.get()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

            # 如果缺少键，则使用默认值安全地更新每个字段
            api_key_entry.delete(0, tk.END)
            api_key_entry.insert(0, config.get("api_key", ""))

            secret_key_entry.delete(0, tk.END)
            secret_key_entry.insert(0, config.get("secret_key", ""))

            sampler_var.set(config.get("sampler_index", "DPM++ SDE Karras"))

            size_var.set(config.get("size", "1024x1024"))

            style_var.set(config.get("style","Base"))

            n_var.set(config.get("n", "1"))

            steps_entry.delete(0, tk.END)
            steps_entry.insert(0, config.get("steps", "20"))

            seed_entry.delete(0,tk.END)
            seed_entry.insert(0, str(random.randint(0, 4294967295)))  # 设置为0到4294967295的随机数

            prompt_entry.delete(0, tk.END)
            prompt_entry.insert(0, config.get("prompt", ""))

            cfg_scale_entry.delete(0, tk.END)
            cfg_scale_entry.insert(0, config.get("cfg_scale", "5"))

            negative_prompt_entry.delete(0, tk.END)
            negative_prompt_entry.insert(0, config.get("negative_prompt", ""))


        except json.JSONDecodeError:
            print("Error: Configuration file is not a valid JSON. Using default settings.")
        except Exception as e:
            print(f"Error: An unexpected error occurred while loading the configuration: {e}")
    else:
        print("No configuration file found. Using default settings.")


# Create main window
root = tk.Tk()
root.title("百度绘画模型-Stable-Diffusion-XL(目前每个免费用户有500张图片生成权限，用完还可以继续申请，快来尝试吧！！！)")
root.geometry("999x650")

# Apply a light blue theme
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', background='#add8e6')
style.configure('TFrame', background='#add8e6')
style.configure('TLabel', background='#add8e6')
style.configure('TEntry', background='#e6f0f8')

# Create frames
left_frame = ttk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10,fill=tk.BOTH)

right_frame = ttk.Frame(root)
right_frame.pack(side=tk.RIGHT, padx=10, pady=10,fill=tk.BOTH,expand=True)

root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=7)

# API Key input
api_key_label = ttk.Label(left_frame, text="API Key:")
api_key_label.grid(row=0, column=0, pady=10)
api_key_entry = ttk.Entry(left_frame, show='*')
api_key_entry.grid(row=0, column=1, pady=10)

# Secret Key input
secret_key_label = ttk.Label(left_frame, text="Secret Key:")
secret_key_label.grid(row=1, column=0, pady=10)
secret_key_entry = ttk.Entry(left_frame, show='*')
secret_key_entry.grid(row=1, column=1, pady=10)

# Show/Hide Password Checkbox
show_pass_check = ttk.Checkbutton(left_frame, text='显示/隐藏', command=toggle_password)
show_pass_check.grid(row=2, columnspan=1, pady=10)

# Sampler selection
sampler_label = ttk.Label(left_frame, text="Sampler(采样器，14种):")
sampler_label.grid(row=3, column=0, pady=10)
sampler_options = [
    "Euler", "Euler a", "DPM++ 2M", "DPM++ 2M Karras", "LMS Karras", "DPM++ SDE",
    "DPM++ SDE Karras", "DPM2 a Karras", "Heun", "DPM++ 2M SDE", "DPM2", "DPM2 Karras",
    "DPM2 a", "LMS"
]
sampler_var = tk.StringVar(root)
sampler_var.set("Euler")  # Default value
sampler_menu = ttk.Combobox(left_frame, textvariable=sampler_var, values=sampler_options, state="readonly")
sampler_menu.grid(row=3, column=1, pady=10)

# Size selection
size_label = ttk.Label(left_frame, text="Size(图片尺寸，6种):")
size_label.grid(row=4, column=0, pady=10)
size_options = ["768x768", "768x1024", "1024x768", "576x1024", "1024x576", "1024x1024"]
size_var = tk.StringVar(root)
size_var.set("1024x1024")  # Default value
size_combobox = ttk.Combobox(left_frame, textvariable=size_var, values=size_options, state="readonly")
size_combobox.grid(row=4, column=1, pady=10)

# Style selection
style_label = ttk.Label(left_frame, text="Style(图片风格，17种):")
style_label.grid(row=5, column=0, pady=10)
style_options = ["Base", "3D Model", "Analog Film", "Anime", "Cinematic", "Comic Book","Craft Clay","Digital Art","Enhance","Fantasy Art","lsometric","Line Art","Lowpoly","Neonpunk","Origami","Pixel Art","Texture"]
style_var = tk.StringVar(root)
style_var.set("Base")  # Default value
style_combobox = ttk.Combobox(left_frame, textvariable=style_var, values=style_options, state="readonly")
style_combobox.grid(row=5, column=1, pady=10)

# N selection
n_label = ttk.Label(left_frame, text="Numbers (图片数量，1-4):")
n_label.grid(row=6, column=0, pady=10)
n_options = ["1", "2", "3", "4"]
n_var = tk.StringVar(root)
n_var.set("1")  # Default value
n_menu = ttk.Combobox(left_frame,textvariable=n_var, values=n_options, state="readonly")
n_menu.grid(row=6, column=1, pady=10)

# Steps input
steps_label = ttk.Label(left_frame, text="Steps (步数，10-50):")
steps_label.grid(row=7, column=0, pady=10)
steps_entry = ttk.Entry(left_frame)
steps_entry.insert(0, "20")
steps_entry.grid(row=7, column=1, pady=10)

# Seed input
seed_label = ttk.Label(left_frame, text="Seed (随机种子，0-4294967295):")
seed_label.grid(row=8, column=0, pady=10)
seed_entry = ttk.Entry(left_frame)
seed_entry.insert(0,"str(random.randint(0, 4294967295)")
seed_entry.grid(row=8, column=1, pady=10)

# Prompt input
prompt_label = ttk.Label(left_frame, text="Prompt(提示词):")
prompt_label.grid(row=9, column=0, pady=10)
prompt_entry = ttk.Entry(left_frame)
prompt_entry.grid(row=9, column=1, pady=10)

# Cfg_scale input
cfg_scale_label = ttk.Label(left_frame, text="Cfg_scale (提示词相关性，0-30):")
cfg_scale_label.grid(row=10, column=0, pady=10)
cfg_scale_entry = ttk.Entry(left_frame)
cfg_scale_entry.insert(0, "5")
cfg_scale_entry.grid(row=10, column=1, pady=10)

# Negative Prompt input
negative_prompt_label = ttk.Label(left_frame, text="Negative Prompt(反向提示词):")
negative_prompt_label.grid(row=11, column=0, pady=10)
negative_prompt_entry = ttk.Entry(left_frame)
negative_prompt_entry.grid(row=11, column=1, pady=10)

# Generate button
generate_button = ttk.Button(left_frame, text="开始生成图片", command=on_generate_button_click)
generate_button.grid(row=12, columnspan=2, pady=20)

# Result label
result_label = ttk.Label(left_frame, text="")
result_label.grid(row=13, columnspan=2)

# 图像初始化
image_files = []
current_image_index = 0

# 图像显示
image_label = ttk.Label(right_frame)
image_label.pack()

# 图像索引
image_index_label = ttk.Label(right_frame, text="")
image_index_label.pack()

# 导航按钮
prev_button = ttk.Button(right_frame, text="<", command=previous_image)
prev_button.pack(side=tk.LEFT)

next_button = ttk.Button(right_frame, text=">", command=next_image)
next_button.pack(side=tk.RIGHT)

# 加载配置
load_config()

# 关闭窗口时保存配置
root.protocol("WM_DELETE_WINDOW", lambda: (save_config(), root.destroy()))

root.mainloop()
