package org.uestc.weglas.util.template;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.TransactionCallbackWithoutResult;
import org.springframework.transaction.support.TransactionTemplate;
import org.uestc.weglas.core.enums.ResultEnum;
import org.uestc.weglas.util.BaseResult;
import org.uestc.weglas.util.exception.ManagerBizException;
import org.uestc.weglas.util.log.LogUtil;

/**
 * @author yingxian.cyx
 * @date Created in 2024/12/5
 */
public class BizTemplate {

    private static final Logger logger = LogManager.getLogger(BizCallback.class);

    private static TransactionTemplate transactionTemplate;

    /**
     * 处理模板
     *
     * @param callback 回调接口
     * @return T 处理结果
     */
    public static <T> BaseResult<T> executeWithTransaction(BizCallback callback) {

        BaseResult<T> innerResult = new BaseResult<>();
        try {
            callback.checkParameter();
            transactionTemplate.execute((new TransactionCallbackWithoutResult() {

                @Override
                public void doInTransactionWithoutResult(TransactionStatus status) {
                    // 2. 回调处理结果
                    callback.executeWithTransaction(status);
                }
            }));

            innerResult.setSuccess(true);
            innerResult.setResultCode(ResultEnum.SUCCESS.getCode());

        } catch (ManagerBizException bizException) {
            innerResult.setSuccess(false);
            innerResult.setResultCode(bizException.getErrorCode());
            LogUtil.warn(logger, bizException, "BizException");
        } catch (RuntimeException e) {
            innerResult.setSuccess(false);
            innerResult.setResultCode(ResultEnum.SYSTEM_EXCEPTION.getCode());
            LogUtil.error(logger, e, "RuntimeException");
        }

        //TODO 摘要日志
        return innerResult;
    }

    /**
     * 处理模板
     *
     * @param callback 回调接口
     * @return T 处理结果
     */
    public static <T> BaseResult<T> execute(BizCallback<T> callback) {

        BaseResult<T> innerResult = new BaseResult<>();
        try {
            callback.checkParameter();
            callback.execute(innerResult);

            innerResult.setSuccess(true);
            innerResult.setResultCode(ResultEnum.SUCCESS.getCode());

        } catch (ManagerBizException bizException) {
            innerResult.setSuccess(false);
            innerResult.setResultCode(bizException.getErrorCode());
            LogUtil.warn(logger, bizException, "BizException");
        } catch (RuntimeException e) {
            innerResult.setSuccess(false);
            innerResult.setResultCode(ResultEnum.SYSTEM_EXCEPTION.getCode());
            LogUtil.error(logger, e, "RuntimeException");
        }

        //TODO 摘要日志
        return innerResult;
    }

    public void setTransactionTemplate(TransactionTemplate transactionTemplate) {
        BizTemplate.transactionTemplate = transactionTemplate;
    }
}
