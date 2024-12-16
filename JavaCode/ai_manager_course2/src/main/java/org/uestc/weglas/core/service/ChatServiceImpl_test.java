//package org.uestc.weglas.core.service;
//
//import com.fasterxml.jackson.databind.ObjectMapper;
//import lombok.extern.slf4j.Slf4j;
//import org.springframework.beans.factory.annotation.Autowired;
//import org.springframework.beans.factory.annotation.Value;
//import org.springframework.http.HttpMethod;
//import org.springframework.http.MediaType;
//import org.springframework.http.ResponseEntity;
//import org.springframework.stereotype.Service;
//import org.springframework.web.client.RestTemplate;
//import org.uestc.weglas.core.builder.ConversationChatBuilder;
//import org.uestc.weglas.core.model.Conversation;
//import org.uestc.weglas.core.model.ConversationChatDetail;
//import reactor.core.publisher.Flux;
//
//import java.io.BufferedReader;
//import java.io.InputStreamReader;
//import java.util.Map;
//
//
///**
// * @author yingxian.cyx
// * @date Created in 2024/12/10
// */
//@Service
//@Slf4j
//public class ChatServiceImpl implements ChatService {
//
//    @Value("${ai.host.url:http://localhost:8080}")
//    private String aiHostURL;
//
//    @Value("${ai.chat.url:http://localhost:8080/chat}")
//    private String chatURL;
//
//    @Value("${ai.stream-chat.url:http://localhost:8080/streamChat}")
//    private String streamChatURL;
//
//    @Autowired
//    private ConversationService conversationService;
//
//    @Override
//    public ConversationChatDetail chat(Conversation conversation, ConversationChatDetail currentChat) {
//        try {
//            // 构造请求体
//            Map<String, Object> payload = buildPayload(conversation, currentChat);
//
//            // 调用 Python 的 HTTP 接口
//            ResponseEntity<String> response = new RestTemplate().postForEntity(chatURL, payload, String.class);
//
//            // 将响应结果转为 ConversationChatDetail 对象
//            ConversationChatDetail assistantChat = parseResponse(response);
//
//            // 记录和返回 AI 回复
//            return ConversationChatBuilder.buildAssistantChat(conversation, assistantChat);
//        } catch (Exception e) {
//            log.error("调用聊天接口失败：", e);
//            throw new RuntimeException("聊天接口调用失败", e);
//        }
//    }
//
//    @Override
//    public Flux<String> streamChat(Conversation conversation, ConversationChatDetail userchat) {
//        try {
//            // 构造请求体
//            Map<String, Object> payload = buildPayload(conversation, userchat);
//
//            // 通过 Flux 创建流式响应
//            return Flux.create(emitter -> {
//                new RestTemplate().execute(streamChatURL, HttpMethod.POST, request -> {
//                    request.getHeaders().setContentType(MediaType.APPLICATION_JSON);
//                    new ObjectMapper().writeValue(request.getBody(), payload);
//                }, response -> {
//                    BufferedReader reader = new BufferedReader(new InputStreamReader(response.getBody()));
//                    String line;
//                    while ((line = reader.readLine()) != null) {
//                        emitter.next(line); // 将每一行流式发送到前端
//                    }
//                    emitter.complete(); // 完成流
//                    return null; // 响应处理完毕
//                });
//            });
//        } catch (Exception e) {
//            log.error("调用流式聊天接口失败：", e);
//            return Flux.error(e); // Flux 中返回异常
//        }
//    }
//
//    private Map<String, Object> buildPayload(Conversation conversation, ConversationChatDetail chat) {
//        Map<String, Object> payload = new HashMap<>();
//        payload.put("conversationId", conversation.getId());
//        payload.put("userInput", chat.getMessage()); // 用户输入的聊天内容
//        return payload;
//    }
//
//    private ConversationChatDetail parseResponse(ResponseEntity<String> response) {
//        try {
//            // 假设请求返回的是 JSON 结构
//            return new ObjectMapper().readValue(response.getBody(), ConversationChatDetail.class);
//        } catch (Exception e) {
//            log.error("解析聊天响应失败：", e);
//            throw new RuntimeException("聊天响应解析失败", e);
//        }
//    }
//}
//
