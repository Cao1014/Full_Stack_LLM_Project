import os
import faiss
import numpy as np
from typing import List, Generator, Union  # 增加 Union 类型注解支持
from Peewee_Model import DatabaseManager, AiContext
from openai import OpenAI


class OnlinePath:
    def __init__(self, faiss_index_file: str, api_key: str, model: str, base_url: str, max_tokens=300, temperature=0.7,
                 stream=True):
        """
        初始化 OnlinePath 对象。

        :param faiss_index_file: FAISS 索引文件路径。
        :param api_key: OpenAI API 密钥。
        :param model: 使用的模型名称。
        :param base_url: OpenAI API 基础 URL。
        :param max_tokens: 最大生成 token 数。
        :param temperature: 生成温度，控制输出的随机性。
        :param stream: 是否启用流式输出。
        """
        self.faiss_index = faiss.read_index(faiss_index_file)
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.stream = stream
        self.messages = [
            {"role": "system", "content": "You are a helpful and versatile assistant."}
        ]

    def query_to_embedding(self, query: str) -> np.ndarray:
        """
        将用户查询转化为向量。
        """
        from llama_index.embeddings.dashscope import (
            DashScopeEmbedding,
            DashScopeTextEmbeddingModels,
            DashScopeTextEmbeddingType,
        )

        embedder = DashScopeEmbedding(
            model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
            text_type=DashScopeTextEmbeddingType.TEXT_TYPE_QUERY,
            api_key=os.getenv("DASHSCOPE_API_KEY"),
        )
        return np.array([embedder.get_text_embedding(query)])

    def search_faiss_index(self, query_vector: np.ndarray, top_k: int = 5) -> List[int]:
        """
        在 FAISS 索引中检索最相似的文本索引。
        """
        distances, indices = self.faiss_index.search(query_vector, top_k)
        return [idx + 1 for idx in indices[0]]

    def fetch_texts_from_database(self, indices: List[int]) -> List[str]:
        """
        从数据库中获取与索引对应的文本内容。
        """
        texts = []
        for idx in indices:
            try:
                entry = DatabaseManager.get_entry_by_id(idx)
                if entry:
                    texts.append(entry.text)
            except AiContext.DoesNotExist:
                print(f"警告: 数据库中未找到 ID 为 {idx} 的记录，已跳过。")
        return texts

    def assemble_context(self, retrieved_texts: List[str], query: str) -> str:
        """
        组装上下文，将检索的内容与用户查询整合。
        """
        context = "以下是关于知识库中检索到的相关内容：\n\n"
        for i, text in enumerate(retrieved_texts):
            context += f"{i + 1}. {text}\n"
        context += f"\n用户查询：{query}\n"
        return context

    def query_llm_stream(self, context: str) -> Generator[str, None, None]:
        """
        调用 OpenAI API 接口生成回答，支持流式输出。
        """
        messages = self.messages + [{"role": "user", "content": context}]
        try:
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            for chunk in response_stream:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content  # 返回每个数据块
        except Exception as e:
            print(f"\n调用 OpenAI 接口时出错（流式）：{e}")
            yield "对不起，当前无法生成回复。\n"

    def query_llm(self, context: str) -> str:
        """
        调用 OpenAI API 接口生成完整回答（非流式）。
        """
        messages = self.messages + [{"role": "user", "content": context}]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            full_response = response.choices[0].message.content.strip()
            self.messages.append({"role": "assistant", "content": full_response})
            return full_response
        except Exception as e:
            print(f"\n调用 OpenAI 接口时出错（非流式）：{e}")
            return "对不起，当前无法生成回复。"

    def process_query(self, query: str, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        在线处理用户查询主流程。

        :param query: 用户输入的查询。
        :param stream: 是否以流式输出方式返回。
        :return: 生成器（流式输出）或字符串（完整回复）。
        """
        query_vector = self.query_to_embedding(query)
        indices = self.search_faiss_index(query_vector)
        retrieved_texts = self.fetch_texts_from_database(indices)

        if not retrieved_texts:
            if stream:
                # 当找不到检索内容时，提供默认的流式内容
                def empty_generator():
                    yield "对不起，未能找到相关内容。\n"

                return empty_generator()
            else:
                return "对不起，未能找到相关内容。"

        context = self.assemble_context(retrieved_texts, query)

        if stream:
            # 修复：始终返回生成器对象
            return self.query_llm_stream(context)
        else:
            # 修复：始终返回字符串
            return self.query_llm(context)

    def chat(self):
        """
        启动交互式命令行聊天。
        """
        print("AI: 您好，有什么可以帮助您的吗？")
        while True:
            user_input = input("用户: ").strip()
            if not user_input:
                continue
            response = self.process_query(user_input)
            print(f"AI: {response}")


if __name__ == "__main__":
    FAISS_INDEX_FILE = "L3_Resources/shoes_faiss_index.index"
    DASH_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    DASH_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    MODEL_NAME = "qwen-plus"

    online_path = OnlinePath(
        faiss_index_file=FAISS_INDEX_FILE,
        api_key=DASH_API_KEY,
        model=MODEL_NAME,
        base_url=DASH_BASE_URL,
    )
    online_path.chat()