package org.uestc.weglas.core.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.uestc.weglas.base.entity.ConversationChatDetailEntity;
import org.uestc.weglas.base.entity.ConversationEntity;
import org.uestc.weglas.base.mapper.ConversationChatDetailMapper;
import org.uestc.weglas.base.mapper.ConversationMapper;
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

    @Override
    @Transactional
    public void add(Conversation conversation) {
        ConversationEntity entity = ConversationConverter.convert(conversation);
        conversationMapper.insert(entity);
        // 设置最新的id
        conversation.setId(entity.getId());
    }

    @Override
    public Conversation queryById(Integer conversationId) {

        ConversationEntity conversationEntity = conversationMapper.selectById(conversationId);
        Conversation basicConversation = ConversationConverter.convert(conversationEntity);

        List<ConversationChatDetailEntity> chatDetailEntities = conversationChatDetailMapper.selectByConversationId(conversationId);
        List<ConversationChatDetail> chatList = ConversationChatDetailConverter.convert(chatDetailEntities);

        basicConversation.setChatList(chatList);

        return basicConversation;
    }

    @Override
    public List<Conversation> queryAll() {

        List<ConversationEntity> conversationEntities = conversationMapper.selectAll();

        return ConversationConverter.convert(conversationEntities);
    }

    @Override
    public void remove(Integer conversationId) {
        conversationMapper.deleteById(conversationId);
    }

    @Override
    @Transactional
    public void addChat(ConversationChatDetail chat) {
        conversationMapper.updateGmtModifiedById(chat.getConversationId());
        doAddChat(chat);
    }

    @Override
    public void removeChat(Integer chatId) {
        conversationChatDetailMapper.deleteById(chatId);
    }


    private void doAddChat(ConversationChatDetail chat) {
        ConversationChatDetailEntity entity = ConversationChatDetailConverter.convert(chat);
        conversationChatDetailMapper.insert(entity);
        chat.setId(entity.getId());
    }

}
