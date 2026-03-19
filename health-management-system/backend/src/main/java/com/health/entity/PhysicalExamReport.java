package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 体检报告实体类
 */
@Data
@TableName("physical_exam_report")
public class PhysicalExamReport {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;
    
    private Long appointmentId;
    
    private LocalDate examDate;
    
    private String centerName;
    
    private String reportNo;
    
    private String overallResult;
    
    private String overallSuggestion;
    
    private String aiAnalysis;
    
    private Integer status;
    
    private String fileUrl;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
