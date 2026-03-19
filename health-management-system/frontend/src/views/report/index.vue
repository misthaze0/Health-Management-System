<template>
  <div class="report-page">
    <!-- Hero Section - 深色背景 -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">REPORT ANALYSIS</div>
        <h1 class="hero-title">报告解读中心</h1>
        <p class="hero-subtitle">Medical Report Analysis & Management</p>
        <div class="hero-desc">
          <p>智能解析体检报告，深度解读健康指标</p>
          <p>支持PDF上传解析，让健康管理更专业、更智能</p>
        </div>
      </div>
    </section>

    <!-- 报告管理区域 -->
    <section class="content-section">
      <div class="section-header">
        <span class="section-num">01</span>
        <h2 class="section-title">报告管理</h2>
        <p class="section-subtitle">Report Management</p>
      </div>

      <!-- 上传工具栏 -->
      <div class="toolbar">
        <button class="btn-upload" @click="showUploadModal = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          上传报告
        </button>
      </div>

      <!-- 报告列表 -->
      <div class="report-list">
        <div v-if="filteredReports.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <p>暂无体检报告</p>
          <span>上传PDF体检报告，AI将自动解读分析</span>
        </div>

        <div
          v-for="report in filteredReports"
          :key="report.id"
          class="report-card"
          :class="{ 'has-analysis': report.status === 3 }"
        >
          <div class="report-main">
            <div class="report-status" :class="getStatusClass(report.status)">
              <span class="status-dot"></span>
            </div>
            <div class="report-info" @click="viewReport(report)">
              <h3 class="report-title">{{ report.title || report.centerName || '体检报告' }}</h3>
              <div class="report-meta">
                <span class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  {{ formatDate(report.examDate) }}
                </span>
                <span class="meta-item" v-if="report.hospitalName">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  {{ report.hospitalName }}
                </span>
                <span class="meta-item" v-if="report.indicatorSummary">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                  </svg>
                  {{ report.indicatorSummary.normal + report.indicatorSummary.abnormal + report.indicatorSummary.warning }} 项指标
                </span>
              </div>
            </div>
            <div class="report-actions">
              <button
                v-if="report.status === 2"
                class="action-btn loading"
                disabled
              >
                <span class="loading-spinner"></span>
                分析中...
              </button>
              <template v-else>
                <button
                  class="action-btn secondary"
                  @click.stop="viewReport(report)"
                >
                  查看详情
                </button>
                <button
                  class="action-btn primary"
                  @click.stop="analyzeReport(report)"
                  :disabled="analyzingId === report.id"
                >
                  <span v-if="analyzingId === report.id" class="loading-spinner"></span>
                  <span v-else>AI分析</span>
                </button>
              </template>
              <button class="action-icon delete" @click.stop="confirmDelete(report)" title="删除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- AI分析预览 -->
          <div v-if="report.status === 3 && report.aiAnalysis" class="report-analysis-preview">
            <div class="preview-header">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
              <span>AI解读摘要</span>
            </div>
            <p class="preview-text">{{ report.aiAnalysis.substring(0, 150) }}...</p>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="filteredReports.length > 0" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredReports.length"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </section>

    <!-- 分析管理区域 -->
    <section class="content-section dark">
      <div class="section-header light">
        <span class="section-num">02</span>
        <h2 class="section-title">分析管理</h2>
        <p class="section-subtitle">AI Analysis Management</p>
      </div>

      <!-- 分析列表工具栏 -->
      <div class="toolbar">
        <div class="toolbar-right">
          <button class="btn-export" @click="exportAnalysis">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            导出
          </button>
        </div>
      </div>

      <!-- 分析列表 -->
      <div class="analysis-list">
        <div v-if="filteredAnalysis.length === 0" class="empty-state light">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <p>暂无AI分析记录</p>
          <span>上传体检报告后将自动生成AI解读，或使用AI文件分析功能</span>
        </div>

        <div
          v-for="item in filteredAnalysis"
          :key="item.id"
          class="analysis-card"
          :class="{ expanded: expandedAnalysis === item.id }"
        >
          <div class="analysis-header" @click="toggleAnalysis(item.id)">
            <div class="analysis-status" :class="item.status">
              <span class="status-dot"></span>
            </div>
            <div class="analysis-info">
              <h4 class="analysis-title">{{ item.reportTitle }}</h4>
              <div class="analysis-meta">
                <span class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  {{ formatDate(item.createdAt) }}
                </span>
                <span class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                  </svg>
                  {{ item.indicatorCount }} 项指标
                </span>
                <span class="meta-item" :class="{ abnormal: item.abnormalCount > 0 }">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                  {{ item.abnormalCount }} 项异常
                </span>
              </div>
            </div>
            <div class="analysis-actions">
              <button class="action-icon" @click.stop="viewAnalysisDetail(item)" title="查看详情">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
              <button class="action-icon" @click.stop="regenerateAnalysis(item)" title="重新分析">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <polyline points="23 4 23 10 17 10"/>
                  <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                </svg>
              </button>
              <button class="action-icon delete" @click.stop="deleteAnalysis(item)" title="删除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
              <svg class="expand-icon" :class="{ rotated: expandedAnalysis === item.id }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>
          </div>

          <div v-if="expandedAnalysis === item.id" class="analysis-content">
            <div class="content-section">
              <h5>AI解读摘要</h5>
              <p class="summary-text">{{ item.summary || '暂无解读摘要' }}</p>
            </div>
            <div class="content-section" v-if="item.keyFindings?.length">
              <h5>关键发现</h5>
              <ul class="findings-list">
                <li v-for="(finding, idx) in item.keyFindings" :key="idx" :class="finding.type">
                  <span class="finding-marker" :class="finding.type"></span>
                  {{ finding.text }}
                </li>
              </ul>
            </div>
            <div class="content-section" v-if="item.recommendations?.length">
              <h5>健康建议</h5>
              <div class="recommendation-tags">
                <span v-for="(rec, idx) in item.recommendations" :key="idx" class="rec-tag">
                  {{ rec }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- PDF上传模态框 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal-content upload-modal">
        <div class="modal-header">
          <div class="modal-title-group">
            <h3>上传体检报告</h3>
            <p>支持 PDF 格式，文件大小不超过 20MB</p>
          </div>
          <button class="modal-close" @click="closeUploadModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div
            class="upload-area"
            :class="{ 'has-file': uploadFile, 'is-dragging': isDragging }"
            @click="triggerFileInput"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleFileDrop"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".pdf"
              @change="handleFileSelect"
              style="display: none"
            />
            <div v-if="!uploadFile" class="upload-placeholder">
              <div class="upload-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
              </div>
              <p class="upload-text">点击或拖拽文件到此处上传</p>
              <p class="upload-hint">支持 PDF 格式，最大 20MB</p>
            </div>
            <div v-else class="upload-file-info">
              <div class="file-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div class="file-details">
                <p class="file-name">{{ uploadFile.name }}</p>
                <p class="file-size">{{ formatFileSize(uploadFile.size) }}</p>
              </div>
              <button class="file-remove" @click.stop="removeFile">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>

          <div v-if="uploadFile" class="upload-form">
            <div class="form-group">
              <label>报告标题 <span class="required">*</span></label>
              <input
                v-model="uploadForm.title"
                type="text"
                placeholder="请输入报告标题"
              />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>体检日期 <span class="required">*</span></label>
                <input
                  v-model="uploadForm.examDate"
                  type="date"
                  :max="today"
                />
              </div>
              <div class="form-group">
                <label>体检机构</label>
                <input
                  v-model="uploadForm.centerName"
                  type="text"
                  placeholder="请输入体检机构名称"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeUploadModal">取消</button>
          <button
            class="btn-confirm"
            :disabled="!canUpload || uploading"
            @click="submitUpload"
          >
            <span v-if="uploading" class="loading-spinner"></span>
            <span v-else>确认上传</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 报告详情模态框 -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-content detail-modal">
        <div class="modal-header">
          <div class="modal-title-group">
            <h3>{{ currentReport?.title || currentReport?.centerName || '体检报告详情' }}</h3>
            <p v-if="currentReport?.examDate">体检日期: {{ formatDate(currentReport.examDate) }}</p>
          </div>
          <button class="modal-close" @click="closeDetailModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <!-- 指标概览 -->
          <div v-if="currentReport?.indicatorSummary" class="indicator-summary">
            <div class="summary-item normal">
              <span class="summary-num">{{ currentReport.indicatorSummary.normal }}</span>
              <span class="summary-label">正常</span>
            </div>
            <div class="summary-item warning">
              <span class="summary-num">{{ currentReport.indicatorSummary.warning }}</span>
              <span class="summary-label">偏高/偏低</span>
            </div>
            <div class="summary-item abnormal">
              <span class="summary-num">{{ currentReport.indicatorSummary.abnormal }}</span>
              <span class="summary-label">异常</span>
            </div>
          </div>

          <!-- AI分析结果 -->
          <div v-if="currentReport?.aiAnalysis" class="ai-analysis-section">
            <h4 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
              AI智能解读
            </h4>
            <div class="analysis-content" v-html="formatAnalysis(currentReport.aiAnalysis)"></div>
          </div>

          <!-- 指标列表 -->
          <div v-if="currentReport?.indicators?.length" class="indicators-section">
            <h4 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
              详细指标
            </h4>
            <div class="indicators-list">
              <div
                v-for="indicator in currentReport.indicators"
                :key="indicator.id"
                class="indicator-item"
                :class="getIndicatorStatusClass(indicator)"
              >
                <div class="indicator-main">
                  <span class="indicator-name">{{ indicator.indicatorName }}</span>
                  <span class="indicator-value" :class="getIndicatorStatusClass(indicator)">
                    {{ indicator.indicatorValue }}
                  </span>
                </div>
                <div class="indicator-reference">
                  参考范围: {{ indicator.referenceRange }}
                </div>
              </div>
            </div>
          </div>

          <div v-else class="no-data">
            <p>暂无详细指标数据</p>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeDetailModal">关闭</button>
          <button
            v-if="currentReport?.status === 1"
            class="btn-confirm"
            @click="analyzeReport(currentReport); closeDetailModal()"
            :disabled="analyzingId === currentReport?.id"
          >
            <span v-if="analyzingId === currentReport?.id" class="loading-spinner"></span>
            <span v-else>AI解读</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-content confirm-modal">
        <div class="confirm-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <h3>确认删除</h3>
        <p>确定要删除这份体检报告吗？此操作不可恢复。</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancelDelete">取消</button>
          <button class="btn-danger" @click="executeDelete">确认删除</button>
        </div>
      </div>
    </div>

    <!-- Kimi AI 文件分析模态框 -->
    <div v-if="showFileAnalysisModal" class="modal-overlay" @click.self="closeFileAnalysisModal">
      <div class="modal-content analysis-modal">
        <div class="modal-header">
          <div class="modal-title-group">
            <h3>Kimi AI 智能分析报告</h3>
            <p>上传体检报告文件，AI将自动分析并生成结构化报告</p>
          </div>
          <button class="modal-close" @click="closeFileAnalysisModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <!-- 报告类型选择 -->
          <div class="form-group">
            <label>报告类型</label>
            <select v-model="selectedReportType" class="report-type-select">
              <option v-for="option in reportTypeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <!-- 文件上传区域 -->
          <div
            v-if="!fileAnalysisResult"
            class="upload-area"
            :class="{ 'has-file': analysisFile }"
            @click="triggerFileAnalysisInput"
          >
            <input
              ref="fileAnalysisInput"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.bmp,.gif,.webp,.tiff"
              @change="handleFileAnalysisSelect"
              style="display: none"
            />
            <div v-if="!analysisFile" class="upload-placeholder">
              <div class="upload-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
              </div>
              <p class="upload-text">点击上传体检报告文件</p>
              <p class="upload-hint">支持 PDF、JPG、PNG 等格式，最大 20MB</p>
            </div>
            <div v-else class="upload-file-info">
              <div class="file-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div class="file-details">
                <p class="file-name">{{ analysisFile.name }}</p>
                <p class="file-size">{{ formatFileSize(analysisFile.size) }}</p>
              </div>
              <button class="file-remove" @click.stop="removeAnalysisFile">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 分析结果展示 -->
          <div v-else class="analysis-result">
            <div class="result-section">
              <h4 class="result-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <path d="M9 12l2 2 4-4"/>
                  <circle cx="12" cy="12" r="10"/>
                </svg>
                报告摘要
              </h4>
              <div class="result-content">
                <div class="summary-grid">
                  <div class="summary-item">
                    <span class="summary-label">报告类型</span>
                    <span class="summary-value">{{ fileAnalysisResult.report_summary?.report_type || '-' }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">体检日期</span>
                    <span class="summary-value">{{ fileAnalysisResult.report_summary?.exam_date || '-' }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">体检机构</span>
                    <span class="summary-value">{{ fileAnalysisResult.report_summary?.exam_center || '-' }}</span>
                  </div>
                </div>
                <p class="overall-assessment">{{ fileAnalysisResult.report_summary?.overall_assessment || '' }}</p>
              </div>
            </div>

            <!-- 指标列表 -->
            <div v-if="fileAnalysisResult.indicators?.length" class="result-section">
              <h4 class="result-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
                检测指标 ({{ fileAnalysisResult.indicators.length }}项)
              </h4>
              <div class="indicators-table">
                <div class="table-header">
                  <span>指标名称</span>
                  <span>检测值</span>
                  <span>参考范围</span>
                  <span>状态</span>
                </div>
                <div
                  v-for="indicator in fileAnalysisResult.indicators"
                  :key="indicator.name"
                  class="table-row"
                  :class="indicator.status"
                >
                  <span class="indicator-name">{{ indicator.name }}</span>
                  <span class="indicator-value">{{ indicator.value }} {{ indicator.unit }}</span>
                  <span class="indicator-range">{{ indicator.reference_range }}</span>
                  <span class="indicator-status" :class="indicator.status">
                    {{ indicator.status === 'normal' ? '正常' : indicator.status === 'warning' ? '警告' : '异常' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 异常发现 -->
            <div v-if="fileAnalysisResult.abnormal_findings?.length" class="result-section">
              <h4 class="result-title warning">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                异常发现 ({{ fileAnalysisResult.abnormal_findings.length }}项)
              </h4>
              <div class="abnormal-list">
                <div
                  v-for="(finding, idx) in fileAnalysisResult.abnormal_findings"
                  :key="idx"
                  class="abnormal-item"
                  :class="finding.severity"
                >
                  <div class="abnormal-header">
                    <span class="abnormal-indicator">{{ finding.indicator }}</span>
                    <span class="abnormal-severity" :class="finding.severity">
                      {{ finding.severity === 'low' ? '轻度' : finding.severity === 'medium' ? '中度' : '重度' }}
                    </span>
                  </div>
                  <p class="abnormal-desc">{{ finding.description }}</p>
                  <p class="abnormal-recommendation">建议: {{ finding.recommendation }}</p>
                </div>
              </div>
            </div>

            <!-- 健康建议 -->
            <div v-if="fileAnalysisResult.health_suggestions?.length" class="result-section">
              <h4 class="result-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
                健康建议
              </h4>
              <ul class="suggestion-list">
                <li v-for="(suggestion, idx) in fileAnalysisResult.health_suggestions" :key="idx">
                  {{ suggestion }}
                </li>
              </ul>
            </div>

            <!-- 随访建议 -->
            <div v-if="fileAnalysisResult.follow_up" class="result-section">
              <h4 class="result-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                随访建议
              </h4>
              <div class="follow-up-content">
                <div class="urgency-level" :class="fileAnalysisResult.follow_up.urgency_level">
                  紧急程度: {{ fileAnalysisResult.follow_up.urgency_level === 'low' ? '常规随访' : fileAnalysisResult.follow_up.urgency_level === 'medium' ? '建议近期就诊' : '建议尽快就诊' }}
                </div>
                <div v-if="fileAnalysisResult.follow_up.recommended_items?.length" class="follow-up-section">
                  <span class="follow-up-label">建议复查:</span>
                  <span class="follow-up-value">{{ fileAnalysisResult.follow_up.recommended_items.join('、') }}</span>
                </div>
                <div v-if="fileAnalysisResult.follow_up.recommended_departments?.length" class="follow-up-section">
                  <span class="follow-up-label">建议科室:</span>
                  <span class="follow-up-value">{{ fileAnalysisResult.follow_up.recommended_departments.join('、') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeFileAnalysisModal">关闭</button>
          <button
            v-if="!fileAnalysisResult && analysisFile"
            class="btn-confirm"
            :disabled="isAnalyzingFile"
            @click="startFileAnalysis"
          >
            <span v-if="isAnalyzingFile" class="loading-spinner"></span>
            <span v-else>开始分析</span>
          </button>
          <button
            v-if="fileAnalysisResult"
            class="btn-confirm"
            @click="closeFileAnalysisModal"
          >
            完成
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getReports, deleteReport, uploadReport, analyzeReport as analyzeReportApi, analyzeMedicalReportFile } from '@/api/report'
import { deleteChatHistoryBatch, clearAllChatHistory } from '@/api/aiDoctor'
import dayjs from 'dayjs'

const userStore = useUserStore()
const router = useRouter()

// 报告列表数据
const reports = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// 筛选选项
const filterOptions = [
  { label: '全部', value: 'all' },
  { label: '待解读', value: 'pending' },
  { label: '分析中', value: 'analyzing' },
  { label: '已完成', value: 'completed' }
]

// 报告统计
const reportStats = computed(() => {
  return {
    total: reports.value.length,
    analyzed: reports.value.filter(r => r.status === 3).length,
    pending: reports.value.filter(r => r.status === 1).length
  }
})

// 筛选后的报告
const filteredReports = computed(() => {
  let result = reports.value

  // 状态筛选
  if (currentFilter.value !== 'all') {
    const statusMap = {
      'pending': 1,
      'analyzing': 2,
      'completed': 3
    }
    result = result.filter(r => r.status === statusMap[currentFilter.value])
  }

  // 搜索筛选
  const query = searchQuery.value.toLowerCase()
  if (query) {
    result = result.filter(r =>
      (r.title && r.title.toLowerCase().includes(query)) ||
      (r.centerName && r.centerName.toLowerCase().includes(query)) ||
      (r.hospitalName && r.hospitalName.toLowerCase().includes(query))
    )
  }

  return result
})

// 分析管理数据
const analysisStats = ref({
  total: 0,
  pending: 0,
  completed: 0,
  abnormal: 0
})
const analysisList = ref([])
const currentAnalysisTab = ref('all')
const analysisSearchQuery = ref('')
const expandedAnalysis = ref(null)

// 分析管理标签
const analysisTabs = [
  { label: '全部', value: 'all', count: 0 },
  { label: '待处理', value: 'pending', count: 0 },
  { label: '已完成', value: 'completed', count: 0 },
  { label: '有异常', value: 'abnormal', count: 0 }
]

// 筛选后的分析列表
const filteredAnalysis = computed(() => {
  let result = analysisList.value

  // 按标签筛选
  if (currentAnalysisTab.value !== 'all') {
    result = result.filter(item => item.status === currentAnalysisTab.value)
  }

  // 搜索筛选
  const query = analysisSearchQuery.value.toLowerCase()
  if (query) {
    result = result.filter(item =>
      item.reportTitle?.toLowerCase().includes(query)
    )
  }

  return result
})

// 上传相关
const showUploadModal = ref(false)
const uploadFile = ref(null)
const uploading = ref(false)
const isDragging = ref(false)
const fileInput = ref(null)
const uploadForm = ref({
  title: '',
  examDate: '',
  centerName: ''
})

// 详情模态框
const showDetailModal = ref(false)
const currentReport = ref(null)

// 删除确认
const showDeleteConfirm = ref(false)
const reportToDelete = ref(null)

// AI分析状态
const analyzingId = ref(null)

// Kimi文件分析相关
const showFileAnalysisModal = ref(false)
const analysisFile = ref(null)
const isAnalyzingFile = ref(false)
const fileAnalysisResult = ref(null)
const fileAnalysisInput = ref(null)
const selectedReportType = ref('general')
const reportTypeOptions = [
  { label: '通用体检报告', value: 'general' },
  { label: '血液检查报告', value: 'blood_test' },
  { label: '影像检查报告', value: 'imaging' },
  { label: '全面体检报告', value: 'physical_exam' }
]

// 计算属性
const today = computed(() => dayjs().format('YYYY-MM-DD'))
const canUpload = computed(() => {
  return uploadFile.value && uploadForm.value.title.trim() && uploadForm.value.examDate
})

// 加载报告列表
const loadReports = async () => {
  loading.value = true
  try {
    const userId = userStore.userInfo?.id
    if (!userId) {
      ElMessage.warning('请先登录')
      return
    }
    const data = await getReports(userId)
    reports.value = data || []
    loadAnalysisData()
  } catch (error) {
    console.error('加载报告失败:', error)
    ElMessage.error('加载报告失败')
  } finally {
    loading.value = false
  }
}

// 分析管理方法
const loadAnalysisData = () => {
  // 从报告中提取分析数据
  const analyzedReports = reports.value.filter(r => r.status === 3)
  analysisList.value = analyzedReports.map(report => ({
    id: report.id,
    reportTitle: report.title || report.centerName || '体检报告',
    status: 'completed',
    createdAt: report.examDate || report.createdAt,
    indicatorCount: report.indicators?.length || report.indicatorSummary?.normal + report.indicatorSummary?.abnormal + report.indicatorSummary?.warning || 0,
    abnormalCount: report.indicatorSummary?.abnormal || report.indicators?.filter(i => i.status === 1).length || 0,
    summary: report.aiAnalysis?.substring(0, 200) + '...' || '',
    keyFindings: report.indicators?.filter(i => i.status !== 0).map(i => ({
      type: i.status === 1 ? 'abnormal' : 'warning',
      text: `${i.indicatorName}: ${i.indicatorValue} (${i.referenceRange})`
    })) || [],
    recommendations: report.aiAnalysis ? extractRecommendations(report.aiAnalysis) : []
  }))

  // 更新统计数据
  analysisStats.value = {
    total: analysisList.value.length,
    pending: reports.value.filter(r => r.status === 2).length,
    completed: analysisList.value.length,
    abnormal: analysisList.value.filter(a => a.abnormalCount > 0).length
  }

  // 更新标签计数
  analysisTabs[0].count = analysisStats.value.total
  analysisTabs[1].count = analysisStats.value.pending
  analysisTabs[2].count = analysisStats.value.completed
  analysisTabs[3].count = analysisStats.value.abnormal
}

// 提取健康建议
const extractRecommendations = (analysisText) => {
  const recommendations = []
  const lines = analysisText.split('\n')
  let inRecommendationSection = false

  for (const line of lines) {
    if (line.includes('建议') || line.includes('推荐') || line.includes('注意')) {
      inRecommendationSection = true
    }
    if (inRecommendationSection && line.trim().startsWith('-')) {
      recommendations.push(line.trim().substring(1).trim())
    }
    if (recommendations.length >= 5) break
  }

  return recommendations
}

// 切换分析展开状态
const toggleAnalysis = (id) => {
  expandedAnalysis.value = expandedAnalysis.value === id ? null : id
}

// 查看分析详情
const viewAnalysisDetail = (item) => {
  const report = reports.value.find(r => r.id === item.id)
  if (report) {
    viewReport(report)
  }
}

// 重新分析
const regenerateAnalysis = async (item) => {
  const report = reports.value.find(r => r.id === item.id)
  if (report) {
    await analyzeReport(report)
    loadAnalysisData()
  }
}

// 删除分析
const deleteAnalysis = async (item) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条AI分析记录吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 从前端列表移除
    analysisList.value = analysisList.value.filter(a => a.id !== item.id)

    // 更新统计数据
    analysisStats.value.total--
    if (item.abnormalCount > 0) {
      analysisStats.value.abnormal--
    }

    ElMessage.success('已删除分析记录')
  } catch (error) {
    // 取消删除
  }
}

// 导出分析
const exportAnalysis = () => {
  const data = filteredAnalysis.value.map(item => ({
    '报告标题': item.reportTitle,
    '分析日期': formatDate(item.createdAt),
    '指标数量': item.indicatorCount,
    '异常数量': item.abnormalCount,
    'AI摘要': item.summary
  }))

  // 简单的CSV导出
  const headers = Object.keys(data[0] || {})
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(h => `"${row[h]}"`).join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `AI分析报告_${dayjs().format('YYYY-MM-DD')}.csv`
  link.click()

  ElMessage.success('分析报告已导出')
}

// ========== Kimi 文件分析相关方法 ==========

// 打开文件分析模态框
const openFileAnalysisModal = () => {
  showFileAnalysisModal.value = true
  analysisFile.value = null
  fileAnalysisResult.value = null
}

// 关闭文件分析模态框
const closeFileAnalysisModal = () => {
  showFileAnalysisModal.value = false
  analysisFile.value = null
  fileAnalysisResult.value = null
  if (fileAnalysisInput.value) {
    fileAnalysisInput.value.value = ''
  }
}

// 触发文件选择
const triggerFileAnalysisInput = () => {
  fileAnalysisInput.value?.click()
}

// 处理文件选择
const handleFileAnalysisSelect = (event) => {
  const file = event.target.files[0]
  if (file) validateAndSetAnalysisFile(file)
}

// 验证并设置分析文件
const validateAndSetAnalysisFile = (file) => {
  const allowedTypes = [
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/bmp',
    'image/gif',
    'image/webp',
    'image/tiff'
  ]

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('不支持的文件类型，请上传 PDF 或图片格式')
    return
  }

  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 20MB')
    return
  }

  analysisFile.value = file
}

// 移除分析文件
const removeAnalysisFile = () => {
  analysisFile.value = null
  fileAnalysisResult.value = null
  if (fileAnalysisInput.value) {
    fileAnalysisInput.value.value = ''
  }
}

// 开始文件分析
const startFileAnalysis = async () => {
  if (!analysisFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  isAnalyzingFile.value = true
  try {
    const result = await analyzeMedicalReportFile(analysisFile.value, selectedReportType.value)

    if (result.code === 200) {
      fileAnalysisResult.value = result.data
      ElMessage.success('分析报告生成成功')

      // 将分析结果添加到分析列表
      const newAnalysis = {
        id: Date.now(),
        reportTitle: result.data.report_summary?.report_type || 'AI分析报告',
        status: 'completed',
        createdAt: new Date().toISOString(),
        indicatorCount: result.data.indicators?.length || 0,
        abnormalCount: result.data.abnormal_findings?.length || 0,
        summary: result.data.report_summary?.overall_assessment || '',
        kimiAnalysis: result.data, // 保存完整的Kimi分析结果
        keyFindings: result.data.abnormal_findings?.map(f => ({
          type: f.severity === 'high' ? 'abnormal' : 'warning',
          text: `${f.indicator}: ${f.description}`
        })) || [],
        recommendations: result.data.health_suggestions || []
      }

      analysisList.value.unshift(newAnalysis)
      analysisStats.value.total++
      analysisStats.value.completed++
      if (newAnalysis.abnormalCount > 0) {
        analysisStats.value.abnormal++
      }
    } else {
      throw new Error(result.message || '分析失败')
    }
  } catch (error) {
    console.error('文件分析失败:', error)
    ElMessage.error(error.message || '文件分析失败，请重试')
  } finally {
    isAnalyzingFile.value = false
  }
}

// 上传相关方法
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) validateAndSetFile(file)
}

const handleFileDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) validateAndSetFile(file)
}

