import os
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.core.base.llms.types import MessageRole, ChatMessage


dashscope_llm = DashScope(
    model_name=DashScopeGenerationModels.QWEN_MAX, api_key=os.environ["DASHSCOPE_API_KEY"]
)



messages = [
    ChatMessage(
        role=MessageRole.SYSTEM, content="You are a helpful assistant."
    ),
    ChatMessage(role=MessageRole.USER, content="请帮我推荐一下江浙沪5天的旅游攻略？"),
]
# 第一轮对话 流式输出
responses = dashscope_llm.stream_chat(messages)
for response in responses:
    print(response.delta, end="")
    # 添加回复到Message中
    messages.append(
        ChatMessage(role=MessageRole.ASSISTANT, content=response.message.content)
    )

messages.append(
    ChatMessage(role=MessageRole.USER, content="请问上海推荐住在哪里？")
)
# 第二轮对话
responses = dashscope_llm.stream_chat(messages)
for response in responses:
    print(response.delta, end="")
