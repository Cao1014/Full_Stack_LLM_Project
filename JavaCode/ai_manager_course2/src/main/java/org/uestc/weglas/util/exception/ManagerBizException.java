package org.uestc.weglas.util.exception;

import org.uestc.weglas.core.enums.ResultEnum;

/**
 * 定义通用业务异常
 *
 * @author yingxian.cyx
 * @date Created in 2024/6/21
 */
public class ManagerBizException extends RuntimeException {

    private String errorCode;

    public ManagerBizException() {
        super();
    }

    public ManagerBizException(String message) {
        super(message);
        this.errorCode = ResultEnum.SYSTEM_EXCEPTION.getCode();
    }

    public ManagerBizException(ResultEnum resultCode) {
        super(resultCode.getCode());
        this.errorCode = resultCode.getCode();
    }

    public ManagerBizException(String message, Throwable cause) {
        super(message, cause);
        this.errorCode = ResultEnum.SYSTEM_EXCEPTION.getCode();
    }

    public ManagerBizException(Throwable cause) {
        super(cause);
        this.errorCode = ResultEnum.SYSTEM_EXCEPTION.getCode();
    }

    public String getErrorCode() {
        return errorCode;
    }

    public void setErrorCode(String errorCode) {
        this.errorCode = errorCode;
    }
}
