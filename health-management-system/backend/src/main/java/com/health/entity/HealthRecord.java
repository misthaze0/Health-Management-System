package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 健康记录实体类
 * 对应数据库表 health_record
 * 用于存储用户的各项健康指标数据
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Data
@TableName("health_record")
public class HealthRecord {

    /**
     * 主键ID，自增
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 用户ID，关联用户表
     */
    private Long userId;

    /**
     * 指标类型
     * 如：血压(blood_pressure)、血糖(blood_sugar)、体重(weight)、心率(heart_rate)等
     */
    private String metricType;

    /**
     * 指标数值
     * 使用BigDecimal确保精确计算
     */
    private BigDecimal metricValue;

    /**
     * 记录日期
     */
    private LocalDate recordDate;

    /**
     * 备注信息
     */
    private String notes;

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
