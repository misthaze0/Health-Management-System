package com.health.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 体检指标实体类
 */
@Data
@TableName("exam_indicator")
public class ExamIndicator {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long reportId;
    
    private String indicatorCode;
    
    private String indicatorName;
    
    private String indicatorValue;
    
    private String unit;
    
    private String referenceRange;
    
    private Integer status;
    
    private String aiInterpretation;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