const validateAndSetFile = (file) => {
  if (file.type !== 'application/pdf') {
    ElMessage.error('请上传PDF格式的文件')
    return
  }
  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过20MB')
    return
  }
  uploadFile.value = file
  // 自动填充标题
  if (!uploadForm.value.title) {
    uploadForm.value.title = file.name.replace('.pdf', '')
  }
}

const removeFile = () => {
  uploadFile.value = null
  uploadForm.value = { title: '', examDate: '', centerName: '' }
  if (fileInput.value) fileInput.value.value = ''
}

const closeUploadModal = () => {
  showUploadModal.value = false
  removeFile()
}

const submitUpload = async () => {
  if (!canUpload.value) return

  uploading.value = true
  try {
    const userId = userStore.userInfo?.id
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    formData.append('title', uploadForm.value.title)
    formData.append('examDate', uploadForm.value.examDate)
    formData.append('centerName', uploadForm.value.centerName)
    formData.append('userId', userId)

    await uploadReport(formData)
    ElMessage.success('报告上传成功')
    closeUploadModal()
    loadReports()
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

// 查看报告详情 - 跳转到PDF预览页面
const viewReport = (report) => {
  router.push(`/report/pdf/${report.id}`)
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentReport.value = null
}

// AI解读报告
const analyzeReport = async (report) => {
  analyzingId.value = report.id
  try {
    await analyzeReportApi(report.id)
    ElMessage.success('AI解读完成')
    await loadReports()
  } catch (error) {
    console.error('AI解读失败:', error)
    ElMessage.error('AI解读失败，请重试')
  } finally {
    analyzingId.value = null
  }
}

// 删除报告
const confirmDelete = (report) => {
  reportToDelete.value = report
  showDeleteConfirm.value = true
}

const cancelDelete = () => {
  showDeleteConfirm.value = false
  reportToDelete.value = null
}

const executeDelete = async () => {
  if (!reportToDelete.value) return

  try {
    await deleteReport(reportToDelete.value.id)
    ElMessage.success('删除成功')
    reports.value = reports.value.filter(r => r.id !== reportToDelete.value.id)
    loadAnalysisData()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  } finally {
    cancelDelete()
  }
}

// 搜索和分页
const handleSearch = () => {
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handlePageChange = (page) => {
  currentPage.value = page
}

// 工具函数
const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

const formatFileSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

const getStatusClass = (status) => {
  const classMap = {
    1: 'pending',
    2: 'analyzing',
    3: 'completed'
  }
  return classMap[status] || 'pending'
}

const getIndicatorStatusClass = (indicator) => {
  if (!indicator.referenceRange) return ''
  const value = parseFloat(indicator.indicatorValue)
  const range = indicator.referenceRange

  if (range.includes('-')) {
    const [min, max] = range.split('-').map(v => parseFloat(v.trim()))
    if (value < min || value > max) return 'abnormal'
  } else if (range.includes('<')) {
    const max = parseFloat(range.replace(/[^\d.]/g, ''))
    if (value >= max) return 'abnormal'
  } else if (range.includes('>')) {
    const min = parseFloat(range.replace(/[^\d.]/g, ''))
    if (value <= min) return 'abnormal'
  }
  return ''
}

const formatAnalysis = (text) => {
  if (!text) return ''
  return text
    .replace(/\n/g, '<br>')
    .replace(/#{1,6}\s*(.+)/g, '<h4>$1</h4>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
}

// 监听报告变化，更新分析数据
watch(reports, () => {
  loadAnalysisData()
}, { deep: true })

onMounted(async () => {
  // 如果已登录但用户信息未加载，先获取用户信息
  if (userStore.isLoggedIn && !userStore.userInfo?.id) {
    try {
      await userStore.fetchUserInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
  loadReports()
})
</script>

<style scoped lang="scss">
// 页面基础样式
.report-page {
  min-height: 100vh;
  background: #f8fafc;
}

// Hero Section - 深色背景
.hero-section {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  padding: 80px 24px 100px;
  text-align: center;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(ellipse at 20% 50%, rgba(56, 189, 248, 0.1) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
    pointer-events: none;
  }
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-block;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: #38bdf8;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 2px;
  margin-bottom: 24px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16px;
  letter-spacing: -1px;
}

.hero-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 24px;
  font-weight: 400;
}

.hero-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  line-height: 1.8;

  p {
    margin: 8px 0;
  }
}

// 内容区域
.content-section {
  padding: 40px 24px;
  max-width: 1200px;
  margin: 0 auto;

  &.dark {
    background: #0f172a;
    max-width: 100%;
    padding: 40px 24px;

    .section-header.light {
      .section-num,
      .section-title {
        color: #fff;
      }
      .section-subtitle {
        color: rgba(255, 255, 255, 0.5);
      }
    }
  }
}

// 区域标题
.section-header {
  text-align: center;
  margin-bottom: 24px;

  .section-num {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    color: #3b82f6;
    margin-bottom: 8px;
    letter-spacing: 2px;
  }

  .section-title {
    font-size: 28px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
  }

  .section-subtitle {
    font-size: 13px;
    color: #64748b;
    font-weight: 400;
  }
}

// 工具栏
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 10px 20px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }

  &.active {
    background: #3b82f6;
    border-color: #3b82f6;
    color: #fff;
  }
}

.tab-badge {
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  font-size: 12px;
}

.search-box {
  position: relative;
  width: 280px;

  input {
    width: 100%;
    padding: 10px 12px 10px 40px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.2s;

    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }

  .search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
  }
}

.btn-upload,
.btn-export {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #3b82f6;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #2563eb;
  }
}

