package org.uestc.weglas.util.template;

import org.springframework.transaction.TransactionStatus;
import org.uestc.weglas.util.BaseResult;

/**
 * @author yingxian.cyx
 * @date Created in 2024/12/5
 */
public class AbstractBizCallback<T> implements BizCallback<T> {
    @Override
    public void checkParameter() {
        // do nothing
    }

    @Override
    public void executeWithTransaction(TransactionStatus status) {
        // do nothing
    }

    @Override
    public void execute(BaseResult<T> result) {

    }

}
