package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 用户实体类
 * 对应数据库表: sys_user
 * 用于存储系统用户的基本信息
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Data
@TableName("sys_user")
public class User {

    /**
     * 用户ID，主键，自增
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 用户名，唯一标识，用于登录
     */
    private String username;

    /**
     * 密码，BCrypt加密存储
     */
    private String password;

    /**
     * 邮箱地址，可选
     */
    private String email;

    /**
     * 手机号码，可选
     */
    private String phone;

    /**
     * 头像URL地址
     */
    private String avatar;

    /**
     * 真实姓名
     */
    private String realName;

    /**
     * 性别: 0-未知, 1-男, 2-女
     */
    private Integer gender;

    /**
     * 出生日期
     */
    private LocalDate birthday;

    /**
     * 身份证号
     */
    private String idCard;

    /**
     * 状态: 0-禁用, 1-启用
     */
    private Integer status;

    /**
     * 删除标记: 0-未删除, 1-已删除（逻辑删除）
     */
    @TableLogic
    private Integer deleted;

    /**
     * 创建时间，自动填充
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    /**
     * 更新时间，自动填充
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