.btn-export {
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #475569;

  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
  }
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

// 报告列表
.report-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #94a3b8;
  text-align: center;
  background: #fff;
  border-radius: 12px;
  border: 2px dashed #e2e8f0;

  &.light {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.5);
  }

  .empty-icon {
    width: 64px;
    height: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    font-size: 16px;
    font-weight: 500;
    color: #64748b;
    margin-bottom: 8px;
  }

  span {
    font-size: 14px;
  }
}

.empty-state.light {
  p {
    color: rgba(255, 255, 255, 0.7);
  }
}

.report-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;

  &:hover {
    border-color: #cbd5e1;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }

  &.has-analysis {
    border-left: 3px solid #10b981;
  }
}

.report-main {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.report-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &.pending {
    background: #f59e0b;
  }
  &.analyzing {
    background: #3b82f6;
    animation: pulse 2s infinite;
  }
  &.completed {
    background: #10b981;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.report-info {
  flex: 1;
  cursor: pointer;

  .report-title {
    font-size: 16px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 8px;
  }

  .report-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;

    .meta-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: #64748b;

      svg {
        color: #94a3b8;
      }
    }
  }
}

.report-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;

  &.primary {
    background: #3b82f6;
    color: #fff;

    &:hover:not(:disabled) {
      background: #2563eb;
    }
  }

  &.secondary {
    background: #f1f5f9;
    color: #475569;

    &:hover {
      background: #e2e8f0;
    }
  }

  &.loading {
    background: #f1f5f9;
    color: #94a3b8;
    cursor: not-allowed;
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.action-icon {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;

  &:hover {
    background: #f1f5f9;
    color: #334155;
  }

  &.delete:hover {
    background: #fef2f2;
    color: #ef4444;
  }
}

.report-analysis-preview {
  padding: 16px 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;

  .preview-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #10b981;
    margin-bottom: 8px;

    svg {
      color: #10b981;
    }
  }

  .preview-text {
    font-size: 14px;
    color: #64748b;
    line-height: 1.6;
    margin: 0;
  }
}

