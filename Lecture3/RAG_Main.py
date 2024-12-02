import os
from RAG_OfflinePath import OfflinePath  # 导入离线处理类
from RAG_OnlinePath import OnlinePath  # 导入在线问答处理类


def main():
    """
    主函数，用于构建 RAG 离线数据库并启动在线问答系统。
    """
    # 知识库文件路径，包含运动鞋相关知识
    KNOWLEDGE_FILE = "L3_Resources/运动鞋店铺知识库.txt"
    # FAISS 索引文件路径，用于存储嵌入向量索引
    FAISS_INDEX_FILE = "L3_Resources/shoes_faiss_index.index"
    # 从环境变量中获取 DashScope API 的密钥
    DASH_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    # DashScope API 的基础 URL
    DASH_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    # 使用的大语言模型的名称，例如 qwen-plus
    MODEL_NAME = "qwen-plus"
    # LLM 生成内容的最大 token 数量
    MAX_TOKENS = 300
    # LLM 生成内容的温度（控制随机性，值越高，生成内容越随机）
    TEMPERATURE = 0.7
    # 是否启用流式输出
    STREAM = True

    # Step 1: 构建 RAG 离线数据库
    print("############     构建离线数据库中...     ############")

    # 初始化 OfflinePath 对象，负责处理知识库文本、生成嵌入、创建 FAISS 索引，并将数据存入 MySQL 数据库
    offline_path = OfflinePath(
        knowledge_file=KNOWLEDGE_FILE,  # 知识库文件路径
        faiss_index_file=FAISS_INDEX_FILE,  # FAISS 索引文件路径
        api_key=DASH_API_KEY,  # DashScope API 密钥
    )

    # 开始离线处理流程
    offline_path.process()
    print("############     离线数据库构建完成！     ############")

    # Step 2: 启动 RAG 在线问答系统
    print("############     启动在线问答系统...     ############")

    # 初始化 OnlinePath 对象，负责加载 FAISS 索引、检索数据库内容并与大语言模型交互
    online_path = OnlinePath(
        faiss_index_file=FAISS_INDEX_FILE,  # FAISS 索引文件路径
        api_key=DASH_API_KEY,  # DashScope API 密钥
        model=MODEL_NAME,  # 大语言模型名称
        base_url=DASH_BASE_URL,  # DashScope API 的基础 URL
        max_tokens=MAX_TOKENS,  # LLM 回复的最大 token 数量
        temperature=TEMPERATURE,  # LLM 回复的随机性
        stream=STREAM,  # 是否启用流式输出
    )

    # 启动在线问答系统
    online_path.chat()


# 程序的入口
if __name__ == "__main__":
    main()