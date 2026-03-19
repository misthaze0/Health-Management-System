package com.health.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.health.annotation.RequireAdmin;
import com.health.entity.Carousel;
import com.health.entity.HealthArticle;
import com.health.entity.User;
import com.health.service.CarouselService;
import com.health.service.HealthArticleService;
import com.health.utils.FileUtil;
import com.health.vo.ResultVO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import jakarta.annotation.PostConstruct;
import jakarta.servlet.http.HttpServletRequest;
import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 管理员后台控制器
 * 提供文章管理、图片上传等后台管理功能
 * 所有接口都需要管理员权限
 *
 * @author Health Management System
 * @since 1.0.0
 */
@Slf4j
@RestController
@RequestMapping("/admin")
public class AdminController {

    @Autowired
    private HealthArticleService healthArticleService;

    @Autowired
    private CarouselService carouselService;

    /**
     * 文件上传绝对路径 - 统一使用固定路径
     * 注意：使用 backend/uploads 目录，这是实际存储文件的位置
     */
    private static final String ABSOLUTE_UPLOAD_PATH = "d:/基于KIMI的全流程健康管理系统/health-management-system/backend/uploads/";

    /**
     * URL前缀 - 用于访问上传的文件
     * 注意：由于 server.servlet.context-path=/api，这里的 /uploads/ 会被映射为 /api/uploads/
     */
    private static final String UPLOAD_URL_PREFIX = "/uploads/";

    @PostConstruct
    public void init() {
        // 确保上传目录存在
        File uploadDir = new File(ABSOLUTE_UPLOAD_PATH);
        if (!uploadDir.exists()) {
            boolean created = uploadDir.mkdirs();
            log.info("[AdminController] 创建上传目录: {}, 结果: {}", ABSOLUTE_UPLOAD_PATH, created);
        }
        log.info("[AdminController] 文件上传路径配置: {}", ABSOLUTE_UPLOAD_PATH);
    }

    // ==================== 文章管理接口 ====================

    /**
     * 获取文章列表（支持分页）
     *
     * @param page      当前页码，默认1
     * @param size      每页大小，默认10
     * @param keyword   搜索关键词（标题或摘要）
     * @param status    状态筛选：0-禁用，1-启用
     * @return 分页文章列表
     */
    @GetMapping("/articles")
    @RequireAdmin("获取文章列表")
    public ResultVO<Map<String, Object>> getArticleList(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Integer status) {

        log.info("管理员获取文章列表: page={}, size={}, keyword={}", page, size, keyword);

        // 构建查询条件
        LambdaQueryWrapper<HealthArticle> queryWrapper = new LambdaQueryWrapper<>();

        // 关键词搜索（标题或摘要）
        if (keyword != null && !keyword.trim().isEmpty()) {
            queryWrapper.and(wrapper -> wrapper
                    .like(HealthArticle::getTitle, keyword)
                    .or()
                    .like(HealthArticle::getSummary, keyword));
        }

        // 状态筛选
        if (status != null) {
            queryWrapper.eq(HealthArticle::getStatus, status);
        }

        // 按创建时间倒序排列
        queryWrapper.orderByDesc(HealthArticle::getCreateTime);

        // 执行分页查询
        Page<HealthArticle> pageParam = new Page<>(page, size);
        Page<HealthArticle> resultPage = healthArticleService.page(pageParam, queryWrapper);

        // 转换为前端期望的格式
        Map<String, Object> result = new HashMap<>();
        result.put("list", resultPage.getRecords());
        result.put("total", resultPage.getTotal());
        result.put("page", resultPage.getCurrent());
        result.put("pageSize", resultPage.getSize());
        result.put("pages", resultPage.getPages());

        return ResultVO.success(result);
    }