// 分页
.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

// 分析列表
.analysis-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.08);
  }

  &.expanded {
    border-color: #3b82f6;
  }
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  cursor: pointer;
}

.analysis-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &.completed {
    background: #10b981;
  }
  &.abnormal {
    background: #ef4444;
  }
}

.analysis-info {
  flex: 1;

  .analysis-title {
    font-size: 16px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 8px;
  }

  .analysis-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;

    .meta-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: rgba(255, 255, 255, 0.6);

      svg {
        color: rgba(255, 255, 255, 0.4);
      }

      &.abnormal {
        color: #ef4444;

        svg {
          color: #ef4444;
        }
      }
    }
  }
}

.analysis-actions {
  display: flex;
  align-items: center;
  gap: 8px;

  .action-icon {
    color: rgba(255, 255, 255, 0.6);

    &:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }

    &.delete:hover {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
    }
  }
}

.expand-icon {
  color: rgba(255, 255, 255, 0.4);
  transition: transform 0.3s;
  margin-left: 8px;

  &.rotated {
    transform: rotate(180deg);
  }
}

.analysis-content {
  padding: 0 20px 20px 44px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideDown 0.3s ease;

  .content-section {
    margin-top: 20px;

    h5 {
      font-size: 14px;
      font-weight: 600;
      color: rgba(255, 255, 255, 0.8);
      margin-bottom: 12px;
    }
  }

  .summary-text {
    font-size: 14px;
    line-height: 1.7;
    color: rgba(255, 255, 255, 0.7);
    background: rgba(255, 255, 255, 0.05);
    padding: 16px;
    border-radius: 8px;
  }

  .findings-list {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 10px 0;
      font-size: 14px;
      color: rgba(255, 255, 255, 0.7);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);

      &:last-child {
        border-bottom: none;
      }
    }
  }

  .finding-marker {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 6px;
    flex-shrink: 0;

    &.abnormal {
      background: #ef4444;
    }

    &.warning {
      background: #f59e0b;
    }
  }

  .recommendation-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .rec-tag {
      padding: 6px 12px;
      background: rgba(59, 130, 246, 0.2);
      color: #60a5fa;
      font-size: 13px;
      border-radius: 6px;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 模态框
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;

  h3 {
    font-size: 20px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 4px;
  }

  p {
    font-size: 14px;
    color: #64748b;
  }
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;

  &:hover {
    background: #f1f5f9;
    color: #334155;
  }
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
}

