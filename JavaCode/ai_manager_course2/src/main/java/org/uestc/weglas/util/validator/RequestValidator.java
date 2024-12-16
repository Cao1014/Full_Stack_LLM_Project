package org.uestc.weglas.util.validator;

import org.uestc.weglas.core.enums.ResultEnum;
import org.uestc.weglas.util.exception.AssertUtil;
import org.uestc.weglas.util.exception.ManagerBizException;

import javax.validation.ConstraintViolation;
import javax.validation.Validation;
import javax.validation.Validator;
import java.util.Set;

/**
 * @author yingxian.cyx
 * @date Created in 2024/12/5
 */
public class RequestValidator {

    private static final Validator validator = Validation.buildDefaultValidatorFactory().getValidator();

    /**
     * 统一校验方法
     *
     * @param request
     */
    public static void valid(Object request) {
        AssertUtil.notNull(request);

        Set<ConstraintViolation<Object>> violations = validator.validate(request);
        if (!violations.isEmpty()) {
            throw new ManagerBizException(ResultEnum.PARAMETER_ILLEGAL);
        }
    }
}
