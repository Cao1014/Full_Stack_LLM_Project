import os
import traceback
import pymysql
import numpy as np
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from llama_index.vector_stores.faiss import FaissVectorStore
import faiss

# 配置文件路径
knowledge_file = "L2_Resources/运动鞋店铺知识库.txt"
faiss_index_file = "L2_Resources/shoes_shop_faiss_vector.index"
schema_file = "L2_Resources/schema.sql"
insert_sql_file = "L2_Resources/ai_context_insert.sql"

# 数据库配置
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "cao1014#",
    "database": "RAG_Shoes_Database",
    "port": 3306,
    "charset": "utf8mb4",
}


# 步骤 1：读取知识库文件
def read_knowledge_file(file_path):
    """
    读取知识库文件，将每行文本存储为列表。
    :param file_path: 知识库文件路径
    :return: 文本列表
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        knowledge_data = [line.strip() for line in lines if line.strip()]
        print(f"成功读取知识库文件，共 {len(knowledge_data)} 条记录。")
        return knowledge_data
    except FileNotFoundError:
        print(f"文件未找到，请确认路径是否正确: {file_path}")
        return []
    except Exception as e:
        print(f"读取知识库文件时发生错误：{e}")
        return []


# 步骤 2：生成向量
def generate_embeddings_with_dashscope(texts, api_key):
    """
    调用 DashScope API 生成文本向量，并打印部分嵌入值。
    :param texts: 文本列表
    :param api_key: DashScope API 密钥
    :return: 二维 numpy 数组，表示向量列表
    """
    if not api_key:
        raise ValueError("API 密钥未设置，请设置环境变量 DASHSCOPE_API_KEY。")

    embedder = DashScopeEmbedding(
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
        text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
        api_key=api_key,
    )

    embeddings = embedder.get_text_embedding_batch(texts)

    for index, embedding in enumerate(embeddings):
        if embedding is None:
            print(f"The embedding for '{texts[index]}' failed.")
        else:
            print(f"Dimension of embedding: {len(embedding)}, Values: {embedding[:5]}")

    if None in embeddings:
        failed_indices = [i for i, e in enumerate(embeddings) if e is None]
        raise ValueError(f"以下文本嵌入生成失败：{[texts[i] for i in failed_indices]}")

    return np.array(embeddings)


# 步骤 3：将向量写入 FAISS 索引
def save_to_faiss_index(embeddings, index_file):
    d = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(d)
    faiss_index.add(embeddings)

    dirpath = os.path.dirname(index_file)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath)

    vector_store = FaissVectorStore(faiss_index=faiss_index)
    vector_store.persist(index_file)
    print(f"FAISS 索引已保存至 {index_file}。")


# 步骤 4：执行 SQL 文件中的表结构创建（创建表）
def execute_create_table_sql(connection, sql_file):
    """
    执行 SQL 文件中的表结构创建语句。
    :param connection: 数据库连接
    :param sql_file: SQL 文件路径
    """
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_commands = f.read().split(";")  # 按分号拆分语句

    with connection.cursor() as cursor:
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    # 如果是 CREATE TABLE 语句，可以加入判断，跳过表已存在的错误
                    if command.lower().startswith("create table"):
                        cursor.execute(command)
                        print(f"成功执行表创建命令: {command[:50]}")
                    else:
                        continue  # 只执行 CREATE TABLE，不执行其他语句
                except pymysql.err.OperationalError as e:
                    if e.args[0] == 1050:  # 表已存在错误
                        print(f"表已存在，跳过语句: {command[:50]}")
                    else:
                        raise
        connection.commit()
    print(f"已执行表结构创建 SQL 文件：{sql_file}")


# 步骤 5：执行 SQL 文件中的数据插入（插入数据）
def execute_insert_sql(connection, sql_file):
    """
    执行 SQL 文件中的插入数据语句。
    :param connection: 数据库连接
    :param sql_file: SQL 文件路径
    """
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_commands = f.read().split(";")  # 按分号拆分语句

    with connection.cursor() as cursor:
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    if command.lower().startswith("insert into"):
                        # 提取 VALUES 部分的内容，假设 VALUES 部分只有一个字段值
                        values_part = command.split("VALUES")[1].strip(" ()")  # 去除括号
                        text_value = values_part.strip("'")  # 去除单引号

                        # 检查数据库中是否已有相同的 text
                        cursor.execute("SELECT COUNT(*) FROM ai_context WHERE text = %s", (text_value,))
                        count = cursor.fetchone()[0]

                        if count == 0:  # 如果数据库中没有相同的 text，则执行插入
                            cursor.execute(command)
                            print(f"成功执行插入命令: {command[:200]}")
                        else:
                            print(f"插入跳过：text '{text_value}' 已存在。")

                except Exception as e:
                    print(f"执行插入命令失败: {command[:50]}，错误：{e}")
                    raise
        connection.commit()
    print(f"已执行插入数据 SQL 文件：{sql_file}")


# 主流程
if __name__ == "__main__":
    try:
        # 获取 DashScope API 密钥
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("请设置环境变量 DASHSCOPE_API_KEY。")
            exit(1)

        # 读取知识库文本
        texts = read_knowledge_file(knowledge_file)
        if not texts:
            print("没有读取到任何文本，程序终止。")
            exit(1)

        # 生成向量
        embeddings = generate_embeddings_with_dashscope(texts, api_key)

        # 保存向量至 FAISS 索引
        save_to_faiss_index(embeddings, faiss_index_file)

        # 连接数据库
        connection = pymysql.connect(**db_config)

        # 执行表结构创建（schema.sql）
        execute_create_table_sql(connection, schema_file)

        # 执行数据插入（ai_context_insert.sql）
        execute_insert_sql(connection, insert_sql_file)

    except Exception as e:
        print(f"发生错误：{e}")
        traceback.print_exc()

    finally:
        if "connection" in locals() and connection.open:
            connection.close()
            print("数据库连接已关闭。")