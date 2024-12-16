package org.uestc.weglas.core.service;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.uestc.weglas.core.model.Conversation;
import org.uestc.weglas.core.model.ConversationChatDetail;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
public class ChatServiceImpl implements ChatService {

    private final Logger logger = LogManager.getLogger(ChatServiceImpl.class);

    private final WebClient webClient = WebClient.create();

    @Value("${spring.ai.chat-url}")
    private String chatUrl;

    @Value("${spring.ai.stream-chat-url}")
    private String streamChatUrl;

    @Override
    public ConversationChatDetail chat(Conversation conversation, ConversationChatDetail currentChat) {
        try {
            logger.info("调用普通 AI 服务开始... URL: {}", chatUrl);

            String userMessage = currentChat.getContent();

            // 如果 bodyValue 不兼容，使用 body(Mono.just(...))
            String aiResponse = webClient
                    .post()
                    .uri(chatUrl)
                    .body(Mono.just(userMessage), String.class) // 替代 bodyValue(userMessage)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            ConversationChatDetail aiReply = new ConversationChatDetail();
            aiReply.setConversationId(conversation.getId());
            aiReply.setRole("ASSISTANT");
            aiReply.setType("TEXT");
            aiReply.setContent(aiResponse);

            logger.info("AI普通服务调用成功，回复内容: {}", aiResponse);

            return aiReply;
        } catch (Exception e) {
            logger.error("调用普通 AI 服务失败: {}", e.getMessage(), e);
            return buildErrorResponse(conversation, "AI服务暂时不可用，请稍后重试。");
        }
    }

    @Override
    public Flux<String> streamChat(Conversation conversation, ConversationChatDetail userChat) {
        try {
            logger.info("调用流式 AI 服务开始... URL: {}", streamChatUrl);

            return webClient
                    .post()
                    .uri(streamChatUrl)
                    .body(Mono.just(userChat.getContent()), String.class) // 替代 bodyValue(userChat.getContent())
                    .retrieve()
                    .bodyToFlux(String.class)
                    .map(response -> {
                        logger.debug("流式响应部分数据: {}", response);
                        return response;
                    });
        } catch (Exception e) {
            logger.error("调用流式 AI 服务失败: {}", e.getMessage(), e);
            return Flux.error(new RuntimeException("流式AI服务暂时不可用，请稍后重试。"));
        }
    }

    private ConversationChatDetail buildErrorResponse(Conversation conversation, String errorMessage) {
        ConversationChatDetail errorResponse = new ConversationChatDetail();
        errorResponse.setConversationId(conversation.getId());
        errorResponse.setRole("ASSISTANT");
        errorResponse.setType("TEXT");
        errorResponse.setContent(errorMessage);
        return errorResponse;
    }
}