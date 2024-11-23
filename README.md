# Full_Stack_LLM_Project


>《基于AI大模型的前后端应用开发》课程仓库 by *Cao Zhengyang*

## Lecture1 Qwen Chat Bot

![img_v3_02gj_adebf020-a837-4d6f-8478-844514d4394g](https://github.com/user-attachments/assets/fbe54e38-bd35-4de3-9d9e-30f50d50c3de)

【参考文档】

环境确认：https://help.aliyun.com/zh/model-studio/getting-started/first-api-call-to-qwen

API参考：https://help.aliyun.com/zh/model-studio/developer-reference/dashscopellm

### Lecture1 Demo:

- [x] Please run `Qwen_ChatBot_Homework_DemoV4.py` to start multiple conversations. :tada:
- [x] Support streaming output. :tada:
- [x] When the user enters words such as "今天就聊到这吧，不想继续了", return "感谢您的咨询，再见!". :tada:

![img.png](Lecture1/Qwen chat bot流式输出.png)




## Lecture2 RAG Offline

![离线链路1-2.png](Lecture2/L2_Resources/%E7%A6%BB%E7%BA%BF%E9%93%BE%E8%B7%AF1-2.png)
![离线链路3-4.png](Lecture2/L2_Resources/%E7%A6%BB%E7%BA%BF%E9%93%BE%E8%B7%AF3-4.png)

【参考文档】

1. DashScopeEmbedding: https://docs.llamaindex.ai/en/stable/api_reference/embeddings/dashscope/
2. DashScopeEmbedding的应用：https://help.aliyun.com/zh/model-studio/developer-reference/dashscopeembedding
3. faiss: https://docs.llamaindex.ai/en/v0.10.23/api_reference/storage/vector_store/faiss/

### Lecture2 Demo:
- [x] 下载并配置MySQL。 :tada:
```
在终端输入命令
cd /usr/local/mysql

sudo vim .bash_profile

需要输入root用户密码。sudo是使用root用户修改环境变量文件。
进入编辑器后，我们先按"i”，即切换到“插入”状态。就可以通过上下左右移动光标，或空格、退格及回车等进行编辑内容了，和WINDOWS是一样的了。
文档的最下方输入：
export PATH=${PATH}:/usr/local/mysql/bin

然后按Esc退出insert状态，并在最下方输入:wq保存退出(或直接按shift+zz，或者切换到大写模式按ZZ，就可以保存退出了)。
输入：
source .bash_profile
回车执行，运行环境变量。

再输入mysql命令，即可使用。
mysql -uroot -p
```

- [x] 使用SQL常用命令，创建一个名为"RAG_Shoes_Database"的数据库。 :tada:
```
-- 创建一个名为 `my_database` 的自定义数据库
CREATE DATABASE my_database;

-- 查看当前数据库列表，检查 `my_database` 是否创建成功
SHOW DATABASES;

-- 使用刚刚创建的数据库
USE my_database;

-- 如果需要，可以在 `my_database` 数据库中创建一个表（示例）
CREATE TABLE my_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 检查数据库中的表
SHOW TABLES;

-- 插入一条示例数据到表中
INSERT INTO my_table (name) VALUES ('Example Name');

-- 查询表中数据
SELECT * FROM my_table;
```

- [x] 运行脚本`RAG_Offline.py`从而执行 `schema.sql`在RAG_Shoes_Database中创建名为"ai_context"的table，
再执行`ai_context_insert.sql`往table中插入数据，如下图MySQL终端所示。 :tada:
![RAG_Shoes_Database图片.png](Lecture2/L2_Resources/RAG_Shoes_Database%E5%9B%BE%E7%89%87.png)

- [x] 运行脚本`01_write_to_faiss_test.py`，测试向量写入 FAISS 索引的效果。 :tada:
![faiss测试结果图片.png](Lecture2/L2_Resources/faiss%E6%B5%8B%E8%AF%95%E7%BB%93%E6%9E%9C%E5%9B%BE%E7%89%87.png)
