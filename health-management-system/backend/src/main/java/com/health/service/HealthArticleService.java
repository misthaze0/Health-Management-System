package com.health.service;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.health.entity.HealthArticle;
import com.health.repository.HealthArticleRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 健康知识文章服务层
 * 提供文章的业务逻辑处理
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@Service
public class HealthArticleService extends ServiceImpl<HealthArticleRepository, HealthArticle> {

    @Autowired
    private CarouselService carouselService;

    /**
     * 获取所有启用的文章
     */
    public List<HealthArticle> getAllActiveArticles() {
        log.info("[HealthArticleService] 开始获取所有启用的文章");
        try {
            List<HealthArticle> list = baseMapper.selectAllActiveArticles();
            log.info("[HealthArticleService] 获取所有文章成功, 数量: {}", list != null ? list.size() : 0);
            return list;
        } catch (Exception e) {
            log.error("[HealthArticleService] 获取所有文章失败: {}", e.getMessage(), e);
            throw e;
        }
    }

    /**
     * 创建文章
     */
    public boolean createArticle(HealthArticle article, Long userId) {
        log.info("[HealthArticleService] 创建文章: title={}, userId={}", article.getTitle(), userId);
        try {
            article.setCreatedBy(userId);
            article.setViews(0);
            article.setStatus(1);
            boolean result = save(article);
            log.info("[HealthArticleService] 创建文章成功: id={}", article.getId());
            return result;
        } catch (Exception e) {
            log.error("[HealthArticleService] 创建文章失败: {}", e.getMessage(), e);
            throw e;
        }
    }

    /**
     * 更新文章
     */
    public boolean updateArticle(HealthArticle article) {
        log.info("[HealthArticleService] 更新文章: id={}", article.getId());
        try {
            boolean result = updateById(article);
            log.info("[HealthArticleService] 更新文章成功: id={}", article.getId());
            return result;
        } catch (Exception e) {
            log.error("[HealthArticleService] 更新文章失败: {}", e.getMessage(), e);
            throw e;
        }
    }

    /**
     * 删除文章
     */
    public boolean deleteArticle(Long id) {
        log.info("[HealthArticleService] 删除文章: id={}", id);
        try {
            boolean result = removeById(id);
            log.info("[HealthArticleService] 删除文章成功: id={}", id);
            return result;
        } catch (Exception e) {
            log.error("[HealthArticleService] 删除文章失败: {}", e.getMessage(), e);
            throw e;
        }
    }

    /**
     * 增加文章浏览量
     */
    public void incrementViews(Long articleId) {
        try {
            HealthArticle article = getById(articleId);
            if (article != null) {
                article.setViews(article.getViews() + 1);
                updateById(article);
                log.info("[HealthArticleService] 文章浏览量+1: id={}", articleId);
            }
        } catch (Exception e) {
            log.error("[HealthArticleService] 增加浏览量失败: {}", e.getMessage(), e);
        }
    }
}
