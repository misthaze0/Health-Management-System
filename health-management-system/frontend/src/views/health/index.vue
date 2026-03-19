<template>
  <div class="health-dashboard">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">HEALTH DASHBOARD</div>
        <h1 class="hero-title">健康数据看板</h1>
        <p class="hero-subtitle">Health Metrics & Activity Tracking</p>
        <div class="hero-desc">
          <p>实时监测身体核心指标，科学分析运动数据</p>
          <p>让健康管理更精准、更智能、更个性化</p>
        </div>
        <div class="hero-actions">
          <button class="btn-primary" @click="showUploadDialog = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            记录今日数据
          </button>
          <button class="btn-secondary" @click="showDataManager = true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            数据管理
          </button>

        </div>
      </div>
      <div class="hero-stats">
        <div class="stat-item">
          <span class="stat-value">{{ bodyMetrics.heartRate || '--' }}</span>
          <span class="stat-label">心率 BPM</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ bodyMetrics.spo2 || '--' }}</span>
          <span class="stat-label">血氧 %</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ formatNumber(exerciseData.steps) }}</span>
          <span class="stat-label">步数</span>
        </div>
      </div>
    </section>

    <!-- Body Metrics Section - 多维度分开管理 -->
    <section class="metrics-section">
      <div class="section-header">
        <span class="section-num">01</span>
        <h2 class="section-title">身体指标</h2>
        <p class="section-subtitle">Body Metrics</p>
      </div>
      
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载健康数据中...</p>
      </div>
      
      <div v-else-if="!hasData" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
        </div>
        <h3>暂无健康数据</h3>
        <p>点击上方"记录今日数据"按钮开始记录您的健康指标</p>
      </div>
      
      <div v-else class="metrics-dimensions">
        <!-- 维度1: 心血管指标 -->
        <div class="dimension-card cardiovascular">
          <div class="dimension-header">
            <div class="dimension-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </div>
            <div class="dimension-info">
              <h3 class="dimension-title">心血管指标</h3>
              <p class="dimension-subtitle">Cardiovascular Metrics</p>
            </div>
          </div>
          
          <div class="dimension-content">
            <!-- 左侧：主要指标和次要指标堆叠 -->
            <div class="metrics-left">
              <!-- 静息心率 -->
              <div class="metric-item primary">
                <div class="metric-item-header">
                  <span class="metric-name">静息心率</span>
                  <span class="metric-badge" :class="getStatusClass(bodyMetrics.heartRate, 'heartRate')">
                    {{ getStatusText(bodyMetrics.heartRate, 'heartRate') }}
                  </span>
                </div>
                <div class="metric-value-wrapper">
                  <span class="metric-number">{{ bodyMetrics.heartRate || '--' }}</span>
                  <span class="metric-unit">次/分</span>
                </div>
                <div class="metric-range-info">正常范围: 60-100 次/分</div>
                <div class="metric-trend">
                  <v-chart v-if="heartRateHistory.length > 0" :option="heartRateChartOption" autoresize />
                  <div v-else class="no-trend-data">暂无趋势数据</div>
                </div>
              </div>
              
              <!-- 次要指标堆叠 -->
              <div class="secondary-metrics-stack">
                <!-- 心率变异性 -->
                <div class="metric-item secondary">
                  <div class="metric-item-header">
                    <span class="metric-name">心率变异性 (HRV)</span>
                    <span class="metric-badge" :class="getStatusClass(bodyMetrics.hrv, 'hrv')">
                      {{ getStatusText(bodyMetrics.hrv, 'hrv') }}
                    </span>
                  </div>
                  <div class="metric-value-wrapper">
                    <span class="metric-number">{{ bodyMetrics.hrv || '--' }}</span>
                    <span class="metric-unit">ms</span>
                  </div>
                  <div class="metric-range-info">正常范围: 20-200 ms</div>
                </div>
                
                <!-- 夜间心率波动 -->
                <div class="metric-item secondary">
                  <div class="metric-item-header">
                    <span class="metric-name">夜间心率波动</span>
                    <span class="metric-badge normal">{{ bodyMetrics.heartFluctuation ? '平稳' : '--' }}</span>
                  </div>
                  <div class="metric-value-wrapper">
                    <span class="metric-number">
                      {{ bodyMetrics.heartFluctuation ? `${bodyMetrics.heartFluctuation.min}-${bodyMetrics.heartFluctuation.max}` : '--' }}
                    </span>
                    <span class="metric-unit">次/分</span>
                  </div>
                  <div class="metric-range-info">
                    {{ bodyMetrics.heartFluctuation ? `波动范围: ${bodyMetrics.heartFluctuation.max - bodyMetrics.heartFluctuation.min} 次/分` : '暂无数据' }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 右侧：健康解读 -->
            <div class="metrics-right" v-if="bodyMetrics.heartRate">
              <div class="metric-analysis">
                <div class="analysis-title">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                  健康解读
                </div>
                <div class="analysis-content">
                  <div class="analysis-section">
                    <h4 class="section-title">数据概况</h4>
                    <p class="section-text">{{ getHeartRateAnalysis.summary }}</p>
                    <p class="section-detail" v-if="getHeartRateAnalysis.details">{{ getHeartRateAnalysis.details }}</p>
                  </div>
                  <div class="analysis-section" v-if="getHeartRateAnalysis.science">
                    <h4 class="section-title">专业科普</h4>
                    <p class="section-text">{{ getHeartRateAnalysis.science }}</p>
                  </div>
                  <div class="analysis-section">
                    <h4 class="section-title">改善建议</h4>
                    <ul class="section-list">
                      <li v-for="(suggestion, idx) in getHeartRateAnalysis.suggestions" :key="idx">{{ suggestion }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 维度2: 呼吸与氧合 -->
        <div class="dimension-card respiratory">
          <div class="dimension-header">
            <div class="dimension-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <div class="dimension-info">
              <h3 class="dimension-title">呼吸与氧合</h3>
              <p class="dimension-subtitle">Respiratory & Oxygen</p>
            </div>
          </div>
          
          <div class="dimension-content">
            <!-- 左侧：主要指标和次要指标堆叠 -->
            <div class="metrics-left">
              <!-- 夜间血氧 -->
              <div class="metric-item primary">
                <div class="metric-item-header">
                  <span class="metric-name">夜间血氧饱和度</span>
                  <span class="metric-badge" :class="getStatusClass(bodyMetrics.spo2, 'spo2')">
                    {{ getStatusText(bodyMetrics.spo2, 'spo2') }}
                  </span>
                </div>
                <div class="metric-value-wrapper">
                  <span class="metric-number">{{ bodyMetrics.spo2 || '--' }}</span>
                  <span class="metric-unit">%</span>
                </div>
                <div class="metric-range-info">正常范围: 95-100%</div>
                <div class="metric-trend">
                  <v-chart v-if="spo2History.length > 0" :option="spo2ChartOption" autoresize />
                  <div v-else class="no-trend-data">暂无趋势数据</div>
                </div>
              </div>
              
              <!-- 次要指标堆叠 -->
              <div class="secondary-metrics-stack">
                <!-- 呼吸频率 -->
                <div class="metric-item secondary">
                  <div class="metric-item-header">
                    <span class="metric-name">呼吸频率</span>
                    <span class="metric-badge" :class="getStatusClass(bodyMetrics.respiration, 'respiration')">
                      {{ getStatusText(bodyMetrics.respiration, 'respiration') }}
                    </span>
                  </div>
                  <div class="metric-value-wrapper">
                    <span class="metric-number">{{ bodyMetrics.respiration || '--' }}</span>
                    <span class="metric-unit">次/分</span>
                  </div>
                  <div class="metric-range-info">正常范围: 12-20 次/分</div>
                </div>
              </div>
            </div>
            
            <!-- 右侧：健康解读 -->
            <div class="metrics-right" v-if="bodyMetrics.spo2">
              <div class="metric-analysis">
                <div class="analysis-title">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                  健康解读
                </div>
                <div class="analysis-content">
                  <div class="analysis-section">
                    <h4 class="section-title">数据概况</h4>
                    <p class="section-text">{{ getSpO2Analysis.summary }}</p>
                    <p class="section-detail" v-if="getSpO2Analysis.details">{{ getSpO2Analysis.details }}</p>
                  </div>
                  <div class="analysis-section" v-if="getSpO2Analysis.science">
                    <h4 class="section-title">专业科普</h4>
                    <p class="section-text">{{ getSpO2Analysis.science }}</p>
                  </div>
                  <div class="analysis-section">
                    <h4 class="section-title">改善建议</h4>
                    <ul class="section-list">
                      <li v-for="(suggestion, idx) in getSpO2Analysis.suggestions" :key="idx">{{ suggestion }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 维度3: 睡眠质量 -->
        <div class="dimension-card sleep">
          <div class="dimension-header">
            <div class="dimension-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            </div>
            <div class="dimension-info">
              <h3 class="dimension-title">睡眠质量</h3>
              <p class="dimension-subtitle">Sleep Quality</p>
            </div>
          </div>
          
          <div class="dimension-content">
            <!-- 左侧：主要指标和次要指标堆叠 -->
            <div class="metrics-left">
              <!-- 睡眠效率 -->
              <div class="metric-item primary">
                <div class="metric-item-header">
                  <span class="metric-name">睡眠效率</span>
                  <span class="metric-badge" :class="getStatusClass(bodyMetrics.sleepEfficiency, 'sleepEfficiency')">
                    {{ getStatusText(bodyMetrics.sleepEfficiency, 'sleepEfficiency') }}
                  </span>
                </div>
                <div class="metric-value-wrapper">
                  <span class="metric-number">{{ bodyMetrics.sleepEfficiency || '--' }}</span>
                  <span class="metric-unit">%</span>
                </div>
                <div class="metric-range-info">正常范围: 85-95%</div>
                <div class="metric-trend">
                  <v-chart v-if="sleepHistory.length > 0" :option="sleepChartOption" autoresize />
                  <div v-else class="no-trend-data">暂无趋势数据</div>
                </div>
              </div>
              
              <!-- 次要指标堆叠 -->
              <div class="secondary-metrics-stack">
                <!-- 深睡占比 -->
                <div class="metric-item secondary">
                  <div class="metric-item-header">
                    <span class="metric-name">深睡占比</span>
                    <span class="metric-badge" :class="getStatusClass(bodyMetrics.deepSleep, 'deepSleep')">
                      {{ getStatusText(bodyMetrics.deepSleep, 'deepSleep') }}
                    </span>
                  </div>
                  <div class="metric-value-wrapper">
                    <span class="metric-number">{{ bodyMetrics.deepSleep || '--' }}</span>
                    <span class="metric-unit">%</span>
                  </div>
                  <div class="metric-range-info">正常范围: 15-25%</div>
                </div>
              </div>
            </div>
            
            <!-- 右侧：健康解读 -->
            <div class="metrics-right" v-if="bodyMetrics.sleepEfficiency">
              <div class="metric-analysis">
                <div class="analysis-title">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                  健康解读
                </div>
                <div class="analysis-content">
                  <div class="analysis-section">
                    <h4 class="section-title">数据概况</h4>
                    <p class="section-text">{{ getSleepAnalysis.summary }}</p>
                    <p class="section-detail" v-if="getSleepAnalysis.details">{{ getSleepAnalysis.details }}</p>
                  </div>
                  <div class="analysis-section" v-if="getSleepAnalysis.science">
                    <h4 class="section-title">专业科普</h4>
                    <p class="section-text">{{ getSleepAnalysis.science }}</p>
                  </div>
                  <div class="analysis-section">
                    <h4 class="section-title">改善建议</h4>
                    <ul class="section-list">
                      <li v-for="(suggestion, idx) in getSleepAnalysis.suggestions" :key="idx">{{ suggestion }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Exercise Section -->
    <section class="exercise-section">
      <div class="section-header light">
        <span class="section-num">02</span>
        <h2 class="section-title">运动数据</h2>
        <p class="section-subtitle">Activity Tracking</p>
      </div>

      <!-- Exercise Overview -->
      <div class="exercise-overview">
        <div class="exercise-stat-card">
          <div class="stat-icon steps">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 4v2.5M13 17v2.5M13 10.5v2.5M4 10.5h2.5M17 10.5h2.5M10.5 10.5h2.5"/>
              <circle cx="12" cy="12" r="9"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-num">{{ formatNumber(exerciseData.steps) }}</span>
            <span class="stat-name">步数</span>
            <div class="stat-progress">
              <div class="progress-bar" :style="{ width: Math.min((exerciseData.steps / 10000) * 100, 100) + '%' }"></div>
            </div>
            <span class="stat-target">目标: 10,000</span>
          </div>
        </div>

        <div class="exercise-stat-card">
          <div class="stat-icon calories">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-num">{{ exerciseData.calories }}</span>
            <span class="stat-name">卡路里 (千卡)</span>
            <div class="stat-progress">
              <div class="progress-bar" :style="{ width: Math.min((exerciseData.calories / 500) * 100, 100) + '%' }"></div>
            </div>
            <span class="stat-target">目标: 500</span>
          </div>
        </div>

        <div class="exercise-stat-card">
          <div class="stat-icon duration">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-num">{{ exerciseData.duration }}</span>
            <span class="stat-name">运动时长 (分钟)</span>
            <div class="stat-progress">
              <div class="progress-bar" :style="{ width: Math.min((exerciseData.duration / 60) * 100, 100) + '%' }"></div>
            </div>
            <span class="stat-target">目标: 60</span>
          </div>
        </div>
      </div>

      <!-- Exercise Chart -->
      <div class="exercise-chart-wrapper">
        <div class="chart-controls">
          <h3 class="chart-title">运动趋势</h3>
          <div class="view-toggle">
            <button 
              v-for="view in viewOptions" 
              :key="view.value"
              :class="['toggle-btn', { active: exerciseViewType === view.value }]"
              @click="exerciseViewType = view.value"
            >
              {{ view.label }}
            </button>
          </div>
        </div>
        <div class="chart-container">
          <v-chart v-if="exerciseHistory.length > 0" :option="exerciseChartOption" autoresize />
          <div v-else class="no-chart-data-large">暂无运动数据，请记录您的运动数据</div>
        </div>
      </div>
    </section>

    <!-- Upload Dialog -->
    <div v-if="showUploadDialog" class="dialog-overlay" @click.self="showUploadDialog = false">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>记录今日健康数据</h3>
          <button class="dialog-close" @click="showUploadDialog = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-section">
            <h4>身体指标</h4>
            <div class="form-grid">
              <div class="form-item">
                <label>静息心率 (次/分)</label>
                <input v-model.number="uploadForm.heartRate" type="number" placeholder="60-100" min="40" max="200">
              </div>
              <div class="form-item">
                <label>夜间血氧 (%)</label>
                <input v-model.number="uploadForm.spo2" type="number" placeholder="95-100" min="80" max="100">
              </div>
              <div class="form-item">
                <label>心率变异性 (ms)</label>
                <input v-model.number="uploadForm.hrv" type="number" placeholder="20-200" min="10" max="300">
              </div>
              <div class="form-item">
                <label>睡眠效率 (%)</label>
                <input v-model.number="uploadForm.sleepEfficiency" type="number" placeholder="85-95" min="50" max="100">
              </div>
              <div class="form-item">
                <label>深睡占比 (%)</label>
                <input v-model.number="uploadForm.deepSleep" type="number" placeholder="15-25" min="0" max="50">
              </div>
              <div class="form-item">
                <label>呼吸频率 (次/分)</label>
                <input v-model.number="uploadForm.respiration" type="number" placeholder="12-20" min="8" max="30">
              </div>
              <div class="form-item">
                <label>夜间心率最低 (次/分)</label>
                <input v-model.number="uploadForm.heartMin" type="number" placeholder="50-70" min="40" max="100">
              </div>
              <div class="form-item">
                <label>夜间心率最高 (次/分)</label>
                <input v-model.number="uploadForm.heartMax" type="number" placeholder="80-100" min="60" max="150">
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <h4>运动数据</h4>
            <div class="form-grid">
              <div class="form-item">
                <label>步数</label>
                <input v-model.number="uploadForm.steps" type="number" placeholder="0-30000" min="0" max="50000">
              </div>
              <div class="form-item">
                <label>卡路里 (千卡)</label>
                <input v-model.number="uploadForm.calories" type="number" placeholder="0-1000" min="0" max="2000">
              </div>
              <div class="form-item">
                <label>运动时长 (分钟)</label>
                <input v-model.number="uploadForm.duration" type="number" placeholder="0-180" min="0" max="300">
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <h4>记录日期</h4>
            <div class="form-item">
              <input v-model="uploadForm.recordDate" type="date" :max="today">
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showUploadDialog = false">取消</button>
          <button class="btn-submit" :disabled="uploading" @click="submitData">
            {{ uploading ? '保存中...' : '保存数据' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Health Analysis Card - 健康数据解读卡片 -->
    <div v-if="showAnalysisCard && currentAnalysis" class="analysis-overlay" @click.self="showAnalysisCard = false">
      <div class="analysis-card">
        <div class="analysis-header">
          <div class="analysis-title-group">
            <h3>健康数据解读</h3>
            <span class="analysis-date">{{ selectedDate }}</span>
          </div>
          <button class="analysis-close" @click="showAnalysisCard = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="analysis-content">
          <!-- 综合评分 -->
          <div class="score-section">
            <div class="score-circle" :class="currentAnalysis.healthScore.status">
              <div class="score-value">{{ currentAnalysis.healthScore.score }}</div>
              <div class="score-label">健康评分</div>
            </div>
            <div class="score-factors">
              <div v-for="factor in currentAnalysis.healthScore.factors" :key="factor.name" class="factor-item">
                <span class="factor-name">{{ factor.name }}</span>
                <div class="factor-bar">
                  <div class="factor-fill" :style="{ width: factor.score + '%', background: getScoreColor(factor.score) }"></div>
                </div>
                <span class="factor-score">{{ factor.score }}</span>
              </div>
            </div>
          </div>

          <!-- 指标分析列表 -->
          <div class="analysis-list">
            <template v-for="(analysis, key) in currentAnalysis.analyses" :key="key">
              <div v-if="analysis.title !== '暂无数据'" 
                   class="analysis-item" :class="analysis.status">
                <div class="item-header">
                  <div class="item-icon" :class="key">
                    <svg v-if="key === 'heartRate'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                    </svg>
                    <svg v-else-if="key === 'spo2'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"/>
                      <path d="M12 2v20M2 12h20"/>
                    </svg>
                    <svg v-else-if="key === 'hrv'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                    </svg>
                    <svg v-else-if="key === 'sleep'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
                      <path d="M12 6v6l4 2"/>
                    </svg>
                  </div>
                  <div class="item-title-group">
                    <h4>{{ analysis.title }}</h4>
                    <span class="item-status" :class="analysis.status">{{ getStatusLabel(analysis.status) }}</span>
                  </div>
                </div>
                <p class="item-summary">{{ analysis.summary }}</p>
                <div v-if="analysis.details && analysis.details.length > 0" class="item-details">
                  <div v-for="(detail, idx) in analysis.details" :key="idx" class="detail-row">
                    {{ detail }}
                  </div>
                </div>
                <div v-if="analysis.suggestions && analysis.suggestions.length > 0" class="item-suggestions">
                  <h5>改善建议</h5>
                  <ul>
                    <li v-for="(suggestion, idx) in analysis.suggestions" :key="idx">{{ suggestion }}</li>
                  </ul>
                </div>
              </div>
            </template>
          </div>

          <!-- 综合建议 -->
          <div class="overall-suggestions">
            <h4>综合健康建议</h4>
            <ul>
              <li v-for="(suggestion, idx) in currentAnalysis.overallSuggestions" :key="idx">{{ suggestion }}</li>
            </ul>
          </div>
        </div>

        <div class="analysis-footer">
          <button class="btn-close-analysis" @click="showAnalysisCard = false">关闭</button>
          <button class="btn-export" @click="exportAnalysis">导出报告</button>
        </div>
      </div>
    </div>

    <!-- 数据管理对话框 -->
    <div v-if="showDataManager" class="data-manager-overlay" @click.self="showDataManager = false">
      <div class="data-manager-dialog">
        <div class="dialog-header">
          <h3>数据管理</h3>
          <button class="btn-close" @click="showDataManager = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="dialog-body">
          <!-- 操作栏 -->
          <div class="manager-toolbar">
            <div class="date-range-picker">
              <span>日期范围：</span>
              <input type="date" v-model="dateRange[0]" @change="loadAllRecords" />
              <span>至</span>
              <input type="date" v-model="dateRange[1]" @change="loadAllRecords" />
            </div>
            <div class="toolbar-actions">
              <button class="btn-batch-delete" @click="batchDeleteRecords" :disabled="selectedRecords.length === 0">
                批量删除({{ selectedRecords.length }})
              </button>
              <button class="btn-range-delete" @click="deleteByDateRange" :disabled="!dateRange[0] || !dateRange[1]">
                删除选中日期范围
              </button>
            </div>
          </div>

          <!-- 数据列表 -->
          <div class="records-table-wrapper">
            <table class="records-table">
              <thead>
                <tr>
                  <th class="col-checkbox">
                    <input type="checkbox" :checked="selectedRecords.length === allRecords.length && allRecords.length > 0" @change="toggleSelectAll" />
                  </th>
                  <th class="col-date">日期</th>
                  <th class="col-type">指标类型</th>
                  <th class="col-value">数值</th>
                  <th class="col-notes">备注</th>
                  <th class="col-actions">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="dataManagerLoading">
                  <td colspan="6" class="loading-cell">
                    <div class="loading-spinner"></div>
                    <span>加载中...</span>
                  </td>
                </tr>
                <tr v-else-if="allRecords.length === 0">
                  <td colspan="6" class="empty-cell">
                    <div class="empty-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M9 11l3 3L22 4"/>
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                      </svg>
                    </div>
                    <p>暂无数据记录</p>
                  </td>
                </tr>
                <tr v-for="record in allRecords" :key="record.id" :class="{ selected: selectedRecords.find(r => r.id === record.id) }">
                  <td class="col-checkbox">
                    <input type="checkbox" :checked="selectedRecords.find(r => r.id === record.id)" @change="toggleRecordSelection(record)" />
                  </td>
                  <td class="col-date">{{ record.recordDate }}</td>
                  <td class="col-type">
                    <span class="metric-tag" :class="record.metricType">{{ getMetricName(record.metricType) }}</span>
                  </td>
                  <td class="col-value">{{ record.metricValue }}</td>
                  <td class="col-notes">{{ record.notes || '-' }}</td>
                  <td class="col-actions">
                    <button class="btn-delete" @click="deleteSingleRecord(record)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 分页 -->
          <div class="pagination" v-if="totalRecords > pageSize">
            <button :disabled="currentPage === 1" @click="currentPage--; loadAllRecords()">上一页</button>
            <span>第 {{ currentPage }} 页，共 {{ Math.ceil(totalRecords / pageSize) }} 页</span>
            <button :disabled="currentPage >= Math.ceil(totalRecords / pageSize)" @click="currentPage++; loadAllRecords()">下一页</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, GraphicComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'
import { 
  getLatestMetrics, 
  getHealthRecords, 
  addHealthRecord,
  deleteHealthRecord,
  batchDeleteHealthRecords,
  deleteHealthRecordsByDateRange,
  MetricTypes 
} from '@/api/health'
import { analyzeHealthData, analyzeDailyData } from '@/utils/healthAnalysis'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent, GraphicComponent])

// 响应式数据
const loading = ref(false)
const uploading = ref(false)
const showUploadDialog = ref(false)
const hasData = ref(false)

// 健康解读卡片数据
const showAnalysisCard = ref(false)
const currentAnalysis = ref(null)
const selectedDate = ref('')

// 数据管理
const showDataManager = ref(false)
const dataManagerLoading = ref(false)
const allRecords = ref([])
const selectedRecords = ref([])
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)

// 身体指标数据
const bodyMetrics = reactive({
  heartRate: null,
  spo2: null,
  hrv: null,
  sleepEfficiency: null,
  deepSleep: null,
  respiration: null,
  heartFluctuation: null
})

// 运动数据
const exerciseData = reactive({
  steps: 0,
  calories: 0,
  duration: 0
})

// 历史数据
const heartRateHistory = ref([])
const spo2History = ref([])
const hrvHistory = ref([])
const sleepHistory = ref([])
const respirationHistory = ref([])
const heartFluctuationHistory = ref([])
const exerciseHistory = ref([])

// 视图控制
const exerciseViewType = ref('week')
const viewOptions = [
  { value: 'day', label: '日' },
  { value: 'week', label: '周' },
  { value: 'month', label: '月' }
]

// 上传表单
const today = dayjs().format('YYYY-MM-DD')
const uploadForm = reactive({
  heartRate: '',
  spo2: '',
  hrv: '',
  sleepEfficiency: '',
  deepSleep: '',
  respiration: '',
  heartMin: '',
  heartMax: '',
  steps: '',
  calories: '',
  duration: '',
  recordDate: today
})

// 图表配置 - 科技感设计
const createTechChartOption = (data, color, name) => {
  const dates = data.map((_, i) => dayjs().subtract(data.length - 1 - i, 'day').format('MM-DD'))
  const values = data
  const avg = values.length > 0 ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1) : '--'
  const latest = values.length > 0 ? values[values.length - 1] : '--'
  
  return {
    backgroundColor: 'transparent',
    grid: {
      top: 40,
      left: 16,
      right: 16,
      bottom: 24,
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: color,
      borderWidth: 1,
      padding: [12, 16],
      textStyle: {
        color: '#fff',
        fontSize: 13
      },
      formatter: function(params) {
        const data = params[0]
        return `<div style="font-weight:600;margin-bottom:4px">${data.name}</div>
                <div style="display:flex;align-items:center;gap:8px">
                  <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color}"></span>
                  <span>${name}: <strong>${data.value}</strong></span>
                </div>`
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: 'rgba(0,0,0,0.08)' }
      },
      axisTick: { show: false },
      axisLabel: {
        color: '#999',
        fontSize: 10,
        interval: Math.floor(dates.length / 4)
      }
    },
    yAxis: {
      type: 'value',
      splitLine: {
        lineStyle: {
          color: 'rgba(0,0,0,0.04)',
          type: 'dashed'
        }
      },
      axisLabel: { show: false }
    },
    series: [{
      name: name,
      type: 'line',
      data: values,
      smooth: 0.4,
      symbol: 'circle',
      symbolSize: 6,
      showSymbol: false,
      lineStyle: {
        color: color,
        width: 3,
        shadowColor: color + '80',
        shadowBlur: 10,
        shadowOffsetY: 4
      },
      itemStyle: {
        color: color,
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '40' },
            { offset: 0.5, color: color + '20' },
            { offset: 1, color: color + '05' }
          ]
        }
      },
      emphasis: {
        scale: true,
        itemStyle: {
          shadowBlur: 15,
          shadowColor: color
        }
      }
    }],
    // 添加统计信息
    graphic: [
      {
        type: 'group',
        left: 16,
        top: 8,
        children: [
          {
            type: 'text',
            style: {
              text: `最新: ${latest}`,
              fill: '#1a1a2e',
              fontSize: 13,
              fontWeight: 'bold'
            }
          },
          {
            type: 'text',
            left: 80,
            style: {
              text: `平均: ${avg}`,
              fill: '#999',
              fontSize: 11
            }
          }
        ]
      }
    ]
  }
}

