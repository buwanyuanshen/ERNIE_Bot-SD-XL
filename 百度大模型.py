import datetime
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import requests
import json
import os

CONFIG_FILE = "config.json"
BACKGROUND_COLOR = "#D0E0F0"
TEXT_COLOR = "#000000"
BUTTON_COLOR = "#AEC6CF"
ENTRY_BG = "#F0F8FF"
FONT = ("Arial", 10)

# 加载配置文件
def load_config():
    default_config = {
        "API_KEY": "",
        "SECRET_KEY": "",
        "temperature": 0.9,
        "top_p": 0.7,
        "penalty_score": 1.0,
        "system": "You are a helpful assistant",
        "selected_model": "ERNIE-Bot-turbo"
    }

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            default_config.update(config)
            return default_config
    else:
        return default_config

# 保存所有配置
def save_config(api_key, secret_key, selected_model, temperature, top_p, penalty_score, system):
    with open(CONFIG_FILE, "w") as file:
        config = {
            "API_KEY": api_key,
            "SECRET_KEY": secret_key,
            "selected_model": selected_model,
            "temperature": temperature,
            "top_p": top_p,
            "penalty_score": penalty_score,
            "system": system
        }
        json.dump(config, file)

def get_access_token(api_key, secret_key):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    return str(requests.post(url, params=params).json().get("access_token"))

# 在 chat_with_bot 函数中添加参数，从配置文件读取相应的值
def chat_with_bot(prompt, api_key, secret_key, model_url, temperature, top_p, penalty_score, system):
    access_token = get_access_token(api_key, secret_key)
    url = f"https://aip.baidubce.com{model_url}?access_token={access_token}"

    payload = json.dumps({
        "messages": [{"role": "user", "content": prompt}],   #部分模型必要输入参数，1.最后一个message的content长度（即此轮对话的问题）不能超过4800个字符，且不能超过2000 tokens.2.messages中content总长度大于4800个字符或2000 tokens，系统会依次遗忘最早的历史会话，直到content的总长度不超过4800个字符且不超过2000 tokens
        "stream": True,    #流式输出
        "temperature": temperature,    #（1）较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定（2）默认0.8，范围 (0, 1.0]，不能为0（3）建议该参数和top_p只设置1个（4）建议top_p和temperature不要同时更改
        "top_p": top_p,   #（1）影响输出文本的多样性，取值越大，生成文本的多样性越强（2）默认0.8，取值范围 [0, 1.0]（3）建议该参数和temperature只设置1个（4）建议top_p和temperature不要同时更改
        "penalty_score": penalty_score,   #通过对已生成的token增加惩罚，减少重复生成的现象。说明：（1）值越大表示惩罚越大（2）默认1.0，取值范围：[1.0, 2.0]
        "system": system,    #模型人设，主要用于人设设定，例如，你是xxx公司制作的AI助手，长度限制1024个字符
        "extra_parameters": {
            "use_keyword": True,
            "use_reference": True
        },    #Chatlaw必要参数第三方大模型推理高级参数，依据第三方大模型厂商不同而变化
        "prompt": prompt,    #部分模型必要输入参数，请求信息
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload, stream=True)

    replies = []
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    json_str = line_str[6:]
                    data = json.loads(json_str)
                    if 'result' in data and data['result']:
                        replies.append(data['result'])
                except json.JSONDecodeError as e:
                    print("JSON decoding error:", e)

    return "\n".join(replies).replace("\n", "")

# 传递参数
def send_message(event=None):
    api_key = api_key_entry.get()
    secret_key = secret_key_entry.get()
    user_input = user_input_entry.get("1.0", "end-1c")
    selected_model = model_var.get()

    if user_input and api_key and secret_key and selected_model:
        # 从配置文件加载参数
        config = load_config()
        temperature = config["temperature"]
        top_p = config["top_p"]
        penalty_score = config["penalty_score"]
        system = config["system"]

        # 创建一个新的线程来执行聊天请求，避免卡死
        chat_thread = threading.Thread(target=perform_chat,
                                       args=(user_input, api_key, secret_key, model_urls[selected_model],
                                             temperature, top_p, penalty_score, system))
        chat_thread.start()
        user_input_entry.delete("1.0", tk.END)

# 执行聊天请求
def perform_chat(user_input, api_key, secret_key, model_url, temperature, top_p, penalty_score, system):
    response = chat_with_bot(user_input, api_key, secret_key, model_url, temperature, top_p, penalty_score, system)
    update_chat_history("You: " + user_input + "\n" + "Bot: " + response + "\n\n")


# 更新对话消息
def update_chat_history(message):
    chat_history.config(state=tk.NORMAL)
    chat_history.insert(tk.END, message)
    chat_history.config(state=tk.DISABLED)
    chat_history.yview(tk.END)

# 保存对话消息
def save_chat_history_with_timestamp():
    """
    Save the chat history to a text file with a timestamp in the file name.
    """
    chat_content = chat_history.get("1.0", tk.END).strip()
    if chat_content:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"chat_history_{timestamp}.txt"

        with open(filename, "w") as file:
            file.write(chat_content)


# 关闭脚本时保存配置并输出对话消息
def on_closing():
    api_key = api_key_entry.get()
    secret_key = secret_key_entry.get()
    selected_model = model_var.get()
    temperature = float(temperature_entry.get())
    top_p = float(top_p_entry.get())
    penalty_score = float(penalty_score_entry.get())
    system = system_entry.get()

    save_config(api_key, secret_key, selected_model, temperature, top_p, penalty_score, system)

    chat_content = chat_history.get("1.0", tk.END)
    save_chat_history_with_timestamp()
    root.destroy()


# 隐藏密码，保护隐私
def toggle_show_hide(entry, show):
    entry.config(show="" if show.get() else "*")

# 获取对应消息
def get_last_message():
    """
    Get the last user message and bot response from the chat history.
    """
    content = chat_history.get("1.0", tk.END).strip().split("\n")
    last_user_message = ""
    last_bot_response = ""

    for line in content:
        if line.startswith("You: "):
            last_user_message = line[len("You: "):]
        elif line.startswith("Bot: "):
            last_bot_response = line[len("Bot: "):]

    return last_user_message, last_bot_response

# 复制消息
def copy_to_clipboard(text):
    """
    Copy a given text to the system clipboard.
    """
    root.clipboard_clear()
    root.clipboard_append(text)

# 复制用户消息
def copy_user_message():
    user_message, _ = get_last_message()
    copy_to_clipboard(user_message)

#复制bot消息
def copy_bot_response():
    _, bot_response = get_last_message()
    copy_to_clipboard(bot_response)

# 发送后清空输出
def clear_input():
    """
    Clear the user input field.
    """
    user_input_entry.delete("1.0", tk.END)
    chat_history.config(state=tk.NORMAL)
    chat_history.delete("1.0", tk.END)
    chat_history.config(state=tk.DISABLED)

#保存配置
def save_configurations():
    """
    Save the current API Key and Secret Key to the configuration file.
    """
    api_key = api_key_entry.get()
    secret_key = secret_key_entry.get()
    selected_model = model_var.get()
    save_config(api_key, secret_key,selected_model)
# 加载配置
config = load_config()

# 设置应用窗口
root = tk.Tk()
root.title("百度大模型(18个模型，其中5个模型官方限时免费，速来体验！！！)")
root.geometry("650x700")
root.configure(bg=BACKGROUND_COLOR)
root.protocol("WM_DELETE_WINDOW", on_closing)

# API Key输入框
api_key_label = tk.Label(root, text="API Key", bg=BACKGROUND_COLOR, font=FONT)
api_key_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
api_key_entry = tk.Entry(root, width=40, font=FONT, bg=ENTRY_BG, show="*")
api_key_entry.insert(0, config["API_KEY"])
api_key_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2)