// 上传区域
.upload-area {
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover,
  &.is-dragging {
    border-color: #3b82f6;
    background: #eff6ff;
  }

  &.has-file {
    border-style: solid;
    border-color: #10b981;
    background: #f0fdf4;
  }
}

.upload-placeholder {
  .upload-icon {
    color: #94a3b8;
    margin-bottom: 16px;
  }

  .upload-text {
    font-size: 16px;
    font-weight: 500;
    color: #334155;
    margin-bottom: 8px;
  }

  .upload-hint {
    font-size: 14px;
    color: #94a3b8;
  }
}

.upload-file-info {
  display: flex;
  align-items: center;
  gap: 16px;

  .file-icon {
    color: #10b981;
  }

  .file-details {
    flex: 1;
    text-align: left;

    .file-name {
      font-size: 16px;
      font-weight: 500;
      color: #334155;
      margin-bottom: 4px;
    }

    .file-size {
      font-size: 14px;
      color: #94a3b8;
    }
  }

  .file-remove {
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #94a3b8;
    transition: all 0.2s;

    &:hover {
      background: #fef2f2;
      color: #ef4444;
    }
  }
}

// 表单
.upload-form {
  margin-top: 24px;
}

.form-group {
  margin-bottom: 16px;

  label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    color: #334155;
    margin-bottom: 6px;

    .required {
      color: #ef4444;
    }
  }

  input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    transition: all 0.2s;

    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

