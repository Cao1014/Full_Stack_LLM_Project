from flask import Flask, request, jsonify, render_template, Response
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
STREAM = True  # 支持流式输出

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

@app.route("/chatbot_stream", methods=["GET"])
def chatbot_stream():
    """
    流式聊天功能的 HTTP 接口。
    使用 GET 请求方式，接收以下 URL 参数：
    - message: 用户输入内容
    - historyMessages: 历史聊天记录（JSON 格式的字符串）
    :return: 流式响应生成器
    """
    try:
        # 获取 URL 参数
        user_input = request.args.get("message", "").strip()
        history_messages = eval(request.args.get("historyMessages", "[]"))

        if not user_input:
            return Response("data: Error: message cannot be empty\n\n", content_type="text/event-stream")

        # 更新对话历史
        online_path.messages = [
            {"role": "system", "content": "You are a helpful and versatile assistant."}
        ] + [{"role": "user", "content": msg} for msg in history_messages]

        # 流式生成响应内容
        def generate_response():
            for chunk in online_path.process_query(user_input, stream=True):
                # 将换行符 \n 替换为 <br> 标签
                formatted_chunk = chunk.replace("\n", "<br>")
                yield f"data: {formatted_chunk}\n\n"  # SSE 格式返回每个数据块

        return Response(generate_response(), content_type="text/event-stream")

    except Exception as e:
        print(f"Error during processing: {e}")
        return Response(f"data: Error: {str(e)}\n\n", content_type="text/event-stream")


if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(host="0.0.0.0", port=8080, debug=True)