# 隐藏API Key
show_api_key = tk.BooleanVar(value=False)
api_key_toggle = tk.Checkbutton(root, text="Show", variable=show_api_key, command=lambda: toggle_show_hide(api_key_entry, show_api_key), bg=BACKGROUND_COLOR, font=FONT)
api_key_toggle.grid(row=0, column=2, sticky="w")


# Secret Key输入框
secret_key_label = tk.Label(root, text="Secret Key", bg=BACKGROUND_COLOR, font=FONT)
secret_key_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
secret_key_entry = tk.Entry(root, width=40, font=FONT, bg=ENTRY_BG, show="*")
secret_key_entry.insert(0, config["SECRET_KEY"])
secret_key_entry.grid(row=1, column=1, padx=10, pady=5, columnspan=2)

# 隐藏Secret Key
show_secret_key = tk.BooleanVar(value=False)
secret_key_toggle = tk.Checkbutton(root, text="Show", variable=show_secret_key, command=lambda: toggle_show_hide(secret_key_entry, show_secret_key), bg=BACKGROUND_COLOR, font=FONT)
secret_key_toggle.grid(row=1, column=2, sticky="w")
# 模型网址
model_urls = {
    "ERNIE-Bot-turbo": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant",
    "ERNIE-Bot": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
    "ERNIE-Bot-4.0": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
    "ERNIE-Bot-8k": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_bot_8k",
    "ERNIE-Bot-turbo-AI原生应用工作台": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ai_apaas",
    "BLOOMZ-7B": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/bloomz_7b1",
    "Qianfan-BLOOMZ-7B-compressed": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/qianfan_bloomz_7b_compressed",
    "Llama-2-7b-chat": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_2_7b",
    "Llama-2-13b-chat": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_2_13b",
    "Llama-2-70b-chat": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/llama_2_70b",
    "Qianfan-Chinese-Llama-2-7B": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/qianfan_chinese_llama_2_7b",
    "Qianfan-Chinese-Llama-2-13B(free)": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/qianfan_chinese_llama_2_13b",
    "ChatGLM2-6B-32K": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/chatglm2_6b_32k",
    "XuanYuan-70B-Chat-4bit(free)": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/xuanyuan_70b_chat",
    "ChatLaw(free)": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/chatlaw",
    "AquilaChat-7B": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/aquilachat_7b",
    "SQLCoder-7B(free)": "/rpc/2.0/ai_custom/v1/wenxinworkshop/completions/sqlcoder_7b",
    "CodeLlama-7b-Instruct(free)": "/rpc/2.0/ai_custom/v1/wenxinworkshop/completions/codellama_7b_instruct",

}

