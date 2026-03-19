package com.health.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.health.entity.Carousel;

import java.util.List;

/**
 * 轮播图服务接口
 *
 * @author Health Management System
 * @since 1.0.0
 */
public interface CarouselService extends IService<Carousel> {

    /**
     * 获取启用的轮播图列表
     *
     * @return 轮播图列表
     */
    List<Carousel> getEnabledCarousel();

    /**
     * 创建轮播图
     *
     * @param carousel 轮播图信息
     * @param userId   创建人ID
     * @return 是否成功
     */
    boolean createCarousel(Carousel carousel, Long userId);

    /**
     * 更新轮播图
     *
     * @param carousel 轮播图信息
     * @return 是否成功
     */
    boolean updateCarousel(Carousel carousel);

    /**
     * 删除轮播图
     *
     * @param id 轮播图ID
     * @return 是否成功
     */
    boolean deleteCarousel(Long id);
}