// 按钮
.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 8px;
  font-size: 14px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
  }
}

.btn-confirm {
  padding: 10px 20px;
  border: none;
  background: #3b82f6;
  border-radius: 8px;
  font-size: 14px;
  color: #fff;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: #2563eb;
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.btn-danger {
  padding: 10px 20px;
  border: none;
  background: #ef4444;
  border-radius: 8px;
  font-size: 14px;
  color: #fff;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #dc2626;
  }
}

// 详情模态框
.detail-modal {
  max-width: 800px;
}

.indicator-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;

  .summary-item {
    flex: 1;
    text-align: center;
    padding: 16px;
    border-radius: 8px;

    &.normal {
      background: #f0fdf4;
      .summary-num { color: #10b981; }
    }

    &.warning {
      background: #fffbeb;
      .summary-num { color: #f59e0b; }
    }

    &.abnormal {
      background: #fef2f2;
      .summary-num { color: #ef4444; }
    }

    .summary-num {
      display: block;
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 4px;
    }

    .summary-label {
      font-size: 13px;
      color: #64748b;
    }
  }
}

.ai-analysis-section,
.indicators-section {
  margin-bottom: 24px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 16px;

    svg {
      color: #3b82f6;
    }
  }

  .analysis-content {
    background: #f8fafc;
    padding: 20px;
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.7;
    color: #475569;

    :deep(h4) {
      font-size: 15px;
      font-weight: 600;
      color: #334155;
      margin: 16px 0 8px;
    }

    :deep(strong) {
      color: #334155;
    }
  }
}

.indicators-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid transparent;

  &.abnormal {
    border-left-color: #ef4444;
    background: #fef2f2;

    .indicator-value {
      color: #ef4444;
    }
  }

  .indicator-main {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .indicator-name {
    font-size: 14px;
    color: #334155;
  }

  .indicator-value {
    font-size: 14px;
    font-weight: 600;
    color: #334155;
  }

  .indicator-reference {
    font-size: 13px;
    color: #94a3b8;
  }
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}

// 确认模态框
.confirm-modal {
  max-width: 400px;
  text-align: center;
  padding: 32px;

  .confirm-icon {
    color: #f59e0b;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 8px;
  }

  p {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 24px;
  }

  .confirm-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
  }
}

