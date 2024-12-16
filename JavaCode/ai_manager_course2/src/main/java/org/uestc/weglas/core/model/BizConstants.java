package org.uestc.weglas.core.model;

/**
 * @author yingxian.cyx
 * @date Created in 2024/10/17
 */
public class BizConstants {

    /**
     * 服务质量
     */
    public static final Integer MQTT_QOS = 1;
    /**
     * mqtt超时时间
     */
    public static final Integer MQTT_CONNECT_TIMEOUT = 100;

    /**
     * mqtt保活
     */
    public static final Integer MQTT_KEEP_ALIVE = 20;

    /**
     * mqtt是否保留消息
     */
    public static final Boolean MQTT_RETAINED = true;
}
