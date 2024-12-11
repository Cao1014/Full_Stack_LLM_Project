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

import java.util.List;

/**
 * @author yingxian.cyx
 * @date Created in 2024/10/11
 */
@Service
@Slf4j
public class ConversationServiceImpl implements ConversationService {

    @Autowired
    private ConversationMapper conversationMapper;

    @Autowired
    private ConversationChatDetailMapper conversationChatDetailMapper;

    /**
     * 新建会话，包括新建一条conversation记录+初始chat_detail记录
     * @param conversation 会话
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
                addChat(chatDetail);
            }
        } else {
            ConversationChatDetail defaultChat = ConversationChatBuilder.buildDefaultChat(conversation);
            addChat(defaultChat);
        }
    }

    /**
     * 单条会话查询
     * @param conversationId 会话ID
     * @return 会话详情
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
     * 会话记录列表查询
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
     * 新建一条chat_detail记录
     * @param chat 聊天记录
     */
    @Override
    @Transactional
    public void addChat(ConversationChatDetail chat) {
        ConversationChatDetailEntity chatEntity = ConversationChatDetailConverter.convert(chat);
        conversationChatDetailMapper.insert(chatEntity);
        chat.setId(chatEntity.getId());
    }

    /**
     * 删除一条chat_detail记录
     * @param chatId 聊天记录ID
     */
    @Override
    public void removeChat(Integer chatId) {
        conversationChatDetailMapper.deleteById(chatId); // 调用正确的方法 deleteById
    }
}