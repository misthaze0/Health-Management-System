package com.health.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.health.entity.PhysicalExamAppointment;
import org.apache.ibatis.annotations.Mapper;

/**
 * 体检预约Mapper接口
 */
@Mapper
public interface PhysicalExamAppointmentMapper extends BaseMapper<PhysicalExamAppointment> {
}
