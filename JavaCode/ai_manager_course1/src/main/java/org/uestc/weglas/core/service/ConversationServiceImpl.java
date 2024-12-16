package org.uestc.weglas.core.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.uestc.weglas.base.entity.ConversationChatDetailEntity;
import org.uestc.weglas.base.entity.ConversationEntity;
import org.uestc.weglas.base.mapper.ConversationChatDetailMapper;
import org.uestc.weglas.base.mapper.ConversationMapper;
import org.uestc.weglas.core.builder.ConversationChatBuilder;
import org.uestc.weglas.core.converter.ConversationChatDetailConverter;
import org.uestc.weglas.core.converter.ConversationConverter;
import org.uestc.weglas.core.model.Conversation;
import org.uestc.weglas.core.model.ConversationChatDetail;
import reactor.core.publisher.Flux;

import java.util.List;

/**
 * Conversation 服务实现类.
 * 管理会话、聊天记录，并集成AI接口访问.
 *
 * @author
 * @date Created in 2024/10/11
 */
@Service
@Slf4j
public class ConversationServiceImpl implements ConversationService {

    @Autowired
    private ConversationMapper conversationMapper;

    @Autowired
    private ConversationChatDetailMapper conversationChatDetailMapper;

    @Autowired
    private ChatService chatService; // 注入ChatService以调用AI服务

    /**
     * 新建会话，包括新建一条conversation记录+初始chat_detail记录
     * @param conversation 会话对象
     */
    @Override
    @Transactional
    public void add(Conversation conversation) {
        ConversationEntity entity = ConversationConverter.convert(conversation);
        conversationMapper.insert(entity);
        conversation.setId(entity.getId());

        if (conversation.getChatList() != null && !conversation.getChatList().isEmpty()) {
            for (ConversationChatDetail chatDetail : conversation.getChatList()) {
                chatDetail.setConversationId(entity.getId());
                addChat(chatDetail); // 添加用户输入的聊天记录
            }
        } else {
            ConversationChatDetail defaultChat = ConversationChatBuilder.buildDefaultChat(conversation);
            addChat(defaultChat); // 添加默认聊天记录
        }
    }

    /**
     * 查询单条会话.
     * @param conversationId 会话ID
     * @return 会话详情，包含聊天记录列表
     */
    @Override
    public Conversation queryById(Integer conversationId) {
        ConversationEntity conversationEntity = conversationMapper.selectById(conversationId);
        if (conversationEntity == null) {
            return null;
        }

        Conversation conversation = ConversationConverter.convert(conversationEntity);

        List<ConversationChatDetailEntity> chatDetailEntities = conversationChatDetailMapper.selectByConversationId(conversationId);
        List<ConversationChatDetail> chatList = ConversationChatDetailConverter.convert(chatDetailEntities);

        conversation.setChatList(chatList);

        return conversation;
    }

    /**
     * 查询所有会话列表.
     * @return 会话列表
     */
    @Override
    public List<Conversation> queryAll() {
        List<ConversationEntity> conversationEntities = conversationMapper.selectAll();
        List<Conversation> conversations = ConversationConverter.convert(conversationEntities);

        for (Conversation conversation : conversations) {
            List<ConversationChatDetailEntity> chatDetails = conversationChatDetailMapper.selectByConversationId(conversation.getId());
            List<ConversationChatDetail> chatList = ConversationChatDetailConverter.convert(chatDetails);
            conversation.setChatList(chatList);
        }

        return conversations;
    }

    /**
     * 新建一条chat_detail记录，并调用AI接口补充AI回复.
     * 调用 `/chat` 接口生成普通AI回复，并存储.
     * @param chat 用户输入的聊天记录
     */
    @Override
    @Transactional
    public void addChat(ConversationChatDetail chat) {
        // 插入用户消息
        ConversationChatDetailEntity chatEntity = ConversationChatDetailConverter.convert(chat);
        conversationChatDetailMapper.insert(chatEntity);
        chat.setId(chatEntity.getId());

        // 查询会话上下文
        Conversation conversation = queryById(chat.getConversationId());

        // 调用AI服务生成回复
        ConversationChatDetail aiReply = chatService.chat(conversation, chat);

        // 插入AI服务的响应消息
        if (aiReply != null && aiReply.getContent() != null) {
            ConversationChatDetailEntity aiChatEntity = ConversationChatDetailConverter.convert(aiReply);
            conversationChatDetailMapper.insert(aiChatEntity);
            aiReply.setId(aiChatEntity.getId());
        }
    }

    /**
     * 流式调用AI接口生成聊天记录.
     * 调用 `/streamChat` 接口，并以流形式返回文本分段.
     * @param conversationId 会话ID
     * @param userChat 用户的聊天输入
     * @return Flux<String> 流式返回响应内容
     */
    @Transactional
    public Flux<String> streamChat(Integer conversationId, ConversationChatDetail userChat) {
        Conversation conversation = queryById(conversationId);

        if (conversation == null) {
            log.error("未找到会话. ID: {}", conversationId);
            throw new IllegalArgumentException("会话不存在");
        }

        return chatService.streamChat(conversation, userChat)
                .doOnNext(response -> log.info("流式消息分片: {}", response)) // 输出日志
                .doOnError(error -> log.error("流式服务调用失败: {}", error.getMessage()));
    }

    /**
     * 删除一条chat_detail记录.
     * @param chatId 聊天记录ID
     */
    @Override
    public void removeChat(Integer chatId) {
        conversationChatDetailMapper.deleteById(chatId);
    }
}