// AI文件分析模态框
.analysis-modal {
  max-width: 900px;
  max-height: 90vh;
  overflow-y: auto;

  .report-type-select {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 14px;
    background: #fff;
    cursor: pointer;

    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
  }

  .analysis-result {
    .result-section {
      margin-bottom: 24px;
      padding: 20px;
      background: #f8fafc;
      border-radius: 12px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .result-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #0f172a;
      margin-bottom: 16px;

      svg {
        color: #3b82f6;
      }

      &.warning {
        color: #f59e0b;

        svg {
          color: #f59e0b;
        }
      }
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 16px;

      .summary-item {
        text-align: center;
        padding: 12px;
        background: #fff;
        border-radius: 8px;

        .summary-label {
          display: block;
          font-size: 12px;
          color: #64748b;
          margin-bottom: 4px;
        }

        .summary-value {
          display: block;
          font-size: 14px;
          font-weight: 600;
          color: #0f172a;
        }
      }
    }

    .overall-assessment {
      font-size: 14px;
      line-height: 1.6;
      color: #475569;
      padding: 12px;
      background: #fff;
      border-radius: 8px;
      margin: 0;
    }

    .indicators-table {
      background: #fff;
      border-radius: 8px;
      overflow: hidden;

      .table-header {
        display: grid;
        grid-template-columns: 2fr 1.5fr 1.5fr 1fr;
        gap: 12px;
        padding: 12px 16px;
        background: #f1f5f9;
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
      }

      .table-row {
        display: grid;
        grid-template-columns: 2fr 1.5fr 1.5fr 1fr;
        gap: 12px;
        padding: 12px 16px;
        border-bottom: 1px solid #f1f5f9;
        font-size: 13px;
        align-items: center;

        &:last-child {
          border-bottom: none;
        }

        &.warning {
          background: #fffbeb;
        }

        &.abnormal {
          background: #fef2f2;
        }

        .indicator-name {
          font-weight: 500;
          color: #0f172a;
        }

        .indicator-value {
          color: #475569;
        }

        .indicator-range {
          color: #64748b;
          font-size: 12px;
        }

        .indicator-status {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
          text-align: center;

          &.normal {
            background: #dcfce7;
            color: #16a34a;
          }

          &.warning {
            background: #fef3c7;
            color: #d97706;
          }

          &.abnormal {
            background: #fee2e2;
            color: #dc2626;
          }
        }
      }
    }

    .abnormal-list {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .abnormal-item {
        padding: 16px;
        background: #fff;
        border-radius: 8px;
        border-left: 3px solid #f59e0b;

        &.high {
          border-left-color: #ef4444;
        }

        .abnormal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .abnormal-indicator {
          font-weight: 600;
          color: #0f172a;
        }

        .abnormal-severity {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;

          &.low {
            background: #fef3c7;
            color: #d97706;
          }

          &.medium {
            background: #ffedd5;
            color: #ea580c;
          }

          &.high {
            background: #fee2e2;
            color: #dc2626;
          }
        }

        .abnormal-desc {
          font-size: 13px;
          color: #475569;
          margin-bottom: 8px;
          line-height: 1.5;
        }

        .abnormal-recommendation {
          font-size: 13px;
          color: #3b82f6;
          margin: 0;
        }
      }
    }

    .suggestion-list {
      list-style: none;
      padding: 0;
      margin: 0;

      li {
        position: relative;
        padding: 10px 0 10px 24px;
        font-size: 14px;
        color: #475569;
        border-bottom: 1px solid #f1f5f9;

        &:last-child {
          border-bottom: none;
        }

        &::before {
          content: '•';
          position: absolute;
          left: 8px;
          color: #3b82f6;
          font-weight: bold;
        }
      }
    }

    .follow-up-content {
      background: #fff;
      padding: 16px;
      border-radius: 8px;

      .urgency-level {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 12px;

        &.low {
          background: #dcfce7;
          color: #16a34a;
        }

        &.medium {
          background: #fef3c7;
          color: #d97706;
        }

        &.high {
          background: #fee2e2;
          color: #dc2626;
        }
      }

      .follow-up-section {
        margin-bottom: 8px;
        font-size: 14px;

        &:last-child {
          margin-bottom: 0;
        }
      }

      .follow-up-label {
        color: #64748b;
        margin-right: 8px;
      }

      .follow-up-value {
        color: #0f172a;
        font-weight: 500;
      }
    }
  }
}

// 加载动画
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// 响应式
@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .stats-row {
    flex-direction: column;
    gap: 20px;
  }

  .stat-divider {
    width: 60px;
    height: 1px;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }

  .filter-group {
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .report-main {
    flex-wrap: wrap;
  }

  .report-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: 12px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .indicator-summary {
    flex-direction: column;
  }
}
</style>
