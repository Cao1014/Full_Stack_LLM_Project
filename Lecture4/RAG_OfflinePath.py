import os
import faiss
import numpy as np
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from Peewee_Model import DatabaseManager, AiContext


class OfflinePath:
    def __init__(self, knowledge_file, faiss_index_file, api_key):
        self.knowledge_file = knowledge_file
        self.faiss_index_file = faiss_index_file
        self.embedder = DashScopeEmbedding(
            model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
            text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
            api_key=api_key,
        )

    def read_knowledge_file(self):
        """
        从文件中读取知识库数据
        """
        with open(self.knowledge_file, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines() if line.strip()]

    def generate_embeddings(self, texts):
        """
        调用 DashScope API 生成文本嵌入
        """
        return np.array(self.embedder.get_text_embedding_batch(texts))

    def save_to_faiss(self, embeddings):
        """
        保存嵌入到 FAISS 索引
        """
        d = embeddings.shape[1]
        faiss_index = faiss.IndexFlatL2(d)
        faiss_index.add(embeddings)
        faiss.write_index(faiss_index, self.faiss_index_file)
        print(f"FAISS 索引已保存至 {self.faiss_index_file}。")

    def insert_to_database(self, texts):
        """
        插入数据到 MySQL 数据库
        """
        for text in texts:
            if not DatabaseManager.get_all_entries().where(AiContext.text == text).exists():
                DatabaseManager.create_entry(text)

    def process(self):
        """
        执行离线处理主流程
        """
        texts = self.read_knowledge_file()
        embeddings = self.generate_embeddings(texts)
        self.save_to_faiss(embeddings)
        self.insert_to_database(texts)


# 配置与执行
if __name__ == "__main__":
    offline_path = OfflinePath(
        knowledge_file="L3_Resources/运动鞋店铺知识库.txt",
        faiss_index_file="L3_Resources/shoes_faiss_index.index",
        api_key=os.getenv("DASHSCOPE_API_KEY")
    )
    offline_path.process()