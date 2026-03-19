package com.health.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.health.entity.Hospital;
import org.apache.ibatis.annotations.Mapper;

/**
 * 医院/体检机构Mapper接口
 */
@Mapper
public interface HospitalMapper extends BaseMapper<Hospital> {
}