    /**
     * 获取文章详情
     *
     * @param id 文章ID
     * @return 文章详情
     */
    @GetMapping("/articles/{id}")
    @RequireAdmin("获取文章详情")
    public ResultVO<HealthArticle> getArticleDetail(@PathVariable Long id) {
        log.info("[DEBUG] ==================== 管理员获取文章详情开始 ====================");
        log.info("[DEBUG] 请求参数 - id: {}", id);

        try {
            HealthArticle article = healthArticleService.getById(id);
            log.info("[DEBUG] 数据库查询结果: {}", article != null ? "找到文章" : "文章不存在");

            if (article == null) {
                log.warn("[DEBUG] 文章不存在, id: {}", id);
                return ResultVO.error("文章不存在");
            }

            log.info("[DEBUG] 文章详情 - id: {}, title: {}, imageUrl: {}",
                    article.getId(), article.getTitle(), article.getImageUrl());
            log.info("[DEBUG] ==================== 管理员获取文章详情结束 ====================");

            return ResultVO.success(article);
        } catch (Exception e) {
            log.error("[DEBUG] 获取文章详情时发生异常, id: {}", id, e);
            return ResultVO.error("获取文章详情失败: " + e.getMessage());
        }
    }

    /**
     * 创建文章
     *
     * @param article 文章信息
     * @param request HTTP请求，用于获取当前用户
     * @return 创建结果
     */
    @PostMapping("/articles")
    @RequireAdmin("创建文章")
    public ResultVO<HealthArticle> createArticle(@RequestBody HealthArticle article, HttpServletRequest request) {
        log.info("[DEBUG] ==================== 管理员创建文章开始 ====================");
        log.info("[DEBUG] 请求参数 - title: {}, imageUrl: {}", article.getTitle(), article.getImageUrl());

        try {
            // 参数校验
            if (article.getTitle() == null || article.getTitle().trim().isEmpty()) {
                log.warn("[DEBUG] 参数校验失败: 文章标题为空");
                return ResultVO.error("文章标题不能为空");
            }
            if (article.getContent() == null || article.getContent().trim().isEmpty()) {
                log.warn("[DEBUG] 参数校验失败: 文章内容为空");
                return ResultVO.error("文章内容不能为空");
            }

            // 获取当前管理员用户ID
            Long userId = (Long) request.getAttribute("currentUserId");
            log.info("[DEBUG] 当前用户ID: {}", userId);

            // 设置默认值
            if (article.getStatus() == null) {
                article.setStatus(1); // 默认启用
            }
            if (article.getViews() == null) {
                article.setViews(0);
            }
            if (article.getSortOrder() == null) {
                article.setSortOrder(0);
            }

            log.info("[DEBUG] 准备保存文章到数据库");

            // 保存文章
            boolean success = healthArticleService.createArticle(article, userId);
            if (success) {
                log.info("[DEBUG] 文章创建成功: id={}", article.getId());
                log.info("[DEBUG] ==================== 管理员创建文章结束 ====================");
                return ResultVO.success(article);
            } else {
                log.error("[DEBUG] 文章创建失败");
                return ResultVO.error("文章创建失败");
            }
        } catch (Exception e) {
            log.error("[DEBUG] 创建文章时发生异常", e);
            return ResultVO.error("创建文章失败: " + e.getMessage());
        }
    }

