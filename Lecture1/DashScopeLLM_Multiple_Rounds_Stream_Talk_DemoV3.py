import os

from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.core.base.llms.types import MessageRole, ChatMessage

# 初始化DashScope LLM
dashscope_llm = DashScope(
    model_name=DashScopeGenerationModels.QWEN_MAX, api_key=os.environ["DASHSCOPE_API_KEY"]
)

# 定义结束对话的检测函数
def check_end_conversation(user_message):
    end_phrases = ["结束", "再见", "拜拜", "谢谢"]  # 关键字，用户输入包含这些词语表示结束对话
    return any(phrase in user_message for phrase in end_phrases)

# 初始化消息列表
messages = [
    ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant.")
]

# 初始提示语
print("AI: 您好，有什么可以帮助你的吗？\n")

# 多轮对话循环
while True:
    # 获取用户输入
    user_message = input("用户: ")

    # 添加用户消息到消息列表
    messages.append(ChatMessage(role=MessageRole.USER, content=user_message))

    # 检查是否要结束对话
    if check_end_conversation(user_message):
        print("AI: 感谢您的咨询，再见!\n")
        break

    # 流式输出AI的回复
    print("AI: ", end="")  # 每次AI回复前加上"AI: "
    responses = dashscope_llm.stream_chat(messages)
    assistant_response = ""  # 用于累积AI的完整回复
    for response in responses:
        print(response.delta, end="")  # 实现流式输出
        assistant_response += response.delta  # 累积完整回复内容
    print("\n")  # AI回复结束后换行

    # 将AI回复加入消息列表，保持上下文
    messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=assistant_response))