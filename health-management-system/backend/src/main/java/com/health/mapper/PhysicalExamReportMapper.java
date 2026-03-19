package com.health.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.health.entity.PhysicalExamReport;
import org.apache.ibatis.annotations.Mapper;

/**
 * 体检报告Mapper接口
 */
@Mapper
public interface PhysicalExamReportMapper extends BaseMapper<PhysicalExamReport> {
}
