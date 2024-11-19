import os
from openai import OpenAI
from typing import List

# 初始化 DashScope 兼容的 OpenAI 客户端
def initialize_client(api_key: str, base_url: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url)

# 使用 LLM 判断用户是否想结束对话
def check_end_conversation(client, model: str, user_message: str) -> bool:
    # 提供一个简洁的 prompt，让模型判断用户意图
    system_prompt = "You are a helpful assistant. Your task is to determine if the user intends to end the conversation."
    prompt_message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Does the user want to end the conversation? Message: '{user_message}'"},
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=prompt_message,
            max_tokens=10
        )
        decision = response.choices[0].message.content.strip().lower()
        return "yes" in decision or "true" in decision
    except Exception as e:
        print(f"检查用户意图时发生错误：{e}")
        return False

# 流式生成模型的回复
def generate_streamed_response(client, model: str, messages: List[dict]) -> str:
    try:
        response_stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        full_response = ""
        for response in response_stream:
            delta = response.choices[0].delta
            if delta and delta.content:  # 确保 delta 内容不为空
                print(delta.content, end="", flush=True)  # 只输出 content
                full_response += delta.content  # 累积 content
        print()  # 换行
        return full_response
    except Exception as e:
        print(f"\n发生错误：{e}")
        return "对不起，当前无法生成回复。"

# 主对话逻辑
def chat_loop(client, model: str):
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    print("AI: 您好，有什么可以帮助您的吗？")

    while True:
        # 获取用户输入
        user_input = input("用户: ").strip()
        if not user_input:
            continue  # 跳过空输入

        # 检测是否结束对话
        if check_end_conversation(client, model, user_input):
            print("AI: 感谢您的咨询，再见!")
            break

        # 将用户输入添加到消息列表
        messages.append({'role': 'user', 'content': user_input})

        # 生成流式输出的模型回复
        print("AI: ", end="")
        assistant_response = generate_streamed_response(client, model, messages)
        # 将助手回复添加到消息列表
        messages.append({'role': 'assistant', 'content': assistant_response})

# 主程序入口
if __name__ == "__main__":
    # 环境变量中的 API Key
    DASH_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    DASH_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    MODEL_NAME = "qwen-plus"

    # 初始化客户端
    client = initialize_client(api_key=DASH_API_KEY, base_url=DASH_BASE_URL)

    # 启动多轮对话
    chat_loop(client, model=MODEL_NAME)