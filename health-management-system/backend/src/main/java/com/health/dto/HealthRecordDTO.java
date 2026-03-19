package com.health.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 健康记录DTO类
 * 用于健康记录的数据传输
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Data
public class HealthRecordDTO {

    /**
     * 记录ID
     */
    private Long id;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 指标类型
     * 必填项，如：blood_pressure(血压)、blood_sugar(血糖)、weight(体重)、heart_rate(心率)等
     */
    @NotBlank(message = "指标类型不能为空")
    private String metricType;

    /**
     * 指标数值
     * 必填项，必须为正数
     */
    @NotNull(message = "指标数值不能为空")
    @Positive(message = "指标数值必须为正数")
    private BigDecimal metricValue;

    /**
     * 记录日期
     * 必填项
     */
    @NotNull(message = "记录日期不能为空")
    private LocalDate recordDate;

    /**
     * 备注信息
     */
    private String notes;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    private LocalDateTime updateTime;
}