    /**
     * 更新文章
     * 如果更换了封面图片，会自动删除原封面图片文件
     *
     * @param id      文章ID
     * @param article 更新的文章信息
     * @return 更新结果
     */
    @PutMapping("/articles/{id}")
    @RequireAdmin("更新文章")
    public ResultVO<HealthArticle> updateArticle(@PathVariable Long id, @RequestBody HealthArticle article) {
        log.info("[DEBUG] ==================== 管理员更新文章开始 ====================");
        log.info("[DEBUG] 请求参数 - id: {}, title: {}, imageUrl: {}", id, article.getTitle(), article.getImageUrl());

        try {
            // 检查文章是否存在
            HealthArticle existingArticle = healthArticleService.getById(id);
            log.info("[DEBUG] 数据库查询结果: {}", existingArticle != null ? "找到文章" : "文章不存在");

            if (existingArticle == null) {
                log.warn("[DEBUG] 文章不存在, id: {}", id);
                return ResultVO.error("文章不存在");
            }

            // 检查是否更换了封面图片
            String oldImageUrl = existingArticle.getImageUrl();
            String newImageUrl = article.getImageUrl();
            if (oldImageUrl != null && !oldImageUrl.isEmpty() && 
                newImageUrl != null && !newImageUrl.equals(oldImageUrl)) {
                // 删除旧封面图片文件
                boolean fileDeleted = FileUtil.deleteUploadFile(oldImageUrl);
                if (fileDeleted) {
                    log.info("[DEBUG] 文章旧封面图片已删除: {}", oldImageUrl);
                } else {
                    log.warn("[DEBUG] 文章旧封面图片删除失败或不存在: {}", oldImageUrl);
                }
            }

            // 设置文章ID
            article.setId(id);

            // 不允许修改创建人和创建时间
            article.setCreatedBy(null);
            article.setCreateTime(null);

            log.info("[DEBUG] 准备更新文章到数据库");

            // 更新文章
            boolean success = healthArticleService.updateArticle(article);
            if (success) {
                log.info("[DEBUG] 文章更新成功: id={}", id);
                log.info("[DEBUG] ==================== 管理员更新文章结束 ====================");
                return ResultVO.success(healthArticleService.getById(id));
            } else {
                log.error("[DEBUG] 文章更新失败: id={}", id);
                return ResultVO.error("文章更新失败");
            }
        } catch (Exception e) {
            log.error("[DEBUG] 更新文章时发生异常, id: {}", id, e);
            return ResultVO.error("更新文章失败: " + e.getMessage());
        }
    }

    /**
     * 删除文章
     * 删除文章时会同步删除数据库记录和物理文件
     *
     * @param id 文章ID
     * @return 删除结果
     */
    @DeleteMapping("/articles/{id}")
    @RequireAdmin("删除文章")
    public ResultVO<Void> deleteArticle(@PathVariable Long id) {
        log.info("管理员删除文章: id={}", id);

        // 检查文章是否存在
        HealthArticle existingArticle = healthArticleService.getById(id);
        if (existingArticle == null) {
            return ResultVO.error("文章不存在");
        }

        // 删除封面图片文件（同步删除物理文件）
        String imageUrl = existingArticle.getImageUrl();
        if (imageUrl != null && !imageUrl.isEmpty()) {
            boolean fileDeleted = FileUtil.deleteUploadFile(imageUrl);
            if (fileDeleted) {
                log.info("文章封面图片已删除: {}", imageUrl);
            } else {
                log.warn("文章封面图片删除失败或不存在: {}", imageUrl);
            }
        }

        // 删除文章
        boolean success = healthArticleService.deleteArticle(id);
        if (success) {
            log.info("文章删除成功: id={}", id);
            return ResultVO.success();
        } else {
            return ResultVO.error("文章删除失败");
        }
    }

    /**
     * 批量删除文章
     * 批量删除时会同步删除所有文章的封面图片文件
     *
     * @param ids 文章ID数组
     * @return 删除结果
     */
    @DeleteMapping("/articles/batch")
    @RequireAdmin("批量删除文章")
    public ResultVO<Void> batchDeleteArticles(@RequestBody Map<String, List<Long>> requestBody) {
        List<Long> ids = requestBody.get("ids");
        log.info("管理员批量删除文章: ids={}", ids);

        if (ids == null || ids.isEmpty()) {
            return ResultVO.error("请选择要删除的文章");
        }

        // 先获取所有文章的封面图片路径
        List<HealthArticle> articles = healthArticleService.listByIds(ids);
        int deletedFileCount = 0;

        // 删除所有封面图片文件
        for (HealthArticle article : articles) {
            String imageUrl = article.getImageUrl();
            if (imageUrl != null && !imageUrl.isEmpty()) {
                boolean fileDeleted = FileUtil.deleteUploadFile(imageUrl);
                if (fileDeleted) {
                    deletedFileCount++;
                    log.info("文章封面图片已删除: id={}, url={}", article.getId(), imageUrl);
                }
            }
        }
        log.info("批量删除文章封面图片完成: 成功删除 {} 个文件", deletedFileCount);

        // 批量删除数据库记录
        boolean success = healthArticleService.removeByIds(ids);
        if (success) {
            log.info("批量删除文章成功: 数量={}", ids.size());
            return ResultVO.success();
        } else {
            return ResultVO.error("批量删除失败");
        }
    }

