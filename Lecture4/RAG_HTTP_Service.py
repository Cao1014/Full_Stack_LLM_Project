from flask import Flask, request, jsonify, render_template
from RAG_OnlinePath import OnlinePath
import os

# 初始化 Flask 应用
app = Flask(__name__, template_folder="HTML_Templates")

# 配置参数
FAISS_INDEX_FILE = "L3_Resources/shoes_faiss_index.index"
DASH_API_KEY = os.getenv("DASHSCOPE_API_KEY")  # 从环境变量获取 API 密钥
DASH_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-plus"
MAX_TOKENS = 300
TEMPERATURE = 0.7

# 初始化 OnlinePath 对象
online_path = OnlinePath(
    faiss_index_file=FAISS_INDEX_FILE,
    api_key=DASH_API_KEY,
    model=MODEL_NAME,
    base_url=DASH_BASE_URL,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE,
    stream=False,  # 不在初始化时设置流式输出
)

@app.route("/")
def index():
    """
    渲染聊天网页。
    """
    return render_template("chatbot.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    普通聊天接口：返回完整问答。
    """
    try:
        # 从 POST 请求体中解析数据
        data = request.get_json()
        user_input = data.get("message", "").strip()
        history_messages = data.get("historyMessages", [])

        # 参数校验
        if not user_input:
            return jsonify({"error": "message cannot be empty"}), 400

        # 构建对话历史
        online_path.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ] + [{"role": "user", "content": msg} for msg in history_messages]

        # 调用 AI 模型生成完整输出
        result = online_path.process_query(user_input, stream=False)

        # 确保返回值是字符串或其他可序列化对象
        if not isinstance(result, (str, list, dict)):
            raise ValueError("process_query returned an unserializable type.")

        return jsonify({"responseContent": result})  # 返回 JSON 格式的响应内容

    except Exception as e:
        # 捕获异常并返回信息
        return jsonify({"error": "Exception: " + str(e)}), 500


@app.route("/streamChat", methods=["POST"])
def stream_chat():
    """
    流式聊天接口：返回逐步生成的问答。
    """
    try:
        # 从 POST 请求体中解析数据
        data = request.get_json()
        user_input = data.get("message", "").strip()
        history_messages = data.get("historyMessages", [])

        # 参数校验
        if not user_input:
            return jsonify({"error": "message cannot be empty"}), 400

        # 构建对话历史
        online_path.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ] + [{"role": "user", "content": msg} for msg in history_messages]

        # 调用 AI 模型并开启流式模式
        generator_response = online_path.process_query(user_input, stream=True)

        # 将生成器的内容逐一读取并组合为完整的字符串
        full_response = ""
        try:
            for chunk in generator_response:
                full_response += chunk  # 累加生成器的每一部分内容
        except Exception as e:
            # 捕获生成器迭代中的异常
            raise ValueError("Error while processing generator: " + str(e))

        # 确保生成的内容是字符串
        if not isinstance(full_response, str):
            raise ValueError("The generated response is not a serializable string.")

        return jsonify({"responseContent": full_response})

    except Exception as e:
        # 捕获异常并返回信息
        return jsonify({"error": "Exception: " + str(e)}), 500


if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=8080, debug=True)