# 百度大模型 Chat 和绘画模型 - Stable Diffusion XL 整合 README

## 百度大模型 Chat GUI

这是一个使用百度大模型进行实时聊天的图形用户界面（GUI）应用程序。用户可以与多个预训练模型进行交互，并通过调整参数来定制聊天体验。
![image](https://github.com/buwanyuanshen/ERNIE_Bot-SD-XL/assets/144007759/b759c68c-adcb-4eed-b4c2-ab0e3e0c2c78)


### 使用方法

1. 在 `config.json` 文件中配置您的百度API密钥和其他参数。
2. 运行应用程序，选择模型、调整参数，并输入聊天内容。
3. 点击“发送消息”按钮，即可查看模型的回复。
4. 可以通过清空输入、保存对话、复制消息等按钮来操作聊天记录。

### 配置文件

可以通过编辑 `config.json` 文件来配置应用程序的参数，包括API密钥、模型选择、温度、核采样等。确保在运行应用程序之前配置正确的参数。

### 依赖项安装

运行以下命令以安装应用程序所需的依赖项：

```bash
pip install -r requirements.txt
```

### 注意事项

- 请注意保护您的API密钥，不要将其存储在公共可访问的地方。
- 在使用不同的模型和参数时，可能需要适当调整温度、核采样等参数以获得最佳效果。
- 请确保您的网络连接正常，以便与百度API进行通信。

## 百度绘画模型 - Stable Diffusion XL

### 介绍

这个Python脚本允许你与百度的Stable Diffusion XL绘画模型交互，根据你提供的提示和参数生成图像。该脚本利用百度的文本到图像生成API。
![image](https://github.com/buwanyuanshen/ERNIE_Bot-SD-XL/assets/144007759/b44132a6-586f-4fac-841b-d6254c8d7742)


### 先决条件

- Python 3.x
- 必需的Python包：
  - `base64`
  - `hashlib`
  - `random`
  - `threading`
  - `tkinter`
  - `PIL`
  - `requests`
  - `json`

### 设置

1. 克隆存储库或下载Python脚本。
2. 确保已安装所需的Python包。
3. 从百度API平台获取API密钥和密钥。

### 用法

1. 在Python环境中打开脚本（例如，IDLE，Jupyter Notebook或任何代码编辑器）。
2. 运行脚本。
3. 在提示时填写API密钥和密钥。
4. 在GUI中配置参数，如提示、大小、风格等。
5. 单击“开始生成图片”按钮以启动图像生成过程。
6. 图像将保存在项目目录中。

### 配置

- 该脚本提供了配置参数的选项，如API密钥、密钥、采样器、图像大小、样式、图像数量、步数、种子、提示、cfg_scale和负提示。
- 你可以使用GUI中提供的按钮保存和加载配置设置。

### 重要提示

- 每个免费用户限制生成500张图像。在达到限制后，可以发起额外的请求。
- 确保遵守百度的服务条款和使用政策。