    // ==================== 轮播图管理接口 ====================

    /**
     * 获取轮播图列表
     * 专门用于管理后台的轮播图管理页面
     *
     * @return 轮播图列表（不分页，按排序值升序排列）
     */
    @GetMapping("/carousel")
    @RequireAdmin("获取轮播图列表")
    public ResultVO<List<Carousel>> getCarouselList() {
        log.info("管理员获取轮播图列表");

        // 查询所有轮播图，按排序值升序排列
        LambdaQueryWrapper<Carousel> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.orderByAsc(Carousel::getSortOrder);
        List<Carousel> carouselList = carouselService.list(queryWrapper);

        // 直接返回数据库中的数据，前端会处理URL拼接
        log.info("获取到 {} 条轮播图", carouselList != null ? carouselList.size() : 0);
        return ResultVO.success(carouselList);
    }

    /**
     * 获取轮播图详情
     *
     * @param id 轮播图ID
     * @param request HTTP请求
     * @return 轮播图详情
     */
    @GetMapping("/carousel/{id}")
    @RequireAdmin("获取轮播图详情")
    public ResultVO<Carousel> getCarouselDetail(@PathVariable Long id) {
        log.info("管理员获取轮播图详情: id={}", id);

        Carousel carousel = carouselService.getById(id);
        if (carousel == null) {
            return ResultVO.error("轮播图不存在");
        }

        // 直接返回数据库中的数据，前端会处理URL拼接
        return ResultVO.success(carousel);
    }

    /**
     * 创建轮播图
     *
     * @param carousel 轮播图信息
     * @param request  HTTP请求
     * @return 创建结果
     */
    @PostMapping("/carousel")
    @RequireAdmin("创建轮播图")
    public ResultVO<Carousel> createCarousel(@RequestBody Carousel carousel, HttpServletRequest request) {
        log.info("管理员创建轮播图: title={}", carousel.getTitle());

        // 参数校验
        if (carousel.getTitle() == null || carousel.getTitle().trim().isEmpty()) {
            return ResultVO.error("轮播图标题不能为空");
        }

        // 获取当前管理员用户ID
        Long userId = (Long) request.getAttribute("currentUserId");

        // 保存轮播图
        boolean success = carouselService.createCarousel(carousel, userId);
        if (success) {
            log.info("轮播图创建成功: id={}", carousel.getId());
            return ResultVO.success(carousel);
        } else {
            return ResultVO.error("轮播图创建失败");
        }
    }

    /**
     * 更新轮播图
     * 如果更换了图片，会自动删除原图片文件
     *
     * @param id       轮播图ID
     * @param carousel 更新的轮播图信息
     * @return 更新结果
     */
    @PutMapping("/carousel/{id}")
    @RequireAdmin("更新轮播图")
    public ResultVO<Carousel> updateCarousel(@PathVariable Long id, @RequestBody Carousel carousel) {
        log.info("管理员更新轮播图: id={}", id);

        // 检查轮播图是否存在
        Carousel existingCarousel = carouselService.getById(id);
        if (existingCarousel == null) {
            return ResultVO.error("轮播图不存在");
        }

        // 检查是否更换了图片
        String oldImageUrl = existingCarousel.getImageUrl();
        String newImageUrl = carousel.getImageUrl();
        if (oldImageUrl != null && !oldImageUrl.isEmpty() && 
            newImageUrl != null && !newImageUrl.equals(oldImageUrl)) {
            // 删除旧图片文件
            boolean fileDeleted = FileUtil.deleteUploadFile(oldImageUrl);
            if (fileDeleted) {
                log.info("轮播图旧图片已删除: {}", oldImageUrl);
            } else {
                log.warn("轮播图旧图片删除失败或不存在: {}", oldImageUrl);
            }
        }

        // 设置轮播图ID
        carousel.setId(id);

        // 更新轮播图
        boolean success = carouselService.updateCarousel(carousel);
        if (success) {
            log.info("轮播图更新成功: id={}", id);
            return ResultVO.success(carouselService.getById(id));
        } else {
            return ResultVO.error("轮播图更新失败");
        }
    }

