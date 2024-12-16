from peewee import *
import atexit

# 数据库连接
db = MySQLDatabase(
    database="RAG_Shoes_Database",
    user="root",
    password="cao1014#",
    host="localhost",
    port=3306
)

# 定义 ORM 模型类
class AiContext(Model):
    id = AutoField()  # 主键自动递增
    text = TextField()  # 文本字段

    class Meta:
        database = db
        table_name = "ai_context"

# 确保数据库连接
db.connect()

# 注册关闭连接的钩子
atexit.register(lambda: db.close())


class DatabaseManager:
    @staticmethod
    def create_entry(text):
        return AiContext.create(text=text)

    @staticmethod
    def get_all_entries():
        return AiContext.select()

    @staticmethod
    def get_entry_by_id(entry_id: int) -> AiContext:
        """
        根据 ID 获取单个数据库记录。
        """
        try:
            return AiContext.get(AiContext.id == entry_id)
        except DoesNotExist:
            raise AiContext.DoesNotExist(f"未找到 ID 为 {entry_id} 的记录")

    @staticmethod
    def update_entry(entry_id, new_text):
        entry = AiContext.get(AiContext.id == entry_id)
        entry.text = new_text
        entry.save()

    @staticmethod
    def delete_entry(entry_id):
        entry = AiContext.get(AiContext.id == entry_id)
        entry.delete_instance()