# 设置模型及默认数值
model_var = tk.StringVar(value=config["selected_model"])
model_label = tk.Label(root, text="Selected model(选择模型)", bg=BACKGROUND_COLOR, font=FONT)
model_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
model_combobox = ttk.Combobox(root, textvariable=model_var, values=list(model_urls.keys()), state="readonly",width=29)
model_combobox.grid(row=2, column=1, padx=10, pady=5,columnspan=1)

# 温度输入框
temperature_label = tk.Label(root, text="Temperature(温度)", bg=BACKGROUND_COLOR, font=FONT)
temperature_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
temperature_entry = tk.Entry(root, width=15, font=FONT, bg=ENTRY_BG)
temperature_entry.insert(0, config["temperature"])
temperature_entry.grid(row=3, column=1, padx=10, pady=5, columnspan=1)

# 核采样输入框
top_p_label = tk.Label(root, text="Top P(核采样)", bg=BACKGROUND_COLOR, font=FONT)
top_p_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
top_p_entry = tk.Entry(root, width=15, font=FONT, bg=ENTRY_BG)
top_p_entry.insert(0, config["top_p"])
top_p_entry.grid(row=4, column=1, padx=10, pady=5, columnspan=1)

# 处罚成绩输入框
penalty_score_label = tk.Label(root, text="Penalty Score(处罚成绩)", bg=BACKGROUND_COLOR, font=FONT)
penalty_score_label.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="w")
penalty_score_entry = tk.Entry(root, width=15, font=FONT, bg=ENTRY_BG)
penalty_score_entry.insert(0, config["penalty_score"])
penalty_score_entry.grid(row=5, column=1, padx=10, pady=5, columnspan=1)

# 系统角色输入框
system_label = tk.Label(root, text="System role(系统角色)", bg=BACKGROUND_COLOR, font=FONT)
system_label.grid(row=6, column=0, padx=10, pady=(10, 0), sticky="w")
system_entry = tk.Entry(root, width=45, font=FONT, bg=ENTRY_BG)
system_entry.insert(0, config["system"])
system_entry.grid(row=6, column=1, padx=10, pady=5, columnspan=2)

# 创建一个历史对话消息框
chat_history = ScrolledText(root, state='disabled', width=85, height=15, bg=ENTRY_BG, font=FONT)
chat_history.grid(row=8, column=0, columnspan=3, padx=10, pady=10,sticky="w")

# 用户输入框
user_input_entry = tk.Text(root, height=3, width=80, bd=3, font=("Arial", 10), bg="white")
user_input_entry.grid(row=10, column=0, padx=10, pady=5, columnspan=2)
user_input_entry.bind("<Return>", lambda event: send_message())

# 发送按钮
send_button = tk.Button(root, text="发送消息", command=send_message, bg=BUTTON_COLOR, font=FONT,width=33)
send_button.grid(row=11, column=0, padx=10, pady=10,sticky="nsew",columnspan=1)

# 清空按钮
clear_button = tk.Button(root, text="清空输入", command=clear_input, bg=BUTTON_COLOR, font=FONT)
clear_button.grid(row=11, column=1, padx=10, pady=5, sticky="nsew", columnspan=1)

# 保存消息按钮
save_with_timestamp_button = tk.Button(root, text="保存对话", command=save_chat_history_with_timestamp, bg=BUTTON_COLOR, font=FONT)
save_with_timestamp_button.grid(row=12, column=0, padx=10, pady=10, sticky="nsew", columnspan=1)

# 保存配置按钮
save_config_button = tk.Button(root, text="保存配置", command=save_configurations, bg=BUTTON_COLOR, font=FONT)
save_config_button.grid(row=12, column=1, padx=10, pady=10, sticky="nsew", columnspan=1)

# 复制用户消息按钮
copy_user_message_button = tk.Button(root, text="复制用户消息", command=copy_user_message, bg=BUTTON_COLOR, font=FONT)
copy_user_message_button.grid(row=13, column=0, padx=5, pady=5,sticky="nsew")

# 复制bot信息按钮
copy_bot_response_button = tk.Button(root, text="复制bot消息", command=copy_bot_response, bg=BUTTON_COLOR, font=FONT)
copy_bot_response_button.grid(row=13, column=1, padx=5, pady=5,sticky="nsew")

# 全局定义用户/bot消息
last_user_message = ""
last_bot_response = ""

root.mainloop()