    /**
     * 删除轮播图
     * 删除轮播图时会同步删除数据库记录和物理文件
     *
     * @param id 轮播图ID
     * @return 删除结果
     */
    @DeleteMapping("/carousel/{id}")
    @RequireAdmin("删除轮播图")
    public ResultVO<Void> deleteCarousel(@PathVariable Long id) {
        log.info("管理员删除轮播图: id={}", id);

        // 检查轮播图是否存在
        Carousel existingCarousel = carouselService.getById(id);
        if (existingCarousel == null) {
            return ResultVO.error("轮播图不存在");
        }

        // 删除轮播图图片文件（同步删除物理文件）
        String imageUrl = existingCarousel.getImageUrl();
        if (imageUrl != null && !imageUrl.isEmpty()) {
            boolean fileDeleted = FileUtil.deleteUploadFile(imageUrl);
            if (fileDeleted) {
                log.info("轮播图图片已删除: {}", imageUrl);
            } else {
                log.warn("轮播图图片删除失败或不存在: {}", imageUrl);
            }
        }

        // 删除轮播图
        boolean success = carouselService.deleteCarousel(id);
        if (success) {
            log.info("轮播图删除成功: id={}", id);
            return ResultVO.success();
        } else {
            return ResultVO.error("轮播图删除失败");
        }
    }

    /**
     * 批量删除轮播图
     * 批量删除时会同步删除所有轮播图的图片文件
     *
     * @param requestBody 请求体，包含ids字段
     * @return 删除结果
     */
    @DeleteMapping("/carousel/batch")
    @RequireAdmin("批量删除轮播图")
    public ResultVO<Void> batchDeleteCarousel(@RequestBody Map<String, List<Long>> requestBody) {
        List<Long> ids = requestBody.get("ids");
        log.info("管理员批量删除轮播图: ids={}", ids);

        if (ids == null || ids.isEmpty()) {
            return ResultVO.error("请选择要删除的轮播图");
        }

        // 先获取所有轮播图的图片路径
        List<Carousel> carousels = carouselService.listByIds(ids);
        int deletedFileCount = 0;

        // 删除所有轮播图图片文件
        for (Carousel carousel : carousels) {
            String imageUrl = carousel.getImageUrl();
            if (imageUrl != null && !imageUrl.isEmpty()) {
                boolean fileDeleted = FileUtil.deleteUploadFile(imageUrl);
                if (fileDeleted) {
                    deletedFileCount++;
                    log.info("轮播图图片已删除: id={}, url={}", carousel.getId(), imageUrl);
                }
            }
        }
        log.info("批量删除轮播图图片完成: 成功删除 {} 个文件", deletedFileCount);

        // 批量删除数据库记录
        boolean success = carouselService.removeByIds(ids);
        if (success) {
            log.info("批量删除轮播图成功: 数量={}", ids.size());
            return ResultVO.success();
        } else {
            return ResultVO.error("批量删除失败");
        }
    }

    /**
     * 更新轮播图排序
     *
     * @param sortList 排序列表
     * @return 更新结果
     */
    @PutMapping("/carousel/sort")
    @RequireAdmin("更新轮播图排序")
    public ResultVO<Void> updateCarouselSort(@RequestBody List<Map<String, Object>> sortList) {
        log.info("管理员更新轮播图排序: 数量={}", sortList != null ? sortList.size() : 0);

        // 参数校验
        if (sortList == null || sortList.isEmpty()) {
            return ResultVO.error("排序列表不能为空");
        }

        try {
            // 遍历排序列表，逐个更新
            for (Map<String, Object> item : sortList) {
                Object idObj = item.get("id");
                if (idObj == null) {
                    continue;
                }
                Long id = Long.valueOf(idObj.toString());

                Object orderObj = item.get("sortOrder");
                if (orderObj == null) {
                    continue;
                }
                Integer sortOrder = Integer.valueOf(orderObj.toString());

                Carousel carousel = new Carousel();
                carousel.setId(id);
                carousel.setSortOrder(sortOrder);
                carouselService.updateById(carousel);
            }

            log.info("轮播图排序更新成功");
            return ResultVO.success();
        } catch (Exception e) {
            log.error("轮播图排序更新失败: {}", e.getMessage(), e);
            return ResultVO.error("排序更新失败: " + e.getMessage());
        }
    }

