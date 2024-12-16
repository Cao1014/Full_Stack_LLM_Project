package org.uestc.weglas.util;

import lombok.Getter;
import lombok.Setter;
import org.apache.commons.lang.builder.ToStringBuilder;
import org.uestc.weglas.core.enums.ResultEnum;

import java.util.ArrayList;
import java.util.List;

/**
 * @param <T>
 */
public class BaseResult<T> {
    @Setter
    @Getter
    private boolean success;

    private String message;
    @Setter
    @Getter
    private String resultCode;

    @Setter
    @Getter
    private T data;
    @Setter
    @Getter
    private List<T> values = new ArrayList<>();

    public BaseResult() {
    }

    public BaseResult(boolean success, String resultCode, String message, T data) {
        this.success = success;
        this.resultCode = resultCode;
        this.message = message;
        this.data = data;
    }

    public BaseResult(boolean success, String resultCode, String message, List<T> values) {
        this.success = success;
        this.resultCode = resultCode;
        this.message = message;
        this.values = values;
    }

    public static <T> BaseResult<T> success(T data) {
        return new BaseResult<>(true, ResultEnum.SUCCESS.getCode(), "Operation successful", data);
    }

    public static <T> BaseResult<T> success(List<T> values) {
        return new BaseResult<>(true, ResultEnum.SUCCESS.getCode(), "Operation successful", values);
    }

    public static <T> BaseResult<T> fail(ResultEnum resultCode) {
        return new BaseResult<>(false, resultCode.getCode(), resultCode.getMessage(), null);
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this);
    }

}
