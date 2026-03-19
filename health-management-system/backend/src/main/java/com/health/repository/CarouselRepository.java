package com.health.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.health.entity.Carousel;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 轮播图数据访问层
 * 对应数据库表: carousel
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Mapper
public interface CarouselRepository extends BaseMapper<Carousel> {

    /**
     * 查询启用的轮播图列表，按排序值升序排列
     *
     * @return 轮播图列表
     */
    @Select("SELECT * FROM carousel WHERE status = 1 ORDER BY sort_order ASC")
    List<Carousel> selectEnabledCarousel();
}
