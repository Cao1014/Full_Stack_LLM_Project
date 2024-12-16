# ai_manager
## 准备工作
1. 安装java、maven、mysql server
2. （可选）emqx服务器安装（mqtt使用）。
    * 启动 emqx start
    * 管理页面 http://localhost:18083/
3. mvn clean install 
4. 初始化mysql
    * 新建数据库
    * 参考[application.yml](src%2Fmain%2Fresources%2Fapplication.yml)文件，按需修改db连接配置
5. 启动应用
    * java -jar target/ai-manager.jar
    * 启动过程中会自动执行schema.sql,新建数据表

## 项目说明
1. 目录结构
   - src/main/java
     - controller：web层控制器文件
     - service: 领域层服务
     - model：领域模型
     - base
       - mapper: ibatis数据表映射文件
       - entity：数据层模型
     - util：工具类（日志、错误码、异常等）
     - [AiManageApplication.java](src%2Fmain%2Fjava%2Forg%2Fuestc%2Fweglas%2FAiManageApplication.java) :应用启动文件
   - src/main/resources
     - db：sql目录
     - application.yml 配置文件
     - log4j2-spring.xml 日志配置文件，log4j2
     - mappers:ibatis数据表映射文件
     - static:静态文件，js、css、logo等
     - templates：项目自己实现的前端页面
   - src/test/java 测试用例 
2. 实现关键点
    * mqtt发布订阅
    * db读写
    * http流式读取