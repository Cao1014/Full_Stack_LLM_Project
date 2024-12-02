import os
import faiss
import numpy as np
from typing import List
from Peewee_Model import DatabaseManager, AiContext
from openai import OpenAI


class OnlinePath:
    def __init__(self, faiss_index_file: str, api_key: str, model: str, base_url: str, max_tokens=300, temperature=0.7, stream=True):
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
        distances, indices = self.faiss_index.search(query_vector, top_k)
        return [idx + 1 for idx in indices[0]]

    def fetch_texts_from_database(self, indices: List[int]) -> List[str]:
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
        context = "以下是关于知识库中检索到的相关内容：\n\n"
        for i, text in enumerate(retrieved_texts):
            context += f"{i + 1}. {text}\n"
        context += f"\n用户查询：{query}\n"
        return context

    def query_llm(self, context: str) -> str:
        messages = self.messages + [{"role": "user", "content": context}]
        try:
            response_stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=self.stream,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            full_response = ""
            print("AI: ", end="", flush=True)
            for chunk in response_stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    print(delta.content, end="", flush=True)
                    full_response += delta.content
            print()  # 换行
            self.messages.append({"role": "assistant", "content": full_response})
            return full_response
        except Exception as e:
            print(f"\n调用 OpenAI 接口时出错：{e}")
            return "对不起，当前无法生成回复。"

    def check_end_conversation(self, user_message: str) -> bool:
        prompt_message = [
            {"role": "system",
             "content": "You are a helpful assistant. Your task is to determine if the user intends to end the conversation."},
            {"role": "user", "content": f"Does the user want to end the conversation? Message: '{user_message}'"},
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=prompt_message,
                max_tokens=10,
            )
            decision = response.choices[0].message.content.strip().lower()
            return "yes" in decision or "true" in decision
        except Exception as e:
            print(f"检查用户意图时发生错误：{e}")
            return False

    def chat(self):
        print("AI: 您好，有什么可以帮助您的吗？")
        while True:
            user_input = input("用户: ").strip()
            if not user_input:
                continue
            if self.check_end_conversation(user_input):
                print("AI: 感谢您的咨询，再见!")
                break
            self.process_query(user_input)

    def process_query(self, query: str) -> str:
        query_vector = self.query_to_embedding(query)
        indices = self.search_faiss_index(query_vector)
        retrieved_texts = self.fetch_texts_from_database(indices)

        if not retrieved_texts:
            return "对不起，未能找到相关内容。"

        context = self.assemble_context(retrieved_texts, query)
        return self.query_llm(context)


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