// 各指标图表配置
const heartRateChartOption = computed(() => createTechChartOption(heartRateHistory.value, '#ff6b6b', '心率'))
const spo2ChartOption = computed(() => createTechChartOption(spo2History.value, '#1890ff', '血氧'))
const hrvChartOption = computed(() => createTechChartOption(hrvHistory.value, '#722ed1', 'HRV'))
const sleepChartOption = computed(() => createTechChartOption(sleepHistory.value, '#722ed1', '睡眠效率'))
const respirationChartOption = computed(() => createTechChartOption(respirationHistory.value, '#1890ff', '呼吸'))
const heartFluctuationChartOption = computed(() => createTechChartOption(heartFluctuationHistory.value, '#ff6b6b', '波动'))

// 运动数据图表 - 科技感设计
const exerciseChartOption = computed(() => {
  const count = exerciseViewType.value === 'day' ? 24 : exerciseViewType.value === 'week' ? 7 : 30
  const labels = Array.from({ length: count }, (_, i) => {
    const d = dayjs().subtract(count - 1 - i, exerciseViewType.value === 'day' ? 'hour' : 'day')
    return exerciseViewType.value === 'day' ? d.format('HH:00') : d.format('MM-DD')
  })

  const stepsData = exerciseHistory.value.map(r => r.steps || 0)
  const caloriesData = exerciseHistory.value.map(r => r.calories || 0)
  const durationData = exerciseHistory.value.map(r => r.duration || 0)
  
  // 计算统计数据
  const totalSteps = stepsData.reduce((a, b) => a + b, 0)
  const totalCalories = caloriesData.reduce((a, b) => a + b, 0)
  const totalDuration = durationData.reduce((a, b) => a + b, 0)
  const avgSteps = stepsData.length > 0 ? Math.round(totalSteps / stepsData.length) : 0

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(56, 189, 248, 0.5)',
      borderWidth: 1,
      padding: [16, 20],
      textStyle: { 
        color: '#fff',
        fontSize: 13
      },
      formatter: function(params) {
        let html = `<div style="font-weight:600;margin-bottom:8px;font-size:14px">${params[0].name}</div>`
        params.forEach(p => {
          const color = p.seriesName === '步数' ? '#38bdf8' : p.seriesName === '卡路里' ? '#f87171' : '#34d399'
          const unit = p.seriesName === '步数' ? '步' : p.seriesName === '卡路里' ? '千卡' : '分钟'
          html += `<div style="display:flex;align-items:center;gap:8px;margin:4px 0">
            <span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${color};box-shadow:0 0 8px ${color}"></span>
            <span style="flex:1">${p.seriesName}:</span>
            <span style="font-weight:600;font-size:15px">${p.value.toLocaleString()}${unit}</span>
          </div>`
        })
        return html
      }
    },
    legend: { 
      data: ['步数', '卡路里'],
      textStyle: { 
        color: 'rgba(255, 255, 255, 0.7)',
        fontSize: 12
      },
      bottom: 8,
      itemGap: 24,
      itemWidth: 14,
      itemHeight: 14
    },
    grid: { 
      left: 16, 
      right: 16, 
      top: 60, 
      bottom: 48, 
      containLabel: true 
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: { 
        lineStyle: { 
          color: 'rgba(255, 255, 255, 0.1)',
          width: 1
        } 
      },
      axisLabel: { 
        color: 'rgba(255, 255, 255, 0.5)', 
        fontSize: 11,
        interval: Math.floor(labels.length / 6)
      },
      axisTick: { 
        show: true,
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '步数',
        position: 'left',
        nameTextStyle: {
          color: 'rgba(255, 255, 255, 0.5)',
          padding: [0, 0, 0, -30]
        },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { 
          lineStyle: { 
            color: 'rgba(255, 255, 255, 0.05)', 
            type: 'dashed' 
          } 
        },
        axisLabel: { 
          color: 'rgba(255, 255, 255, 0.4)', 
          fontSize: 11,
          formatter: (value) => value >= 1000 ? (value / 1000).toFixed(1) + 'k' : value
        }
      },
      {
        type: 'value',
        name: '卡路里',
        position: 'right',
        nameTextStyle: {
          color: 'rgba(255, 255, 255, 0.5)',
          padding: [0, -30, 0, 0]
        },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { 
          color: 'rgba(255, 255, 255, 0.4)', 
          fontSize: 11 
        }
      }
    ],
    series: [
      {
        name: '步数',
        type: 'bar',
        data: stepsData.length > 0 ? stepsData : Array(count).fill(0),
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#38bdf8' },
              { offset: 1, color: '#0ea5e9' }
            ]
          },
          borderRadius: [4, 4, 0, 0],
          shadowColor: 'rgba(56, 189, 248, 0.4)',
          shadowBlur: 8
        },
        barWidth: '35%',
        emphasis: {
          itemStyle: {
            shadowColor: 'rgba(56, 189, 248, 0.8)',
            shadowBlur: 12
          }
        }
      },
      {
        name: '卡路里',
        type: 'line',
        yAxisIndex: 1,
        data: caloriesData.length > 0 ? caloriesData : Array(count).fill(0),
        smooth: 0.3,
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
        lineStyle: { 
          color: '#f87171', 
          width: 3,
          shadowColor: 'rgba(248, 113, 113, 0.5)',
          shadowBlur: 10
        },
        itemStyle: {
          color: '#f87171',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(248, 113, 113, 0.3)' },
              { offset: 1, color: 'rgba(248, 113, 113, 0.02)' }
            ]
          }
        }
      }
    ],
    // 添加统计信息
    graphic: [
      {
        type: 'group',
        left: 16,
        top: 12,
        children: [
          {
            type: 'text',
            style: {
              text: `总步数: ${totalSteps.toLocaleString()}`,
              fill: '#38bdf8',
              fontSize: 13,
              fontWeight: 'bold'
            }
          },
          {
            type: 'text',
            left: 120,
            style: {
              text: `平均: ${avgSteps.toLocaleString()}/天`,
              fill: 'rgba(255, 255, 255, 0.6)',
              fontSize: 11
            }
          },
          {
            type: 'text',
            left: 240,
            style: {
              text: `消耗: ${totalCalories.toLocaleString()}千卡`,
              fill: '#f87171',
              fontSize: 13,
              fontWeight: 'bold'
            }
          }
        ]
      }
    ]
  }
})

