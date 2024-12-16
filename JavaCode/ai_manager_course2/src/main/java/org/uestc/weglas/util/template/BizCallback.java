package org.uestc.weglas.util.template;

import org.springframework.transaction.TransactionStatus;
import org.uestc.weglas.util.BaseResult;

/**
 * @author yingxian.cyx
 * @date Created in 2024/12/5
 */
public interface BizCallback<T> {

    /**
     * 基本参数校验
     */
    void checkParameter();

    /**
     * 带事务在Template中执行
     */
    void executeWithTransaction(TransactionStatus status);

    /**
     * 在Template中执行
     */
    void execute(BaseResult<T> result);

}
