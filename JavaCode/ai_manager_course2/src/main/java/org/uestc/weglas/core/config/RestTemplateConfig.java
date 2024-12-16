package org.uestc.weglas.core.config;

import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

@Configuration
public class RestTemplateConfig {

    /**
     * 定义一个 RestTemplate Bean，并进行基本超时配置
     *
     * @param builder RestTemplate构建器
     * @return 配置完成的 RestTemplate 实例
     */
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofSeconds(10)) // 设置连接超时时间
                .setReadTimeout(Duration.ofSeconds(10))    // 设置读取超时时间
                .build();
    }
}