// 计算属性 - 健康分析
const getHeartRateAnalysis = computed(() => {
  const value = bodyMetrics.heartRate
  if (!value) return { summary: '', suggestions: [] }
  
  if (value >= 60 && value <= 100) {
    return {
      summary: `您的静息心率为 ${value} 次/分，处于正常范围（60-100次/分）内，表明心脏功能正常。`,
      suggestions: ['保持规律的有氧运动', '维持良好的睡眠质量', '定期监测心率变化趋势']
    }
  } else if (value < 60) {
    return {
      summary: `您的静息心率为 ${value} 次/分，低于正常范围。如果您是运动员或经常锻炼，这可能是正常的。`,
      suggestions: ['如无运动习惯，建议咨询医生', '检查是否服用影响心率的药物', '避免过度节食或营养不良']
    }
  } else {
    return {
      summary: `您的静息心率为 ${value} 次/分，高于正常范围。可能提示身体处于应激状态。`,
      suggestions: ['减少咖啡因和酒精摄入', '练习深呼吸和冥想缓解压力', '保证充足睡眠（7-9小时）']
    }
  }
})

const getSpO2Analysis = computed(() => {
  const value = bodyMetrics.spo2
  if (!value) return { summary: '', suggestions: [] }
  
  if (value >= 95) {
    return {
      summary: `您的血氧饱和度为 ${value}%，处于理想范围（95-100%），表明呼吸系统功能良好。`,
      suggestions: ['继续保持良好的生活习惯', '适当进行有氧运动增强肺功能', '避免长时间处于密闭空间']
    }
  } else if (value >= 90) {
    return {
      summary: `您的血氧饱和度为 ${value}%，略低于理想范围。建议关注并改善。`,
      suggestions: ['保持室内通风，增加空气流通', '侧卧睡姿有助于改善呼吸', '避免睡前饮酒']
    }
  } else {
    return {
      summary: `您的血氧饱和度为 ${value}%，明显低于正常范围。建议及时就医检查。`,
      suggestions: ['建议就医检查心肺功能', '排查肺部疾病、心脏问题', '避免剧烈运动']
    }
  }
})

