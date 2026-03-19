package com.health.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 管理员权限注解
 * 用于标记需要管理员权限才能访问的方法
 * 配合 AdminInterceptor 拦截器使用
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireAdmin {
    /**
     * 权限描述
     */
    String value() default "";
}