    /**
     * 更新文章状态
     *
     * @param id     文章ID
     * @param body   请求体，包含status字段
     * @return 更新结果
     */
    @PatchMapping("/articles/{id}/status")
    @RequireAdmin("更新文章状态")
    public ResultVO<Void> updateArticleStatus(@PathVariable Long id, @RequestBody Map<String, Integer> body) {
        Integer status = body.get("status");
        log.info("管理员更新文章状态: id={}, status={}", id, status);

        // 参数校验
        if (status == null || (status != 0 && status != 1)) {
            return ResultVO.error("状态值无效，只能是0（禁用）或1（启用）");
        }

        // 检查文章是否存在
        HealthArticle existingArticle = healthArticleService.getById(id);
        if (existingArticle == null) {
            return ResultVO.error("文章不存在");
        }

        // 更新状态
        HealthArticle article = new HealthArticle();
        article.setId(id);
        article.setStatus(status);

        boolean success = healthArticleService.updateById(article);
        if (success) {
            log.info("文章状态更新成功: id={}, status={}", id, status);
            return ResultVO.success();
        } else {
            return ResultVO.error("状态更新失败");
        }
    }

    /**
     * 批量更新文章排序
     * 用于调整文章显示顺序
     *
     * @param sortList 排序列表，每个元素包含id和sortOrder字段
     * @return 更新结果
     */
    @PutMapping("/articles/sort")
    @RequireAdmin("更新文章排序")
    public ResultVO<Void> updateArticleSort(@RequestBody List<Map<String, Object>> sortList) {
        log.info("管理员更新文章排序: 数量={}", sortList != null ? sortList.size() : 0);

        // 参数校验
        if (sortList == null || sortList.isEmpty()) {
            return ResultVO.error("排序列表不能为空");
        }

        try {
            // 遍历排序列表，逐个更新
            for (Map<String, Object> item : sortList) {
                // 获取文章ID
                Object idObj = item.get("id");
                if (idObj == null) {
                    log.warn("排序项缺少id字段，跳过");
                    continue;
                }
                Long id = Long.valueOf(idObj.toString());

                // 获取排序值
                Object orderObj = item.get("sortOrder");
                if (orderObj == null) {
                    log.warn("排序项缺少sortOrder字段，跳过: id={}", id);
                    continue;
                }
                Integer sortOrder = Integer.valueOf(orderObj.toString());

                // 检查文章是否存在
                HealthArticle existingArticle = healthArticleService.getById(id);
                if (existingArticle == null) {
                    log.warn("文章不存在，跳过: id={}", id);
                    continue;
                }

                // 更新排序值
                HealthArticle article = new HealthArticle();
                article.setId(id);
                article.setSortOrder(sortOrder);

                boolean success = healthArticleService.updateById(article);
                if (!success) {
                    log.warn("更新文章排序失败: id={}", id);
                }
            }

            log.info("文章排序更新成功");
            return ResultVO.success();
        } catch (NumberFormatException e) {
            log.error("排序数据格式错误: {}", e.getMessage());
            return ResultVO.error("排序数据格式错误: " + e.getMessage());
        } catch (Exception e) {
            log.error("更新文章排序失败: {}", e.getMessage(), e);
            return ResultVO.error("更新排序失败: " + e.getMessage());
        }
    }

    // ==================== 文件上传接口 ====================

