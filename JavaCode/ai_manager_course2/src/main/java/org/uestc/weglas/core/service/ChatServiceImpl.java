package org.uestc.weglas.core.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.RestTemplate;
import org.uestc.weglas.core.builder.ConversationChatBuilder;
import org.uestc.weglas.core.model.Conversation;
import org.uestc.weglas.core.model.ConversationChatDetail;
import reactor.core.publisher.Flux;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * 服务实现：与 Python AI 服务交互处理聊天功能
 */
@Service
@Slf4j
public class ChatServiceImpl implements ChatService {

    @Value("${ai.chat-url:http://localhost:8080/chat}") // 普通聊天URL
    private String chatURL;

    @Value("${ai.stream-chat-url:http://localhost:8080/streamChat}") // 流式聊天URL
    private String streamChatURL;

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * 普通聊天接口：调用 Flask 服务。
     */
    @Override
    public ConversationChatDetail chat(Conversation conversation, ConversationChatDetail currentChat) {
        try {
            Map<String, Object> payload = buildPayload(conversation, currentChat);
            validatePayload(payload);

            log.info("向 Python 服务发送普通聊天请求: {}", chatURL);
            log.info("请求体: {}", payload);

            ResponseEntity<String> response = restTemplate.postForEntity(chatURL, payload, String.class);
            log.info("Python 服务响应状态码: {}", response.getStatusCodeValue());

            // 解析并返回 AI 的响应
            String aiResponseContent = parseResponseContent(response);
            return ConversationChatBuilder.buildAssistantChat(conversation, aiResponseContent);
        } catch (HttpServerErrorException httpEx) {
            log.error("Python 服务返回 500 错误，响应内容: {}", httpEx.getResponseBodyAsString());
            throw new RuntimeException("Python 服务异常 (500): " + httpEx.getMessage(), httpEx);
        } catch (Exception e) {
            log.error("调用聊天接口失败：", e);
            throw new RuntimeException("调用聊天接口失败: " + e.getMessage(), e);
        }
    }

    /**
     * 流式聊天接口：调用 Flask 服务。
     */
    @Override
    public Flux<String> streamChat(Conversation conversation, ConversationChatDetail currentChat) {
        try {
            Map<String, Object> payload = buildPayload(conversation, currentChat);
            validatePayload(payload);

            log.info("向 Python 服务发送流式聊天请求: {}", streamChatURL);
            log.info("请求体: {}", payload);

            ResponseEntity<String> response = restTemplate.postForEntity(streamChatURL, payload, String.class);
            log.info("Python 服务响应状态码: {}", response.getStatusCodeValue());

            // 假设流式聊天服务返回的内容是以换行符分割的响应
            String fullResponse = parseResponseContent(response);
            return Flux.fromArray(fullResponse.split("\n"));

        } catch (HttpServerErrorException httpEx) {
            log.error("Python 服务返回 500 错误，响应内容: {}", httpEx.getResponseBodyAsString());
            return Flux.error(new RuntimeException("流式 Python 服务异常 (500): " + httpEx.getMessage(), httpEx));
        } catch (Exception e) {
            log.error("调用流式聊天接口失败：", e);
            return Flux.error(new RuntimeException("调用流式聊天接口失败: " + e.getMessage(), e));
        }
    }

    /**
     * 构造请求体。
     */
    private Map<String, Object> buildPayload(Conversation conversation, ConversationChatDetail chat) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("message", chat.getContent()); // 用户输入
        payload.put("historyMessages", conversation.getHistoryMessages()); // 历史内容
        return payload;
    }

    /**
     * 校验参数。
     */
    private void validatePayload(Map<String, Object> payload) {
        if (payload.get("message") == null || ((String) payload.get("message")).isEmpty()) {
            throw new IllegalArgumentException("聊天输入内容不能为空！");
        }
        if (payload.get("historyMessages") == null) {
            payload.put("historyMessages", new ArrayList<>()); // 设置默认值
        }
    }

    /**
     * 解析 AI 接口的 JSON 响应。
     */
    private String parseResponseContent(ResponseEntity<String> response) {
        try {
            Map<String, Object> responseBody = objectMapper.readValue(response.getBody(), Map.class);

            if (responseBody.containsKey("responseContent")) {
                return responseBody.get("responseContent").toString(); // 提取核心内容
            } else {
                log.warn("响应中未找到 'responseContent': {}", responseBody);
                return "Python 服务未返回有效响应内容。";
            }
        } catch (Exception e) {
            log.error("解析 Python 响应 JSON 失败：", e);
            throw new RuntimeException("解析响应失败: " + e.getMessage(), e);
        }
    }
}