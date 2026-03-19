package com.health.controller;

import com.health.entity.Carousel;
import com.health.entity.HealthArticle;
import com.health.service.CarouselService;
import com.health.service.HealthArticleService;
import com.health.vo.ResultVO;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 健康知识文章公开接口控制器
 * 提供首页等公开页面查询文章数据的接口
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@RestController
@RequestMapping("/articles")
public class ArticleController {

    @Autowired
    private HealthArticleService healthArticleService;

    @Autowired
    private CarouselService carouselService;

    @Value("${file.upload.url-prefix:/api/uploads/}")
    private String uploadUrlPrefix;

    /**
     * 获取启用的文章列表
     * 用于首页健康知识区域展示
     *
     * @return 文章列表
     */
    @GetMapping("/list")
    public ResultVO<List<HealthArticle>> getArticles() {
        log.info("[ArticleController] 获取公开文章列表");
        try {
            List<HealthArticle> articles = healthArticleService.getAllActiveArticles();
            log.info("[ArticleController] 获取到 {} 篇文章", articles != null ? articles.size() : 0);
            return ResultVO.success(articles);
        } catch (Exception e) {
            log.error("[ArticleController] 获取文章列表失败: {}", e.getMessage(), e);
            return ResultVO.error("获取文章列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取轮播图列表
     * 用于首页轮播图展示
     *
     * @return 轮播图列表
     */
    @GetMapping("/carousel")
    public ResultVO<List<Carousel>> getCarouselArticles() {
        log.info("[ArticleController] 获取轮播图列表");
        try {
            List<Carousel> carouselList = carouselService.getEnabledCarousel();
            
            // 直接返回数据库中的数据，前端会处理URL拼接
            log.info("[ArticleController] 获取到 {} 条轮播图", carouselList != null ? carouselList.size() : 0);
            return ResultVO.success(carouselList);
        } catch (Exception e) {
            log.error("[ArticleController] 获取轮播图失败: {}", e.getMessage(), e);
            return ResultVO.error("获取轮播图失败: " + e.getMessage());
        }
    }

    /**
     * 获取文章分类列表
     *
     * @return 分类列表
     */
    @GetMapping("/categories")
    public ResultVO<List<String>> getCategories() {
        log.info("[ArticleController] 获取文章分类列表");
        try {
            // 返回预定义的分类列表
            List<String> categories = List.of(
                "健康资讯",
                "疾病科普",
                "饮食建议",
                "运动指导",
                "心理健康",
                "用药指南"
            );
            return ResultVO.success(categories);
        } catch (Exception e) {
            log.error("[ArticleController] 获取分类列表失败: {}", e.getMessage(), e);
            return ResultVO.error("获取分类列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取文章详情
     * 同时增加浏览量
     *
     * @param id 文章ID
     * @return 文章详情
     */
    @GetMapping("/{id}")
    public ResultVO<HealthArticle> getArticleDetail(@PathVariable Long id) {
        log.info("[ArticleController] 获取文章详情: id={}", id);
        try {
            HealthArticle article = healthArticleService.getById(id);
            if (article == null || article.getStatus() != 1) {
                log.warn("[ArticleController] 文章不存在或已下架: id={}", id);
                return ResultVO.error("文章不存在或已下架");
            }

            // 增加浏览量
            healthArticleService.incrementViews(id);

            log.info("[ArticleController] 获取文章详情成功: id={}", id);
            return ResultVO.success(article);
        } catch (Exception e) {
            log.error("[ArticleController] 获取文章详情失败: {}", e.getMessage(), e);
            return ResultVO.error("获取文章详情失败: " + e.getMessage());
        }
    }
}
