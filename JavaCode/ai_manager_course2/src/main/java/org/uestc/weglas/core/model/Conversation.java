package org.uestc.weglas.core.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.uestc.weglas.base.ToString;

import javax.validation.constraints.NotBlank;
import java.util.*;

/**
 * 会话模型类
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class Conversation extends ToString {

    private Integer id; // 会话 ID
    @NotBlank
    private String title; // 会话标题
    private String llmModel; // LLM 模型名称

    private Map<String, String> ext = new HashMap<>(); // 扩展字段
    private List<ConversationChatDetail> chatList = new ArrayList<>(); // 聊天记录列表

    private Date gmtCreate; // 创建时间
    private Date gmtModified; // 更新时间

    /**
     * 获取历史消息内容（文本列表）
     *
     * @return 聊天记录的文本列表
     */
    public List<String> getHistoryMessages() {
        List<String> historyMessages = new ArrayList<>();
        for (ConversationChatDetail chat : chatList) {
            if (chat != null && chat.getContent() != null) {
                historyMessages.add(chat.getContent()); // 提取每条聊天的内容
            }
        }
        return historyMessages; // 返回所有历史消息文本
    }
}