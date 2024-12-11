package org.uestc.weglas.core.service;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.stereotype.Service;
import org.uestc.weglas.core.model.Conversation;
import org.uestc.weglas.core.model.ConversationChatDetail;
import reactor.core.publisher.Flux;

@Service
public class ChatServiceImpl implements ChatService {

    private final Logger logger = LogManager.getLogger(ChatServiceImpl.class);

    /**
     * 生成聊天回复
     * @param conversation 历史会话
     * @param currentChat 当前会话
     * @return AI的回复
     */
    @Override
    public ConversationChatDetail chat(Conversation conversation, ConversationChatDetail currentChat) {
        // 简单模拟生成AI回复的一种实现逻辑
        ConversationChatDetail aiReply = new ConversationChatDetail();
        aiReply.setConversationId(conversation.getId());
        aiReply.setRole("ASSISTANT");
        aiReply.setType("TEXT");
        aiReply.setContent("这是一个简单的自动回复。");

        // 添加到会话的聊天列表中
        conversation.getChatList().add(aiReply);

        return aiReply;
    }

    /**
     * 流式读取聊天记录
     * @param conversation 会话
     * @param userChat 用户输入chat
     * @return 流式返回文本
     */
    @Override
    public Flux<String> streamChat(Conversation conversation, ConversationChatDetail userChat) {
        // 示例性实现，返回用户聊天内容以模拟流
        return Flux.just("流式响应: 你的消息是: " + userChat.getContent());
    }
}