    /**
     * 上传图片
     * 支持上传头像、文章封面图、轮播图、报告文件等
     * 文件将按类型存储在一级目录中：
     * - avatar/   : 用户头像
     * - article/  : 文章封面图片
     * - carousel/ : 轮播图
     * - report/   : 体检报告文件
     * - other/    : 其他文件
     *
     * @param file    图片文件
     * @param type    图片类型：avatar-头像, article-文章封面, carousel-轮播图, report-报告文件, other-其他
     * @param request HTTP请求
     * @return 上传结果，包含图片URL
     */
    @PostMapping("/upload")
    @RequireAdmin("上传图片")
    public ResultVO<Map<String, String>> uploadImage(
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false, defaultValue = "other") String type,
            HttpServletRequest request) {

        log.info("管理员上传图片: filename={}, size={}, type={}",
                file.getOriginalFilename(), file.getSize(), type);

        // 校验文件是否为空
        if (file.isEmpty()) {
            return ResultVO.error("请选择要上传的文件");
        }

        // 校验文件类型
        String originalFilename = file.getOriginalFilename();
        String extension = getFileExtension(originalFilename).toLowerCase();
        if (!isValidImageExtension(extension)) {
            return ResultVO.error("不支持的文件类型，仅支持 jpg, jpeg, png, gif, webp 格式");
        }

        // 校验文件大小（最大100MB）
        long maxSize = 100 * 1024 * 1024; // 100MB
        if (file.getSize() > maxSize) {
            return ResultVO.error("文件大小不能超过100MB");
        }

        try {
            // 生成存储路径：carousel/xxx.png (一级目录)
            String typePath = getTypePath(type);
            // 数据库只存相对路径：carousel/xxx.png
            String relativePath = typePath + UUID.randomUUID().toString().replace("-", "") + "." + extension;
            
            // 完整文件路径
            String absoluteFilePath = ABSOLUTE_UPLOAD_PATH + relativePath;
            File targetFile = new File(absoluteFilePath);
            
            // 确保父目录存在
            File parentDir = targetFile.getParentFile();
            if (!parentDir.exists()) {
                boolean created = parentDir.mkdirs();
                if (!created) {
                    log.error("创建目录失败: {}", parentDir.getAbsolutePath());
                    return ResultVO.error("创建上传目录失败");
                }
            }

            // 保存文件
            file.transferTo(targetFile);

            log.info("图片上传成功: absolutePath={}, relativePath={}", absoluteFilePath, relativePath);

            // 返回结果 - 数据库存相对路径，前端拼接完整URL
            Map<String, String> result = new HashMap<>();
            result.put("url", relativePath);  // carousel/xxx.png
            result.put("filename", targetFile.getName());
            result.put("originalFilename", originalFilename);
            result.put("size", String.valueOf(file.getSize()));

            return ResultVO.success(result);

        } catch (IOException e) {
            log.error("图片上传失败", e);
            return ResultVO.error("文件上传失败: " + e.getMessage());
        }
    }

    // ==================== 私有工具方法 ====================

    /**
     * 获取文件扩展名
     *
     * @param filename 文件名
     * @return 扩展名（不含点号）
     */
    private String getFileExtension(String filename) {
        if (filename == null || filename.lastIndexOf(".") == -1) {
            return "";
        }
        return filename.substring(filename.lastIndexOf(".") + 1);
    }

    /**
     * 校验是否为有效的图片扩展名
     *
     * @param extension 扩展名
     * @return 是否有效
     */
    private boolean isValidImageExtension(String extension) {
        return "jpg".equals(extension) ||
                "jpeg".equals(extension) ||
                "png".equals(extension) ||
                "gif".equals(extension) ||
                "webp".equals(extension);
    }

    /**
     * 根据类型获取存储子目录
     * 使用一级目录结构：avatar/, article/, carousel/, report/, other/
     *
     * @param type 图片类型：avatar-头像, article-文章封面, carousel-轮播图, report-报告文件, other-其他
     * @return 子目录路径
     */
    private String getTypePath(String type) {
        if (type == null) {
            return "other/";
        }
        switch (type.toLowerCase()) {
            case "avatar":
                return "avatar/";
            case "article":
            case "cover":
                return "article/";
            case "carousel":
            case "banner":
                return "carousel/";
            case "report":
            case "file":
                return "report/";
            case "other":
            default:
                return "other/";
        }
    }

}
