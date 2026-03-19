package com.health.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.health.entity.Carousel;
import com.health.repository.CarouselRepository;
import com.health.service.CarouselService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 轮播图服务实现类
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@Service
public class CarouselServiceImpl extends ServiceImpl<CarouselRepository, Carousel> implements CarouselService {

    @Autowired
    private CarouselRepository carouselRepository;

    /**
     * 获取启用的轮播图列表
     *
     * @return 轮播图列表
     */
    @Override
    public List<Carousel> getEnabledCarousel() {
        return carouselRepository.selectEnabledCarousel();
    }

    /**
     * 创建轮播图
     *
     * @param carousel 轮播图信息
     * @param userId   创建人ID
     * @return 是否成功
     */
    @Override
    public boolean createCarousel(Carousel carousel, Long userId) {
        try {
            // 设置默认值
            if (carousel.getStatus() == null) {
                carousel.setStatus(1); // 默认启用
            }
            if (carousel.getSortOrder() == null) {
                // 获取当前最大排序值
                LambdaQueryWrapper<Carousel> wrapper = new LambdaQueryWrapper<>();
                wrapper.orderByDesc(Carousel::getSortOrder);
                wrapper.last("LIMIT 1");
                Carousel lastCarousel = carouselRepository.selectOne(wrapper);
                carousel.setSortOrder(lastCarousel != null ? lastCarousel.getSortOrder() + 1 : 1);
            }

            // 设置创建人
            carousel.setCreatedBy(userId);

            // 保存轮播图
            boolean success = save(carousel);
            if (success) {
                log.info("轮播图创建成功: id={}, title={}", carousel.getId(), carousel.getTitle());
            }
            return success;
        } catch (Exception e) {
            log.error("轮播图创建失败: {}", e.getMessage(), e);
            return false;
        }
    }

    /**
     * 更新轮播图
     *
     * @param carousel 轮播图信息
     * @return 是否成功
     */
    @Override
    public boolean updateCarousel(Carousel carousel) {
        try {
            // 不允许修改创建人和创建时间
            carousel.setCreatedBy(null);
            carousel.setCreateTime(null);

            // 更新轮播图
            boolean success = updateById(carousel);
            if (success) {
                log.info("轮播图更新成功: id={}", carousel.getId());
            }
            return success;
        } catch (Exception e) {
            log.error("轮播图更新失败: id={}, error={}", carousel.getId(), e.getMessage(), e);
            return false;
        }
    }

    /**
     * 删除轮播图
     *
     * @param id 轮播图ID
     * @return 是否成功
     */
    @Override
    public boolean deleteCarousel(Long id) {
        try {
            boolean success = removeById(id);
            if (success) {
                log.info("轮播图删除成功: id={}", id);
            }
            return success;
        } catch (Exception e) {
            log.error("轮播图删除失败: id={}, error={}", id, e.getMessage(), e);
            return false;
        }
    }
}
