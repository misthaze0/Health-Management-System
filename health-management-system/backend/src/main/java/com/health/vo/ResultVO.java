package com.health.vo;

import lombok.Data;

/**
 * 统一响应结果VO (View Object)
 * 用于封装API接口的统一响应格式
 *
 * @param <T> 响应数据的类型
 * @author Health Management System
 * @since 1.0.0
 */
@Data
public class ResultVO<T> {

    /**
     * 响应状态码
     * 200: 成功
     * 500: 服务器错误
     * 其他: 自定义错误码
     */
    private Integer code;

    /**
     * 响应消息
     */
    private String message;

    /**
     * 响应数据
     */
    private T data;

    /**
     * 成功响应（带数据）
     *
     * @param data 响应数据
     * @param <T>  数据类型
     * @return ResultVO对象
     */
    public static <T> ResultVO<T> success(T data) {
        ResultVO<T> result = new ResultVO<>();
        result.setCode(200);
        result.setMessage("success");
        result.setData(data);
        return result;
    }

    /**
     * 成功响应（无数据）
     *
     * @param <T> 数据类型
     * @return ResultVO对象
     */
    public static <T> ResultVO<T> success() {
        return success(null);
    }

    /**
     * 错误响应（默认错误码500）
     *
     * @param message 错误消息
     * @param <T>     数据类型
     * @return ResultVO对象
     */
    public static <T> ResultVO<T> error(String message) {
        ResultVO<T> result = new ResultVO<>();
        result.setCode(500);
        result.setMessage(message);
        return result;
    }

    /**
     * 错误响应（自定义错误码）
     *
     * @param code    错误码
     * @param message 错误消息
     * @param <T>     数据类型
     * @return ResultVO对象
     */
    public static <T> ResultVO<T> error(Integer code, String message) {
        ResultVO<T> result = new ResultVO<>();
        result.setCode(code);
        result.setMessage(message);
        return result;
    }
}
