import os
import traceback
import pymysql
import numpy as np
import faiss
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from llama_index.vector_stores.faiss import FaissVectorStore


class KnowledgeBaseProcessor:
    def __init__(self, config):
        """
        初始化知识库处理器
        :param config: 配置字典，包括文件路径和数据库配置
        """
        self.knowledge_file = config["knowledge_file"]
        self.faiss_index_file = config["faiss_index_file"]
        self.schema_file = config["schema_file"]
        self.insert_sql_file = config["insert_sql_file"]
        self.db_config = config["db_config"]
        self.api_key = os.getenv("DASHSCOPE_API_KEY")

        if not self.api_key:
            raise ValueError("API 密钥未设置，请设置环境变量 DASHSCOPE_API_KEY。")

        self.embedder = DashScopeEmbedding(
            model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
            text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
            api_key=self.api_key,
        )

    def read_knowledge_file(self):
        """
        读取知识库文件，将每行文本存储为列表
        :return: 文本列表
        """
        try:
            with open(self.knowledge_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            knowledge_data = [line.strip() for line in lines if line.strip()]
            print(f"成功读取知识库文件，共 {len(knowledge_data)} 条记录。")
            return knowledge_data
        except FileNotFoundError:
            print(f"文件未找到，请确认路径是否正确: {self.knowledge_file}")
            return []
        except Exception as e:
            print(f"读取知识库文件时发生错误：{e}")
            return []

    def generate_embeddings(self, texts):
        """
        调用 DashScope API 生成文本向量
        :param texts: 文本列表
        :return: 二维 numpy 数组，表示向量列表
        """
        embeddings = self.embedder.get_text_embedding_batch(texts)

        for index, embedding in enumerate(embeddings):
            if embedding is None:
                print(f"The embedding for '{texts[index]}' failed.")
            else:
                print(f"Dimension of embedding: {len(embedding)}, Values: {embedding[:5]}")

        if None in embeddings:
            failed_indices = [i for i, e in enumerate(embeddings) if e is None]
            raise ValueError(f"以下文本嵌入生成失败：{[texts[i] for i in failed_indices]}")

        return np.array(embeddings)

    def save_to_faiss_index(self, embeddings):
        """
        保存向量到 FAISS 索引
        :param embeddings: 向量列表
        """
        d = embeddings.shape[1]
        faiss_index = faiss.IndexFlatL2(d)
        faiss_index.add(embeddings)

        dirpath = os.path.dirname(self.faiss_index_file)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath)

        vector_store = FaissVectorStore(faiss_index=faiss_index)
        vector_store.persist(self.faiss_index_file)
        print(f"FAISS 索引已保存至 {self.faiss_index_file}。")

    def execute_sql_file(self, connection, sql_file, check_existing=True):
        """
        执行 SQL 文件
        :param connection: 数据库连接
        :param sql_file: SQL 文件路径
        :param check_existing: 是否检查重复数据
        """
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_commands = f.read().split(";")

        with connection.cursor() as cursor:
            for command in sql_commands:
                command = command.strip()
                if command:
                    try:
                        if command.lower().startswith("insert into") and check_existing:
                            # 提取 VALUES 部分的内容
                            values_part = command.split("VALUES")[1].strip(" ()")
                            text_value = values_part.strip("'")
                            cursor.execute("SELECT COUNT(*) FROM ai_context WHERE text = %s", (text_value,))
                            count = cursor.fetchone()[0]

                            if count == 0:
                                cursor.execute(command)
                                print(f"成功执行插入命令: {command[:200]}")
                            else:
                                print(f"插入跳过：text '{text_value}' 已存在。")
                        else:
                            cursor.execute(command)
                            print(f"成功执行 SQL 命令: {command[:200]}")

                    except Exception as e:
                        print(f"执行 SQL 命令失败: {command[:50]}，错误：{e}")
                        raise
            connection.commit()
        print(f"已执行 SQL 文件：{sql_file}")

    def process(self):
        """
        主流程，执行知识库的处理
        """
        try:
            # 读取知识库
            texts = self.read_knowledge_file()
            if not texts:
                print("没有读取到任何文本，程序终止。")
                return

            # 生成向量
            embeddings = self.generate_embeddings(texts)

            # 保存向量至 FAISS 索引
            self.save_to_faiss_index(embeddings)

            # 连接数据库
            connection = pymysql.connect(**self.db_config)

            # 执行表结构创建
            self.execute_sql_file(connection, self.schema_file, check_existing=False)

            # 执行数据插入
            self.execute_sql_file(connection, self.insert_sql_file, check_existing=True)

        except Exception as e:
            print(f"发生错误：{e}")
            traceback.print_exc()

        finally:
            if "connection" in locals() and connection.open:
                connection.close()
                print("数据库连接已关闭。")


if __name__ == "__main__":
    config = {
        "knowledge_file": "L2_Resources/运动鞋店铺知识库.txt",
        "faiss_index_file": "L2_Resources/shoes_shop_faiss_vector.index",
        "schema_file": "L2_Resources/schema.sql",
        "insert_sql_file": "L2_Resources/ai_context_insert.sql",
        "db_config": {
            "host": "localhost",
            "user": "root",
            "password": "cao1014#",
            "database": "RAG_Shoes_Database",
            "port": 3306,
            "charset": "utf8mb4",
        },
    }
    processor = KnowledgeBaseProcessor(config)
    processor.process()