const getSleepAnalysis = computed(() => {
  const efficiency = bodyMetrics.sleepEfficiency
  const deepSleep = bodyMetrics.deepSleep
  if (!efficiency) return { summary: '', suggestions: [] }
  
  if (efficiency >= 85) {
    return {
      summary: `您的睡眠效率为 ${efficiency}%，${deepSleep ? `深睡占比 ${deepSleep}%，` : ''}各项指标均处于理想范围。`,
      suggestions: ['继续保持规律的作息时间', '睡前1小时避免使用电子设备', '保持卧室温度在18-22℃']
    }
  } else {
    return {
      summary: `您的睡眠效率为 ${efficiency}%，低于理想范围。可能存在入睡困难、夜间觉醒等问题。`,
      suggestions: ['建立固定的睡前仪式', '避免午后摄入咖啡因', '睡前进行放松活动如阅读']
    }
  }
})

// 方法
const getStatusClass = (value, type) => {
  if (!value) return 'normal'
  const ranges = {
    heartRate: { min: 60, max: 100 },
    spo2: { min: 95, max: 100 },
    hrv: { min: 20, max: 200 },
    sleepEfficiency: { min: 85, max: 95 },
    respiration: { min: 12, max: 20 }
  }
  const range = ranges[type]
  if (!range) return 'normal'
  if (value >= range.min && value <= range.max) return 'normal'
  if (value < range.min * 0.9 || value > range.max * 1.1) return 'warning'
  return 'attention'
}

