from flask import Flask, request, jsonify, render_template
from RAG_OnlinePath import OnlinePath
import os

# 初始化 Flask 应用
app = Flask(__name__, template_folder="HTML_Templates")

# 配置参数
FAISS_INDEX_FILE = "L3_Resources/shoes_faiss_index.index"
DASH_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASH_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"
MAX_TOKENS = 300
TEMPERATURE = 0.7
STREAM = False  # 网页不使用流式输出

# 初始化 OnlinePath 对象
online_path = OnlinePath(
    faiss_index_file=FAISS_INDEX_FILE,
    api_key=DASH_API_KEY,
    model=MODEL_NAME,
    base_url=DASH_BASE_URL,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE,
    stream=STREAM,
)

@app.route("/")
def index():
    """
    渲染聊天网页。
    """
    return render_template("chatbot.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    """
    聊天功能的 AJAX 接口，接收用户输入和历史消息。
    请求格式：
    {
        "message": "用户输入内容",
        "historyMessages": ["历史聊天内容"]
    }
    """
    try:
        # 获取 JSON 数据
        data = request.get_json()
        user_input = data.get("message", "").strip()
        history_messages = data.get("historyMessages", [])

        if not user_input:
            return jsonify({"error": "message cannot be empty"}), 400

        # 更新对话历史
        online_path.messages = [
            {"role": "system", "content": "You are a helpful and versatile assistant."}
        ] + [{"role": "user", "content": msg} for msg in history_messages]

        # 处理用户输入并生成回复
        response = online_path.process_query(user_input)

        # 返回结果
        return jsonify({"response": response}), 200

    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=8080, debug=True)