const getStatusText = (value, type) => {
  if (!value) return '--'
  const cls = getStatusClass(value, type)
  const texts = { normal: '正常', attention: '关注', warning: '异常' }
  return texts[cls]
}

// 获取状态文本（用于解读卡片）
const getStatusLabel = (status) => {
  const labels = { normal: '正常', warning: '关注', abnormal: '异常', unknown: '未知' }
  return labels[status] || '未知'
}

// 获取评分颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#10b981'
  if (score >= 80) return '#3b82f6'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

const formatNumber = (num) => {
  if (!num && num !== 0) return '--'
  return num.toLocaleString('zh-CN')
}

// 获取最新数据
const fetchLatestData = async () => {
  try {
    loading.value = true
    const records = await getLatestMetrics()
    console.log('获取到最新数据:', records)
    
    if (records && records.length > 0) {
      hasData.value = true
      
      // 更新身体指标
      records.forEach(record => {
        // 后端返回的是下划线命名，转换为驼峰命名
        const metricType = record.metricType || record.metric_type
        const metricValue = record.metricValue !== undefined ? record.metricValue : record.metric_value
        const notes = record.notes
        
        switch (metricType) {
          case MetricTypes.RESTING_HEART_RATE:
            bodyMetrics.heartRate = metricValue
            break
          case MetricTypes.SPO2:
            bodyMetrics.spo2 = metricValue
            break
          case MetricTypes.HRV:
            bodyMetrics.hrv = metricValue
            break
          case MetricTypes.SLEEP_EFFICIENCY:
            bodyMetrics.sleepEfficiency = metricValue
            break
          case MetricTypes.DEEP_SLEEP:
            bodyMetrics.deepSleep = metricValue
            break
          case MetricTypes.RESPIRATORY_RATE:
            bodyMetrics.respiration = metricValue
            break
          case MetricTypes.NIGHT_HR_VARIABILITY:
            // 解析心率波动范围 "min-max"
            const notesStr = notes || ''
            const parts = notesStr.split('-') || []
            if (parts.length === 2) {
              bodyMetrics.heartFluctuation = {
                min: parseInt(parts[0]),
                max: parseInt(parts[1])
              }
            }
            break
          case MetricTypes.STEPS:
            exerciseData.steps = metricValue
            break
          case MetricTypes.CALORIES:
            exerciseData.calories = metricValue
            break
          case MetricTypes.EXERCISE_DURATION:
            exerciseData.duration = metricValue
            break
        }
      })
    } else {
      hasData.value = false
    }
  } catch (error) {
    console.error('获取最新数据失败:', error)
    ElMessage.error('获取数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 获取历史数据
const fetchHistoryData = async () => {
  try {
    const endDate = dayjs().format('YYYY-MM-DD')
    const startDate = dayjs().subtract(30, 'day').format('YYYY-MM-DD')
    
    const records = await getHealthRecords({ startDate, endDate })
    console.log('获取到历史数据:', records)
    
    if (records && records.length > 0) {
      // 按指标类型分组
      const grouped = {}
      records.forEach(record => {
        // 后端返回的是下划线命名，转换为驼峰命名
        const metricType = record.metricType || record.metric_type
        if (!grouped[metricType]) {
          grouped[metricType] = []
        }
        grouped[metricType].push(record)
      })
      
      // 更新历史数据
      heartRateHistory.value = (grouped[MetricTypes.RESTING_HEART_RATE] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
        .map(r => r.metricValue !== undefined ? r.metricValue : r.metric_value)
      
      spo2History.value = (grouped[MetricTypes.SPO2] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
        .map(r => r.metricValue !== undefined ? r.metricValue : r.metric_value)
      
      hrvHistory.value = (grouped[MetricTypes.HRV] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
        .map(r => r.metricValue !== undefined ? r.metricValue : r.metric_value)
      
      sleepHistory.value = (grouped[MetricTypes.SLEEP_EFFICIENCY] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
        .map(r => r.metricValue !== undefined ? r.metricValue : r.metric_value)
      
      respirationHistory.value = (grouped[MetricTypes.RESPIRATORY_RATE] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
        .map(r => r.metricValue !== undefined ? r.metricValue : r.metric_value)
      
      // 运动数据
      const stepsRecords = (grouped[MetricTypes.STEPS] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
      const caloriesRecords = (grouped[MetricTypes.CALORIES] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
      const durationRecords = (grouped[MetricTypes.EXERCISE_DURATION] || [])
        .sort((a, b) => new Date(a.recordDate || a.record_date) - new Date(b.recordDate || b.record_date))
      
      exerciseHistory.value = stepsRecords.map((s, i) => ({
        date: s.recordDate || s.record_date,
        steps: s.metricValue !== undefined ? s.metricValue : s.metric_value,
        calories: caloriesRecords[i] ? (caloriesRecords[i].metricValue !== undefined ? caloriesRecords[i].metricValue : caloriesRecords[i].metric_value) : 0,
        duration: durationRecords[i] ? (durationRecords[i].metricValue !== undefined ? durationRecords[i].metricValue : durationRecords[i].metric_value) : 0
      }))
    }
  } catch (error) {
    console.error('获取历史数据失败:', error)
  }
}

// 提交数据
const submitData = async () => {
  try {
    uploading.value = true
    
    const records = []
    
    // 身体指标
    if (uploadForm.heartRate) {
      records.push({
        metricType: MetricTypes.RESTING_HEART_RATE,
        metricValue: uploadForm.heartRate,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.spo2) {
      records.push({
        metricType: MetricTypes.SPO2,
        metricValue: uploadForm.spo2,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.hrv) {
      records.push({
        metricType: MetricTypes.HRV,
        metricValue: uploadForm.hrv,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.sleepEfficiency) {
      records.push({
        metricType: MetricTypes.SLEEP_EFFICIENCY,
        metricValue: uploadForm.sleepEfficiency,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.deepSleep) {
      records.push({
        metricType: MetricTypes.DEEP_SLEEP,
        metricValue: uploadForm.deepSleep,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.respiration) {
      records.push({
        metricType: MetricTypes.RESPIRATORY_RATE,
        metricValue: uploadForm.respiration,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.heartMin && uploadForm.heartMax) {
      records.push({
        metricType: MetricTypes.NIGHT_HR_VARIABILITY,
        metricValue: parseInt(uploadForm.heartMax) - parseInt(uploadForm.heartMin),
        recordDate: uploadForm.recordDate,
        notes: `${uploadForm.heartMin}-${uploadForm.heartMax}`
      })
    }
    
    // 运动数据
    if (uploadForm.steps) {
      records.push({
        metricType: MetricTypes.STEPS,
        metricValue: uploadForm.steps,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.calories) {
      records.push({
        metricType: MetricTypes.CALORIES,
        metricValue: uploadForm.calories,
        recordDate: uploadForm.recordDate
      })
    }
    if (uploadForm.duration) {
      records.push({
        metricType: MetricTypes.EXERCISE_DURATION,
        metricValue: uploadForm.duration,
        recordDate: uploadForm.recordDate
      })
    }
    
    if (records.length === 0) {
      ElMessage.warning('请至少填写一项数据')
      return
    }
    
    // 批量提交
    for (const record of records) {
      await addHealthRecord(record)
    }
    
    ElMessage.success('数据保存成功！')
    showUploadDialog.value = false
    
    // 刷新数据
    await refreshData()
    
    // 重置表单
    Object.keys(uploadForm).forEach(key => {
      uploadForm[key] = key === 'recordDate' ? today : ''
    })
    
  } catch (error) {
    console.error('保存数据失败:', error)
    ElMessage.error('保存失败，请稍后重试')
  } finally {
    uploading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([fetchLatestData(), fetchHistoryData()])
}

// 打开数据管理器
const openDataManager = async () => {
  showDataManager.value = true
  await loadAllRecords()
}

// 加载所有记录
const loadAllRecords = async () => {
  try {
    dataManagerLoading.value = true
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      startDate: dateRange.value?.[0],
      endDate: dateRange.value?.[1]
    }
    const res = await getHealthRecords(params)
    allRecords.value = res.records || []
    totalRecords.value = res.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    dataManagerLoading.value = false
  }
}

// 选择/取消选择记录
const toggleRecordSelection = (record) => {
  const index = selectedRecords.value.findIndex(r => r.id === record.id)
  if (index > -1) {
    selectedRecords.value.splice(index, 1)
  } else {
    selectedRecords.value.push(record)
  }
}

// 全选/取消全选
const toggleSelectAll = () => {
  if (selectedRecords.value.length === allRecords.value.length) {
    selectedRecords.value = []
  } else {
    selectedRecords.value = [...allRecords.value]
  }
}

// 删除单条记录
const deleteSingleRecord = async (record) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${record.recordDate} 的${getMetricName(record.metricType)}数据吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteHealthRecord(record.id)
    ElMessage.success('删除成功')
    await loadAllRecords()
    await refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除记录
const batchDeleteRecords = async () => {
  if (selectedRecords.value.length === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 条数据吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const ids = selectedRecords.value.map(r => r.id)
    await batchDeleteHealthRecords(ids)
    ElMessage.success(`成功删除 ${selectedRecords.value.length} 条数据`)
    selectedRecords.value = []
    await loadAllRecords()
    await refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

// 按日期范围删除
const deleteByDateRange = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请先选择日期范围')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${dateRange.value[0]} 至 ${dateRange.value[1]} 期间的所有数据吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteHealthRecordsByDateRange({
      startDate: dateRange.value[0],
      endDate: dateRange.value[1]
    })
    ElMessage.success('删除成功')
    await loadAllRecords()
    await refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 获取指标名称
const getMetricName = (type) => {
  const names = {
    [MetricTypes.RESTING_HEART_RATE]: '静息心率',
    [MetricTypes.SPO2]: '血氧饱和度',
    [MetricTypes.HRV]: '心率变异性',
    [MetricTypes.SLEEP_EFFICIENCY]: '睡眠效率',
    [MetricTypes.DEEP_SLEEP]: '深睡占比',
    [MetricTypes.RESPIRATORY_RATE]: '呼吸频率',
    [MetricTypes.EXERCISE_STEPS]: '步数',
    [MetricTypes.EXERCISE_CALORIES]: '卡路里',
    [MetricTypes.EXERCISE_DURATION]: '运动时长'
  }
  return names[type] || type
}

// 显示健康解读卡片
const showHealthAnalysis = (date) => {
  selectedDate.value = date
  
  // 获取该日期的数据
  const dayRecords = []
  
  // 从各个历史数据中找到对应日期的记录
  const allRecords = [
    ...heartRateHistory.value.map((v, i) => ({ type: 'resting_heart_rate', value: v, date: dayjs().subtract(heartRateHistory.value.length - 1 - i, 'day').format('YYYY-MM-DD') })),
    ...spo2History.value.map((v, i) => ({ type: 'spo2', value: v, date: dayjs().subtract(spo2History.value.length - 1 - i, 'day').format('YYYY-MM-DD') })),
    ...hrvHistory.value.map((v, i) => ({ type: 'hrv', value: v, date: dayjs().subtract(hrvHistory.value.length - 1 - i, 'day').format('YYYY-MM-DD') })),
    ...sleepHistory.value.map((v, i) => ({ type: 'sleep_efficiency', value: v, date: dayjs().subtract(sleepHistory.value.length - 1 - i, 'day').format('YYYY-MM-DD') })),
    ...respirationHistory.value.map((v, i) => ({ type: 'respiratory_rate', value: v, date: dayjs().subtract(respirationHistory.value.length - 1 - i, 'day').format('YYYY-MM-DD') }))
  ]
  
  // 筛选出选中日期和最近几天的记录用于分析
  const targetDate = dayjs(date)
  const endDate = targetDate.add(1, 'day')
  const recentRecords = allRecords.filter(r => {
    const recordDate = dayjs(r.date)
    return recordDate.isAfter(targetDate.subtract(7, 'day')) && (recordDate.isBefore(endDate) || recordDate.isSame(endDate, 'day'))
  })
  
  // 构建分析数据
  const metrics = {
    heartRate: bodyMetrics.heartRate,
    spo2: bodyMetrics.spo2,
    hrv: bodyMetrics.hrv,
    sleepEfficiency: bodyMetrics.sleepEfficiency,
    deepSleep: bodyMetrics.deepSleep,
    respiration: bodyMetrics.respiration,
    heartRateHistory: heartRateHistory.value,
    spo2History: spo2History.value,
    hrvHistory: hrvHistory.value
  }
  
  // 生成分析
  currentAnalysis.value = analyzeHealthData(metrics)
  showAnalysisCard.value = true
}

// 导出分析报告
const exportAnalysis = () => {
  if (!currentAnalysis.value) return
  
  const content = `
健康数据分析报告
生成时间：${new Date().toLocaleString('zh-CN')}
分析日期：${selectedDate.value}

综合健康评分：${currentAnalysis.value.healthScore.score}分

各项指标分析：
${Object.entries(currentAnalysis.value.analyses).map(([key, analysis]) => {
  if (analysis.title === '暂无数据') return ''
  return `
【${analysis.title}】
状态：${getStatusLabel(analysis.status)}
分析：${analysis.summary}
详细数据：
${analysis.details.map(d => '  - ' + d).join('\n')}
改善建议：
${analysis.suggestions.map(s => '  - ' + s).join('\n')}
`
}).join('\n')}

综合建议：
${currentAnalysis.value.overallSuggestions.map(s => '- ' + s).join('\n')}

---
本报告由久物健康AI系统生成，仅供参考。如有健康问题，请咨询专业医生。
  `.trim()
  
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `健康分析报告_${selectedDate.value}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('报告已导出')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.health-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
}

/* Hero Section */
.hero-section {
  padding: 80px 40px 60px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(24, 144, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(54, 207, 201, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-block;
  font-size: 12px;
  letter-spacing: 4px;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 20px;
  padding: 8px 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 30px;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 4px;
}

.hero-subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  margin-bottom: 24px;
}

.hero-desc {
  max-width: 500px;
  margin: 0 auto 32px;
}

.hero-desc p {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  color: #fff;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  position: relative;
  z-index: 1;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

/* Section Header */
.metrics-section,
.exercise-section {
  padding: 60px 40px;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-header.light {
  color: #fff;
}

.section-num {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: #1890ff;
  letter-spacing: 4px;
  margin-bottom: 12px;
}

.section-header.light .section-num {
  color: rgba(255, 255, 255, 0.6);
}

.section-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1a1a2e;
}

.section-header.light .section-title {
  color: #fff;
}

.section-subtitle {
  font-size: 12px;
  color: #999;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.section-header.light .section-subtitle {
  color: rgba(255, 255, 255, 0.4);
}

/* Loading & Empty State */
.loading-state, .empty-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(24, 144, 255, 0.2);
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p, .empty-state p {
  color: #666;
  font-size: 14px;
}

.empty-state {
  background: #fff;
  border-radius: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.empty-icon svg {
  width: 32px;
  height: 32px;
}

.empty-state h3 {
  font-size: 18px;
  color: #1a1a2e;
  margin-bottom: 8px;
}

/* Metrics Dimensions - 多维度管理 */
.metrics-section {
  background: #f8fafc;
}

.metrics-dimensions {
  display: flex;
  flex-direction: column;
  gap: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Dimension Card */
.dimension-card {
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.dimension-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* Cardiovascular - 心血管指标 */
.dimension-card.cardiovascular {
  border-left: 4px solid #ff6b6b;
}

.dimension-card.cardiovascular .dimension-icon {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
}

/* Respiratory - 呼吸与氧合 */
.dimension-card.respiratory {
  border-left: 4px solid #1890ff;
}

.dimension-card.respiratory .dimension-icon {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
}

/* Sleep - 睡眠质量 */
.dimension-card.sleep {
  border-left: 4px solid #722ed1;
}

.dimension-card.sleep .dimension-icon {
  background: linear-gradient(135deg, #722ed1 0%, #b37feb 100%);
}

/* Dimension Header */
.dimension-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 28px 32px;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-bottom: 1px solid #f0f0f0;
}

.dimension-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dimension-icon svg {
  width: 28px;
  height: 28px;
}

.dimension-info {
  flex: 1;
}

.dimension-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.dimension-subtitle {
  font-size: 12px;
  color: #999;
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* Dimension Content */
.dimension-content {
  padding: 32px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

/* 左侧指标区域 */
.metrics-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 次要指标堆叠 */
.secondary-metrics-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 右侧健康解读区域 */
.metrics-right {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.metrics-right .metric-analysis {
  margin-top: 0;
  height: 100%;
  min-height: 200px;
}

/* Metric Item */
.metric-item {
  position: relative;
  padding: 24px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.metric-item.primary {
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border: 1px solid #f0f0f0;
}

.metric-item.secondary {
  background: linear-gradient(135deg, rgba(26, 26, 46, 0.6) 0%, rgba(22, 33, 62, 0.6) 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-item.secondary .metric-name {
  color: rgba(255, 255, 255, 0.9);
}

.metric-item.secondary .metric-number {
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.metric-item.secondary .metric-range-info {
  color: rgba(255, 255, 255, 0.5);
}

.metric-item.secondary:hover {
  background: linear-gradient(135deg, rgba(26, 26, 46, 0.8) 0%, rgba(22, 33, 62, 0.8) 100%);
  border-color: rgba(54, 207, 201, 0.3);
  box-shadow: 0 4px 20px rgba(54, 207, 201, 0.15);
  transform: translateY(-2px);
}

.metric-item:hover {
  border-color: #d9d9d9;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.metric-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.metric-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.metric-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
}

.metric-badge.normal {
  background: #f6ffed;
  color: #52c41a;
}

.metric-badge.attention {
  background: #fffbe6;
  color: #faad14;
}

.metric-badge.warning {
  background: #fff2f0;
  color: #ff4d4f;
}

.metric-value-wrapper {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.metric-number {
  font-size: 42px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1;
  background: linear-gradient(135deg, #1a1a2e 0%, #4a4a6a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.metric-item.primary .metric-number {
  font-size: 52px;
}

.metric-unit {
  font-size: 14px;
  color: #999;
}

.metric-range-info {
  font-size: 12px;
  color: #bbb;
  margin-bottom: 16px;
}

.metric-trend {
  height: 140px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  padding: 0;
  border: 1px solid rgba(0, 0, 0, 0.06);
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.02);
}

.metric-trend :deep(.chart) {
  width: 100%;
  height: 100%;
}

.no-trend-data {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  font-size: 12px;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
}

/* 健康分析区域 - 白色主题 */
.metric-analysis {
  margin-top: 0;
  padding: 28px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  text-align: left;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.analysis-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.analysis-title svg {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
}

.analysis-content {
  font-size: 14px;
  line-height: 1.9;
  color: #4b5563;
  text-align: left;
}

/* 分析段落区块 */
.analysis-section {
  margin-bottom: 24px;
}

.analysis-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
  padding-left: 12px;
  border-left: 3px solid #1890ff;
}

.section-text {
  margin: 0 0 10px 0;
  color: #374151;
  line-height: 1.9;
  text-align: justify;
  font-size: 14px;
}

.section-detail {
  margin: 0;
  color: #6b7280;
  line-height: 1.8;
  text-align: justify;
  font-size: 13px;
  padding: 12px;
  background: rgba(24, 144, 255, 0.04);
  border-radius: 8px;
  border-left: 2px solid rgba(24, 144, 255, 0.2);
}

.section-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.section-list li {
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
  color: #4b5563;
  line-height: 1.7;
}

.section-list li:last-child {
  margin-bottom: 0;
}

.section-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 9px;
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 50%;
}

/* 旧样式兼容 */
.analysis-summary {
  margin: 0 0 16px 0;
  color: #1f2937;
  text-align: left;
}

.analysis-suggestions {
  margin: 0;
  padding-left: 0;
  list-style: none;
  color: #6b7280;
  text-align: left;
}

.analysis-suggestions li {
  margin-bottom: 8px;
  position: relative;
  padding-left: 16px;
}

.analysis-suggestions li:last-child {
  margin-bottom: 0;
}

.analysis-suggestions li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  width: 6px;
  height: 6px;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 50%;
}

/* Responsive */
@media (max-width: 1024px) {
  .dimension-content {
    grid-template-columns: 1fr;
  }
  
  .metrics-right .metric-analysis {
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .dimension-content {
    grid-template-columns: 1fr;
    padding: 24px;
  }
  
  .dimension-header {
    padding: 20px 24px;
  }
  
  .metrics-left {
    gap: 12px;
  }
  
  .secondary-metrics-stack {
    gap: 10px;
  }
}

/* Exercise Section */
.exercise-section {
  background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
}

.exercise-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1000px;
  margin: 0 auto 48px;
}

.exercise-stat-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.exercise-stat-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-4px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
}

.stat-icon.steps {
  background: rgba(24, 144, 255, 0.15);
  color: #1890ff;
}

.stat-icon.calories {
  background: rgba(255, 107, 107, 0.15);
  color: #ff6b6b;
}

.stat-icon.duration {
  background: rgba(82, 196, 26, 0.15);
  color: #52c41a;
}

.stat-content {
  flex: 1;
}

.stat-num {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
  display: block;
}

.stat-progress {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-bottom: 8px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.stat-target {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

/* Exercise Chart */
.exercise-chart-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 32px;
}

.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.view-toggle {
  display: flex;
  gap: 8px;
}

.toggle-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.toggle-btn.active {
  background: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

.chart-container {
  height: 300px;
}

.chart-container :deep(.chart) {
  width: 100%;
  height: 100%;
}

.no-chart-data-large {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.dialog-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.dialog-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.dialog-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.3s ease;
}

.dialog-close:hover {
  background: #e8e8e8;
}

.dialog-close svg {
  width: 16px;
  height: 16px;
}

.dialog-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.form-section {
  margin-bottom: 24px;
}

.form-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item label {
  font-size: 13px;
  color: #666;
}

.form-item input {
  padding: 10px 12px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-item input:focus {
  outline: none;
  border-color: #1890ff;
}

.form-item input::placeholder {
  color: #bbb;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
}

.btn-cancel, .btn-submit {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #f5f5f5;
  border: none;
  color: #666;
}

.btn-cancel:hover {
  background: #e8e8e8;
}

.btn-submit {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border: none;
  color: #fff;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Health Analysis Card Styles */
.analysis-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  padding: 20px;
  backdrop-filter: blur(8px);
}

.analysis-card {
  background: #fff;
  border-radius: 24px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

.analysis-title-group h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.analysis-date {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.analysis-close {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  transition: all 0.3s ease;
}

.analysis-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.analysis-close svg {
  width: 18px;
  height: 18px;
}

.analysis-content {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
}

/* Score Section */
.score-section {
  display: flex;
  gap: 32px;
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border: 4px solid #e2e8f0;
  flex-shrink: 0;
}

.score-circle.excellent {
  border-color: #10b981;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.score-circle.good {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
}

.score-circle.fair {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.score-circle.poor {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.score-value {
  font-size: 48px;
  font-weight: 800;
  color: #1a1a2e;
  line-height: 1;
}

.score-label {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.score-factors {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  justify-content: center;
}

.factor-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.factor-name {
  width: 60px;
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.factor-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.factor-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.factor-score {
  width: 36px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

/* Analysis List */
.analysis-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}

.analysis-item {
  background: #f8fafc;
  border-radius: 16px;
  padding: 24px;
  border-left: 4px solid #e2e8f0;
}

.analysis-item.normal {
  border-left-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #f8fafc 100%);
}

.analysis-item.warning {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #f8fafc 100%);
}

.analysis-item.abnormal {
  border-left-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #f8fafc 100%);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.item-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.item-icon.heartRate {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
}

.item-icon.spo2 {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
}

.item-icon.hrv {
  background: linear-gradient(135deg, #722ed1 0%, #b37feb 100%);
}

.item-icon.sleep {
  background: linear-gradient(135deg, #13c2c2 0%, #36cfc9 100%);
}

.item-icon.respiration {
  background: linear-gradient(135deg, #fa8c16 0%, #ffc53d 100%);
}

.item-icon svg {
  width: 22px;
  height: 22px;
}

.item-title-group {
  flex: 1;
}

.item-title-group h4 {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.item-status {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 20px;
  font-weight: 600;
}

.item-status.normal {
  background: #d1fae5;
  color: #059669;
}

.item-status.warning {
  background: #fef3c7;
  color: #d97706;
}

.item-status.abnormal {
  background: #fee2e2;
  color: #dc2626;
}

.item-summary {
  font-size: 14px;
  line-height: 1.7;
  color: #4b5563;
  margin-bottom: 16px;
}

.item-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.detail-row {
  font-size: 13px;
  color: #6b7280;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
}

.item-suggestions {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 16px;
}

.item-suggestions h5 {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.item-suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-suggestions li {
  font-size: 13px;
  color: #4b5563;
  padding: 6px 0;
  padding-left: 20px;
  position: relative;
}

.item-suggestions li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: #1890ff;
  font-weight: 600;
}

/* Overall Suggestions */
.overall-suggestions {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 24px;
  color: #fff;
}

.overall-suggestions h4 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
}

.overall-suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.overall-suggestions li {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  padding: 8px 0;
  padding-left: 24px;
  position: relative;
  line-height: 1.6;
}

.overall-suggestions li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #10b981;
  font-weight: 700;
}

/* Analysis Footer */
.analysis-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 32px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.btn-close-analysis, .btn-export {
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-close-analysis {
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #666;
}

.btn-close-analysis:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.btn-export {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border: none;
  color: #fff;
}

.btn-export:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .analysis-card {
    max-height: 95vh;
    border-radius: 20px;
  }
  
  .analysis-header,
  .analysis-content,
  .analysis-footer {
    padding: 20px 24px;
  }
  
  .score-section {
    flex-direction: column;
    align-items: center;
    gap: 24px;
  }
  
  .score-circle {
    width: 120px;
    height: 120px;
  }
  
  .score-value {
    font-size: 40px;
  }
  
  .item-details {
    grid-template-columns: 1fr;
  }
}

/* Responsive */
@media (max-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .exercise-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }
  
  .hero-stats {
    flex-direction: column;
    gap: 20px;
  }
  
  .stat-divider {
    width: 60px;
    height: 1px;
  }
  
  .metrics-grid,
  .exercise-overview {
    grid-template-columns: 1fr;
  }
  
  .chart-controls {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .dialog-content {
    max-height: 95vh;
  }
}

/* 数据管理对话框 */
.data-manager-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.data-manager-dialog {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 900px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.btn-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  padding: 4px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.dialog-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.manager-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.date-range-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
}

.date-range-picker input[type="date"] {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #374151;
  background: #fff;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.btn-batch-delete,
.btn-range-delete {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-batch-delete {
  background: #fef2f2;
  color: #dc2626;
}

.btn-batch-delete:hover:not(:disabled) {
  background: #fecaca;
}

.btn-batch-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-range-delete {
  background: #fff7ed;
  color: #ea580c;
}

.btn-range-delete:hover:not(:disabled) {
  background: #ffedd5;
}

.btn-range-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.records-table-wrapper {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.records-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.records-table th,
.records-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.records-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.records-table tbody tr:hover {
  background: #f9fafb;
}

.records-table tbody tr.selected {
  background: #eff6ff;
}

.col-checkbox {
  width: 50px;
  text-align: center;
}

.col-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.col-date {
  width: 120px;
}

.col-type {
  width: 120px;
}

.col-value {
  width: 80px;
}

.col-notes {
  flex: 1;
}

.col-actions {
  width: 80px;
  text-align: center;
}

.metric-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.metric-tag.resting_heart_rate {
  background: #fef2f2;
  color: #dc2626;
}

.metric-tag.spo2 {
  background: #eff6ff;
  color: #2563eb;
}

.metric-tag.hrv {
  background: #f5f3ff;
  color: #7c3aed;
}

.metric-tag.sleep_efficiency {
  background: #f0fdf4;
  color: #16a34a;
}

.metric-tag.deep_sleep {
  background: #f0f9ff;
  color: #0891b2;
}

.metric-tag.respiratory_rate {
  background: #fff7ed;
  color: #ea580c;
}

.metric-tag.exercise_steps {
  background: #fefce8;
  color: #ca8a04;
}

.metric-tag.exercise_calories {
  background: #fdf2f8;
  color: #db2777;
}

.metric-tag.exercise_duration {
  background: #f5f5f4;
  color: #78716c;
}

.btn-delete {
  padding: 6px 14px;
  background: #fef2f2;
  color: #dc2626;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-delete:hover {
  background: #fecaca;
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.loading-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.empty-cell .empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  color: #d1d5db;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.pagination button {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination button:hover:not(:disabled) {
  background: #e5e7eb;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  font-size: 14px;
  color: #6b7280;
}

@media (max-width: 768px) {
  .data-manager-dialog {
    max-height: 95vh;
    margin: 10px;
  }

  .manager-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .date-range-picker {
    flex-wrap: wrap;
  }

  .toolbar-actions {
    justify-content: flex-end;
  }

  .records-table-wrapper {
    overflow-x: auto;
  }

  .records-table {
    min-width: 600px;
  }
}
</style>
