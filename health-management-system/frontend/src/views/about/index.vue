<template>
  <div class="about-container" ref="containerRef">
    <!-- 固定导航指示器 -->
    <div class="nav-dots">
      <div 
        v-for="n in 9" 
        :key="n"
        :class="['nav-dot', { active: currentSection === n }]"
        @click="scrollToSection(n)"
      >
        <span class="dot-label">{{ getSectionLabel(n) }}</span>
      </div>
    </div>

    <!-- Section 1: Hero - 品牌展示 -->
    <section class="section hero-section" :class="{ active: currentSection === 1 }" id="section1">
      <!-- 极光背景效果 -->
      <AuroraBackground
        class="hero-aurora-bg"
        :color-stops="['#00d4aa', '#7c3aed', '#00d4aa']"
        :amplitude="0.5"
        :blend="0.8"
        :speed="1"
      />
      <div class="section-content">
        <div class="hero-badge">JIUWU HEALTH</div>
        <h1 class="hero-title">久物健康</h1>
        <p class="hero-slogan">科技赋能健康 · 智慧守护生命</p>
        <div class="hero-desc">
          <p>以人工智能为核心驱动力，构建覆盖全生命周期的智慧健康管理生态系统</p>
          <p>让每个人都能享受精准、高效、个性化的健康管理服务</p>
        </div>
        <div class="scroll-hint" @click="scrollToSection(2)">
          <span>向下滚动探索</span>
          <div class="scroll-arrow"></div>
        </div>
      </div>
      <div class="hero-bg-pattern"></div>
    </section>

    <!-- Section 2: 企业使命 -->
    <section class="section mission-section" :class="{ active: currentSection === 2 }" id="section2">
      <div class="section-content">
        <div class="section-header">
          <span class="section-num">01</span>
          <h2 class="section-title">企业使命</h2>
          <p class="section-subtitle">Corporate Mission</p>
        </div>
        <div class="mission-content">
          <div class="mission-quote">
            "用科技守护生命健康，让健康管理更智能、更普惠、更人性化"
          </div>
          <div class="mission-text">
            <p>久物健康成立于2020年，总部位于杭州滨江物联网小镇。作为一家专注于智慧健康管理的高科技企业，我们始终秉持"科技赋能健康，智慧守护生命"的核心理念，深度融合人工智能、大数据分析、物联网等前沿技术，致力于构建覆盖全生命周期的智慧健康管理生态系统。</p>
            <p>我们相信，科技的力量可以让健康管理变得更加精准、高效和个性化。通过持续的技术创新和产品优化，久物健康正在帮助数百万用户实现从被动治疗到主动预防的健康理念转变，让每个人都能享受到专业级的健康管理服务。</p>
          </div>
          <div class="mission-text-en">
            <p>Founded in 2020 and headquartered in Binjiang IoT Town, Hangzhou, Jiuwu Health is a high-tech enterprise dedicated to intelligent health management. We consistently uphold the core philosophy of "Empowering Health with Technology, Guarding Life with Wisdom," deeply integrating cutting-edge technologies such as artificial intelligence, big data analytics, and the Internet of Things to build a comprehensive intelligent health management ecosystem covering the entire life cycle.</p>
            <p>We believe that the power of technology can make health management more precise, efficient, and personalized. Through continuous technological innovation and product optimization, Jiuwu Health is helping millions of users shift from passive treatment to proactive prevention, enabling everyone to enjoy professional-grade health management services.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 3: 核心优势 -->
    <section class="section advantages-section" :class="{ active: currentSection === 3 }" id="section3">
      <div class="section-content">
        <div class="section-header light">
          <span class="section-num">02</span>
          <h2 class="section-title">核心优势</h2>
          <p class="section-subtitle">Core Advantages</p>
        </div>
        <div class="advantages-grid">
          <div class="advantage-card">
            <div class="advantage-num">01</div>
            <h3>AI智能诊断引擎</h3>
            <p>基于深度学习技术构建的智能健康助手，整合医学知识图谱与临床诊疗数据，提供7×24小时不间断的智能问诊服务。系统可自动分析用户症状描述，给出初步健康评估和建议，实现疾病的早发现、早预防。</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-num">02</div>
            <h3>全维度数据可视化</h3>
            <p>将复杂的健康数据转化为直观的可视化图表，涵盖血糖、血压、心率、睡眠质量等多维度指标。通过趋势分析和异常预警，帮助用户全面掌握自身健康状况，做出科学的健康决策。</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-num">03</div>
            <h3>IoT生态无缝连接</h3>
            <p>支持血糖仪、血压计、智能手环、体脂秤等上百种健康监测设备的接入。数据自动同步至云端，构建完整的个人健康档案，告别手动记录的繁琐，实现健康管理的数字化、智能化。</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-num">04</div>
            <h3>智能报告解读系统</h3>
            <p>运用自然语言处理技术，将晦涩的医学术语转化为通俗易懂的解读报告。AI自动识别体检报告中的异常指标，结合用户历史数据，生成个性化的健康改善方案和就医建议。</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-num">05</div>
            <h3>千人千面精准服务</h3>
            <p>基于用户画像和行为分析，为每位用户量身定制健康管理方案。无论是慢病管理、体重控制还是运动健身，系统都能根据个体差异提供最适合的建议，真正实现个性化健康管理。</p>
          </div>
          <div class="advantage-card">
            <div class="advantage-num">06</div>
            <h3>金融级安全保障</h3>
            <p>采用银行级数据加密技术和多重隐私保护机制，所有健康数据均经过脱敏处理后存储。通过ISO 27001信息安全管理体系认证，确保用户隐私数据的安全与合规，让用户安心使用。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 4: 技术架构 -->
    <section class="section technology-section" :class="{ active: currentSection === 4 }" id="section4">
      <div class="section-content">
        <div class="section-header">
          <span class="section-num">03</span>
          <h2 class="section-title">技术架构</h2>
          <p class="section-subtitle">Technology Architecture</p>
        </div>
        <div class="tech-layers">
          <div class="tech-layer">
            <div class="layer-header">
              <span class="layer-tag">应用层</span>
              <h3>智慧健康管理平台</h3>
            </div>
            <div class="layer-content">
              <p>涵盖AI智能问诊、健康数据监测、体检报告管理、健康风险评估、个性化健康方案等核心功能模块，为用户提供一站式的健康管理服务体验。</p>
            </div>
          </div>
          <div class="tech-layer">
            <div class="layer-header">
              <span class="layer-tag">算法层</span>
              <h3>AI核心引擎</h3>
            </div>
            <div class="layer-content">
              <p>基于Transformer架构的医疗大语言模型，融合知识图谱与强化学习技术，实现症状理解、疾病预测、用药推荐等智能化功能，持续学习优化诊疗能力。</p>
            </div>
          </div>
          <div class="tech-layer">
            <div class="layer-header">
              <span class="layer-tag">数据层</span>
              <h3>大数据平台</h3>
            </div>
            <div class="layer-content">
              <p>分布式数据存储与计算架构，支持PB级健康数据的实时处理与分析。通过数据挖掘和机器学习，发现健康趋势与风险因子，为精准医疗提供数据支撑。</p>
            </div>
          </div>
          <div class="tech-layer">
            <div class="layer-header">
              <span class="layer-tag">接入层</span>
              <h3>物联网网关</h3>
            </div>
            <div class="layer-content">
              <p>标准化设备接入协议，支持蓝牙、WiFi、NFC等多种通信方式。统一的数据采集与预处理机制，确保来自不同厂商设备的数据格式一致性和准确性。</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 5: 数据实力 -->
    <section class="section stats-section" :class="{ active: currentSection === 5 }" id="section5">
      <div class="section-content">
        <div class="section-header light">
          <span class="section-num">04</span>
          <h2 class="section-title">数据实力</h2>
          <p class="section-subtitle">Data Strength</p>
        </div>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number" data-target="300">0</div>
            <div class="stat-unit">万+</div>
            <div class="stat-label">健康数据记录</div>
            <p class="stat-desc">累计服务用户产生的健康数据总量</p>
          </div>
          <div class="stat-item">
            <div class="stat-number" data-target="200">0</div>
            <div class="stat-unit">+</div>
            <div class="stat-label">覆盖城市</div>
            <p class="stat-desc">服务网络遍布全国主要城市</p>
          </div>
          <div class="stat-item">
            <div class="stat-number" data-target="50">0</div>
            <div class="stat-unit">+</div>
            <div class="stat-label">合作医疗机构</div>
            <p class="stat-desc">与三甲医院、体检中心深度合作</p>
          </div>
          <div class="stat-item">
            <div class="stat-number" data-target="99.9">0</div>
            <div class="stat-unit">%</div>
            <div class="stat-label">系统可用性</div>
            <p class="stat-desc">7×24小时稳定运行保障</p>
          </div>
        </div>
        <div class="stats-highlight">
          <div class="highlight-item">
            <span class="highlight-num">10亿+</span>
            <span class="highlight-text">AI对话交互次数</span>
          </div>
          <div class="highlight-item">
            <span class="highlight-num">500万+</span>
            <span class="highlight-text">体检报告智能解读</span>
          </div>
          <div class="highlight-item">
            <span class="highlight-num">98.5%</span>
            <span class="highlight-text">用户满意度</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 6: 资质认证 -->
    <section class="section certification-section" :class="{ active: currentSection === 6 }" id="section6">
      <div class="section-content">
        <div class="section-header">
          <span class="section-num">05</span>
          <h2 class="section-title">资质认证</h2>
          <p class="section-subtitle">Certifications</p>
        </div>
        <div class="cert-intro">
          <p>久物健康始终将信息安全和用户隐私保护置于首位，建立了完善的安全管理体系，获得了多项国内外权威认证，为用户提供可靠的安全保障。</p>
        </div>
        <div class="cert-grid">
          <div class="cert-card">
            <div class="cert-badge">ISO</div>
            <h4>ISO 27001</h4>
            <p>信息安全管理体系认证</p>
            <span class="cert-year">2019年通过</span>
          </div>
          <div class="cert-card">
            <div class="cert-badge">等保</div>
            <h4>三级等保</h4>
            <p>国家信息安全等级保护</p>
            <span class="cert-year">2019年备案</span>
          </div>
          <div class="cert-card">
            <div class="cert-badge">HIPAA</div>
            <h4>HIPAA合规</h4>
            <p>国际医疗隐私保护标准</p>
            <span class="cert-year">2020年认证</span>
          </div>
          <div class="cert-card">
            <div class="cert-badge">GDPR</div>
            <h4>GDPR合规</h4>
            <p>欧盟数据保护条例</p>
            <span class="cert-year">2021年认证</span>
          </div>
        </div>
        <div class="awards-section">
          <h3>荣誉奖项</h3>
          <div class="awards-list">
            <div class="award-item">
              <span class="award-year">2024</span>
              <span class="award-name">国家高新技术企业</span>
            </div>
            <div class="award-item">
              <span class="award-year">2023</span>
              <span class="award-name">浙江省"专精特新"中小企业</span>
            </div>
            <div class="award-item">
              <span class="award-year">2022</span>
              <span class="award-name">中国智慧医疗创新奖</span>
            </div>
            <div class="award-item">
              <span class="award-year">2021</span>
              <span class="award-name">杭州市"雏鹰计划"企业</span>
            </div>
            <div class="award-item">
              <span class="award-year">2020</span>
              <span class="award-name">最具投资价值健康科技企业</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 7: 发展历程 -->
    <section class="section timeline-section" :class="{ active: currentSection === 7 }" id="section7">
      <div class="section-content">
        <div class="section-header light">
          <span class="section-num">06</span>
          <h2 class="section-title">发展历程</h2>
          <p class="section-subtitle">Development History</p>
        </div>
        <div class="timeline">
          <div class="timeline-item">
            <div class="timeline-year">2024</div>
            <div class="timeline-content">
              <h4>生态拓展</h4>
              <p>服务网络覆盖全国200+城市，合作医疗机构突破50家，用户规模突破500万</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2023</div>
            <div class="timeline-content">
              <h4>技术突破</h4>
              <p>自研医疗大语言模型上线，AI诊断准确率达到三甲医院主治医师水平</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2022</div>
            <div class="timeline-content">
              <h4>产品升级</h4>
              <p>推出3.0版本，整合体检管理、慢病监测、健康档案等全场景功能</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2021</div>
            <div class="timeline-content">
              <h4>规模扩张</h4>
              <p>完成A轮融资，团队扩展至200人，入选杭州市"雏鹰计划"企业</p>
            </div>
          </div>
          <div class="timeline-item">
            <div class="timeline-year">2020</div>
            <div class="timeline-content">
              <h4>公司成立</h4>
              <p>久物健康在杭州成立，首款AI健康助手产品正式上线运营</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 8: 未来愿景 -->
    <section class="section vision-section" :class="{ active: currentSection === 8 }" id="section8">
      <div class="section-content">
        <div class="section-header">
          <span class="section-num">07</span>
          <h2 class="section-title">未来愿景</h2>
          <p class="section-subtitle">Future Vision</p>
        </div>
        <div class="vision-content">
          <div class="vision-main">
            <h3>成为全球领先的智慧健康管理平台</h3>
            <p>久物健康将持续以科技创新为驱动，以用户需求为导向，不断深化在智慧健康管理领域的布局。我们计划进一步加大研发投入，持续优化现有产品和服务，积极探索智慧医疗、智慧养老、数字疗法等领域的新应用、新模式。</p>
            <p>同时，公司将加强与国内外顶尖科研机构、医疗机构的合作与交流，整合优质资源，共同推动医疗健康产业的智能化、数字化发展，为提升全民健康水平贡献更多科技力量。</p>
          </div>
          <div class="vision-pillars">
            <div class="pillar">
              <h4>智慧医疗</h4>
              <p>构建AI驱动的智能诊疗体系，实现疾病的精准预测与个性化治疗</p>
            </div>
            <div class="pillar">
              <h4>精准健康</h4>
              <p>基于基因组学和大数据的精准健康管理，因人而异的健康干预方案</p>
            </div>
            <div class="pillar">
              <h4>数字疗法</h4>
              <p>通过软件程序实现疾病的治疗、管理和预防，开启数字医疗新时代</p>
            </div>
            <div class="pillar">
              <h4>远程医疗</h4>
              <p>打破地域限制，让优质医疗资源触手可及，实现医疗服务的普惠化</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 9: 联系我们 -->
    <section class="section contact-section" :class="{ active: currentSection === 9 }" id="section9">
      <div class="section-content">
        <div class="section-header light">
          <span class="section-num">08</span>
          <h2 class="section-title">联系我们</h2>
          <p class="section-subtitle">Contact Us</p>
        </div>
        
        <div class="contact-wrapper">
          <!-- 左侧：联系信息 -->
          <div class="contact-info-panel">
            <div class="contact-brand">
              <h3>久物健康</h3>
              <p>JIUWU HEALTH</p>
            </div>
            <p class="contact-slogan">用科技守护生命健康<br>让健康管理更智能</p>
            
            <div class="contact-details">
              <div class="contact-item">
                <div class="contact-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                </div>
                <div class="contact-text">
                  <h5>总部地址</h5>
                  <p>浙江省杭州市滨江区物联网小镇<br>智慧健康产业园A座18层</p>
                </div>
              </div>
              
              <div class="contact-item">
                <div class="contact-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                  </svg>
                </div>
                <div class="contact-text">
                  <h5>服务热线</h5>
                  <p class="contact-highlight">400-888-9999</p>
                  <p class="contact-note">7×24小时全天候服务</p>
                </div>
              </div>
              
              <div class="contact-item">
                <div class="contact-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                </div>
                <div class="contact-text">
                  <h5>电子邮箱</h5>
                  <p>contact@jiuwu.health</p>
                  <p class="contact-note">商务合作 / 媒体咨询</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 右侧：快速链接 -->
          <div class="contact-links-panel">
            <h4>快速链接</h4>
            <div class="links-grid">
              <a href="#" class="link-card">
                <span class="link-title">商务合作</span>
                <span class="link-desc">bd@jiuwu.health</span>
              </a>
              <a href="#" class="link-card">
                <span class="link-title">客户服务</span>
                <span class="link-desc">support@jiuwu.health</span>
              </a>
              <a href="#" class="link-card">
                <span class="link-title">媒体联系</span>
                <span class="link-desc">pr@jiuwu.health</span>
              </a>
              <a href="#" class="link-card">
                <span class="link-title">加入我们</span>
                <span class="link-desc">hr@jiuwu.health</span>
              </a>
            </div>
            
            <div class="social-links">
              <h5>关注我们</h5>
              <div class="social-icons">
                <a href="#" class="social-icon" title="微信公众号">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.027-.407-.032zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z"/>
                  </svg>
                </a>
                <a href="#" class="social-icon" title="微博">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10.098 20.323c-3.977.391-7.414-1.406-7.672-4.02-.259-2.609 2.759-5.047 6.74-5.441 3.979-.394 7.413 1.404 7.671 4.018.259 2.6-2.759 5.049-6.737 5.439l-.002.004zM9.05 17.219c-.384.616-1.208.884-1.829.602-.612-.279-.793-.991-.406-1.593.379-.595 1.176-.861 1.793-.601.622.263.82.972.442 1.592zm1.27-1.627c-.141.237-.449.353-.689.253-.236-.09-.313-.361-.177-.586.138-.227.436-.346.672-.24.239.09.315.36.18.573h.014zm.176-2.719c-1.893-.493-4.033.45-4.857 2.118-.836 1.704-.026 3.591 1.886 4.21 1.983.64 4.318-.341 5.132-2.179.8-1.793-.201-3.642-2.161-4.149zm7.563-1.224c-.346-.105-.579-.18-.405-.649.381-1.025.421-1.905.003-2.535-.781-1.188-2.924-1.123-5.383-.034 0 0-.772.338-.575-.272.378-1.207.321-2.217-.267-2.8-1.336-1.32-4.887.047-7.93 3.052C1.634 10.848.312 13.18.312 15.139c0 3.747 4.802 6.023 9.503 6.023 6.164 0 10.263-3.58 10.263-6.423 0-1.718-1.45-2.693-2.919-3.09zm.586-5.522c-.941-.953-2.33-1.396-3.659-1.25l.002-.002c-.299.032-.51.285-.482.579.028.295.282.508.581.476.985-.107 1.998.227 2.708.945.709.719 1.038 1.688.921 2.673-.028.294.178.556.476.585.295.029.557-.177.585-.476c.163-1.377-.3-2.75-1.132-3.53zm-1.613 1.613c-.471-.476-1.168-.699-1.833-.625.003 0 .003-.002.003-.002a.49.49 0 0 0-.555.419.49.49 0 0 0 .419.555c.388-.044.787.09 1.062.37.276.28.403.668.346 1.057a.49.49 0 0 0 .419.555c.295.029.557-.177.585-.476.099-.669-.136-1.36-.446-1.853z"/>
                  </svg>
                </a>
                <a href="#" class="social-icon" title="抖音">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import AuroraBackground from '@/components/AuroraBackground.vue'

const containerRef = ref(null)
const currentSection = ref(1)
const isScrolling = ref(false)
const totalSections = 9

// 获取section标签
const getSectionLabel = (n) => {
  const labels = ['首页', '使命', '优势', '技术', '数据', '资质', '历程', '愿景', '联系']
  return labels[n - 1] || ''
}

// 滚动到指定section
const scrollToSection = (index) => {
  if (isScrolling.value || index < 1 || index > totalSections) return
  
  isScrolling.value = true
  currentSection.value = index
  
  const section = document.getElementById(`section${index}`)
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' })
  }
  
  setTimeout(() => {
    isScrolling.value = false
  }, 800)
}

// 处理滚轮事件
const handleWheel = (e) => {
  e.preventDefault()
  
  if (isScrolling.value) return
  
  const delta = e.deltaY
  if (delta > 0 && currentSection.value < totalSections) {
    scrollToSection(currentSection.value + 1)
  } else if (delta < 0 && currentSection.value > 1) {
    scrollToSection(currentSection.value - 1)
  }
}

// 处理键盘事件
const handleKeydown = (e) => {
  if (e.key === 'ArrowDown' || e.key === 'PageDown') {
    e.preventDefault()
    scrollToSection(currentSection.value + 1)
  } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
    e.preventDefault()
    scrollToSection(currentSection.value - 1)
  }
}

// 数字动画
const animateNumbers = () => {
  const statElements = document.querySelectorAll('.stat-number[data-target]')
  
  statElements.forEach(el => {
    const target = parseFloat(el.getAttribute('data-target'))
    if (isNaN(target)) return
    
    const duration = 2000
    const increment = target / (duration / 16)
    let current = 0
    let hasAnimated = false
    
    const updateNumber = () => {
      current += increment
      if (current < target) {
        el.textContent = target % 1 !== 0 ? current.toFixed(1) : Math.floor(current)
        requestAnimationFrame(updateNumber)
      } else {
        el.textContent = target
      }
    }
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !hasAnimated) {
          hasAnimated = true
          updateNumber()
          observer.unobserve(entry.target)
        }
      })
    })
    
    observer.observe(el)
  })
}

onMounted(() => {
  const container = containerRef.value
  if (container) {
    container.addEventListener('wheel', handleWheel, { passive: false })
  }
  window.addEventListener('keydown', handleKeydown)
  
  animateNumbers()
})

onUnmounted(() => {
  const container = containerRef.value
  if (container) {
    container.removeEventListener('wheel', handleWheel)
  }
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.about-container {
  height: 100vh;
  overflow-y: hidden;
  scroll-behavior: smooth;
}

/* 导航指示器 */
.nav-dots {
  position: fixed;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nav-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.nav-dot:hover,
.nav-dot.active {
  background: #1890ff;
  transform: scale(1.2);
}

.dot-label {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #fff;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s;
  background: rgba(0, 0, 0, 0.6);
  padding: 4px 12px;
  border-radius: 4px;
}

.nav-dot:hover .dot-label {
  opacity: 1;
}

/* 通用Section样式 */
.section {
  height: 100vh;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.section-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
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
  font-size: 14px;
  font-weight: 600;
  color: #1890ff;
  letter-spacing: 4px;
  margin-bottom: 12px;
}

.section-header.light .section-num {
  color: rgba(255, 255, 255, 0.8);
}

.section-title {
  font-size: 40px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1a1a2e;
}

.section-header.light .section-title {
  color: #fff;
}

.section-subtitle {
  font-size: 13px;
  color: #999;
  letter-spacing: 4px;
  text-transform: uppercase;
}

.section-header.light .section-subtitle {
  color: rgba(255, 255, 255, 0.6);
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  text-align: center;
  position: relative;
  overflow: hidden;
}

/* 极光背景 */
.hero-aurora-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.hero-badge {
  display: inline-block;
  font-size: 13px;
  letter-spacing: 6px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 20px;
  padding: 8px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 30px;
}

.hero-title {
  font-size: 64px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 6px;
}

.hero-slogan {
  font-size: 22px;
  color: rgba(255, 255, 255, 0.8);
  letter-spacing: 3px;
  margin-bottom: 32px;
}

.hero-desc {
  max-width: 640px;
  margin: 0 auto 48px;
}

.hero-desc p {
  font-size: 16px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
}

.scroll-hint {
  position: absolute;
  bottom: 48px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  cursor: pointer;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateX(-50%) translateY(0); }
  40% { transform: translateX(-50%) translateY(-10px); }
  60% { transform: translateX(-50%) translateY(-5px); }
}

.scroll-hint span {
  display: block;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.scroll-arrow {
  width: 20px;
  height: 32px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  margin: 0 auto;
  position: relative;
}

.scroll-arrow::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 3px;
  height: 6px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 2px;
  animation: scrollDown 1.5s infinite;
}

@keyframes scrollDown {
  0%, 100% { opacity: 1; transform: translateX(-50%) translateY(0); }
  50% { opacity: 0.3; transform: translateX(-50%) translateY(6px); }
}

.hero-bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(24, 144, 255, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(54, 207, 201, 0.08) 0%, transparent 50%);
  pointer-events: none;
}

/* Mission Section */
.mission-section {
  background: #f8fafc;
}

.mission-content {
  max-width: 840px;
  margin: 0 auto;
}

.mission-quote {
  font-size: 24px;
  font-weight: 500;
  color: #1890ff;
  text-align: center;
  line-height: 1.6;
  margin-bottom: 36px;
  padding: 28px 32px;
  border-left: 3px solid #1890ff;
  background: rgba(24, 144, 255, 0.05);
  border-radius: 0 8px 8px 0;
}

.mission-text p {
  font-size: 15px;
  line-height: 1.9;
  color: #555;
  margin-bottom: 16px;
  text-align: justify;
}

.mission-text-en {
  margin-top: 28px;
  padding-top: 28px;
  border-top: 1px solid #e8e8e8;
}

.mission-text-en p {
  font-size: 14px;
  line-height: 1.8;
  color: #888;
  margin-bottom: 14px;
  text-align: justify;
  font-style: italic;
}

/* Advantages Section */
.advantages-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.advantage-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 28px 24px;
  transition: all 0.3s ease;
}

.advantage-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-4px);
  border-color: rgba(24, 144, 255, 0.25);
}

.advantage-num {
  font-size: 36px;
  font-weight: 700;
  color: rgba(24, 144, 255, 0.25);
  margin-bottom: 12px;
  line-height: 1;
}

.advantage-card h3 {
  font-size: 17px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 12px;
}

.advantage-card p {
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.65);
}

/* Technology Section */
.technology-section {
  background: #fff;
}

.tech-layers {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tech-layer {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 32px;
  padding: 24px 32px;
  background: #f8fafc;
  border-radius: 10px;
  border-left: 3px solid #1890ff;
  transition: all 0.3s ease;
}

.tech-layer:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transform: translateX(4px);
}

.tech-layer:nth-child(2) { border-left-color: #36cfc9; }
.tech-layer:nth-child(3) { border-left-color: #722ed1; }
.tech-layer:nth-child(4) { border-left-color: #eb2f96; }

.layer-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.layer-tag {
  font-size: 11px;
  font-weight: 600;
  color: #1890ff;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

.tech-layer:nth-child(2) .layer-tag { color: #36cfc9; }
.tech-layer:nth-child(3) .layer-tag { color: #722ed1; }
.tech-layer:nth-child(4) .layer-tag { color: #eb2f96; }

.layer-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}

.layer-content p {
  font-size: 14px;
  line-height: 1.7;
  color: #666;
}

/* Stats Section */
.stats-section {
  background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

.stat-item {
  text-align: center;
  padding: 28px 20px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-number {
  font-size: 44px;
  font-weight: 700;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
  display: inline;
}

.stat-unit {
  font-size: 20px;
  font-weight: 600;
  color: #1890ff;
}

.stat-label {
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  margin-top: 8px;
  margin-bottom: 6px;
}

.stat-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.stats-highlight {
  display: flex;
  justify-content: center;
  gap: 60px;
  padding-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.highlight-item {
  text-align: center;
}

.highlight-num {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6px;
}

.highlight-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* Certification Section */
.certification-section {
  background: #f8fafc;
}

.cert-intro {
  max-width: 720px;
  margin: 0 auto 36px;
  text-align: center;
}

.cert-intro p {
  font-size: 15px;
  line-height: 1.8;
  color: #666;
}

.cert-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 48px;
}

.cert-card {
  background: #fff;
  border-radius: 12px;
  padding: 28px 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.cert-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
}

.cert-badge {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  margin: 0 auto 16px;
}

.cert-card h4 {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 6px;
}

.cert-card p {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
}

.cert-year {
  font-size: 11px;
  color: #999;
  padding: 3px 10px;
  background: #f0f0f0;
  border-radius: 20px;
}

.awards-section {
  padding-top: 36px;
  border-top: 1px solid #e8e8e8;
}

.awards-section h3 {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a2e;
  text-align: center;
  margin-bottom: 24px;
}

.awards-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.award-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.03);
}

.award-year {
  font-size: 13px;
  font-weight: 600;
  color: #1890ff;
}

.award-name {
  font-size: 13px;
  color: #555;
}

/* Timeline Section */
.timeline-section {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.timeline {
  max-width: 720px;
  margin: 0 auto;
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 80px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #1890ff 0%, #36cfc9 100%);
}

.timeline-item {
  display: flex;
  gap: 40px;
  margin-bottom: 32px;
  position: relative;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-year {
  width: 80px;
  font-size: 20px;
  font-weight: 700;
  color: #1890ff;
  text-align: right;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
  padding-left: 32px;
  position: relative;
}

.timeline-content::before {
  content: '';
  position: absolute;
  left: -5px;
  top: 6px;
  width: 10px;
  height: 10px;
  background: #1890ff;
  border-radius: 50%;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.2);
}

.timeline-content h4 {
  font-size: 17px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6px;
}

.timeline-content p {
  font-size: 13px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.65);
}

/* Vision Section */
.vision-section {
  background: #fff;
}

.vision-content {
  max-width: 920px;
  margin: 0 auto;
}

.vision-main {
  text-align: center;
  margin-bottom: 40px;
}

.vision-main h3 {
  font-size: 26px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 20px;
}

.vision-main p {
  font-size: 15px;
  line-height: 1.9;
  color: #555;
  margin-bottom: 12px;
}

.vision-pillars {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.pillar {
  padding: 24px 20px;
  background: #f8fafc;
  border-radius: 10px;
  text-align: center;
  transition: all 0.3s ease;
  border-top: 3px solid #1890ff;
}

.pillar:nth-child(2) { border-top-color: #36cfc9; }
.pillar:nth-child(3) { border-top-color: #722ed1; }
.pillar:nth-child(4) { border-top-color: #eb2f96; }

.pillar:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.06);
}

.pillar h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 10px;
}

.pillar p {
  font-size: 12px;
  line-height: 1.7;
  color: #666;
}

/* Contact Section - 全新设计 */
.contact-section {
  background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
}

.contact-wrapper {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 48px;
  align-items: start;
}

/* 左侧联系信息面板 */
.contact-info-panel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 36px;
}

.contact-brand {
  margin-bottom: 20px;
}

.contact-brand h3 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 3px;
  margin-bottom: 4px;
}

.contact-brand p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 3px;
}

.contact-slogan {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.8;
  margin-bottom: 28px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.contact-icon {
  width: 44px;
  height: 44px;
  background: rgba(24, 144, 255, 0.15);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.contact-icon svg {
  width: 20px;
  height: 20px;
  color: #1890ff;
}

.contact-text h5 {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.contact-text p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.contact-highlight {
  font-size: 20px !important;
  font-weight: 600;
  color: #1890ff !important;
  letter-spacing: 1px;
}

.contact-note {
  font-size: 12px !important;
  color: rgba(255, 255, 255, 0.5) !important;
  margin-top: 2px;
}

/* 右侧链接面板 */
.contact-links-panel {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 32px;
}

.contact-links-panel h4 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20px;
  letter-spacing: 1px;
}

.links-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 28px;
}

.link-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.link-card:hover {
  background: rgba(24, 144, 255, 0.1);
  border-color: rgba(24, 144, 255, 0.3);
  transform: translateY(-2px);
}

.link-title {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.link-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.social-links h5 {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 14px;
}

.social-icons {
  display: flex;
  gap: 12px;
}

.social-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.social-icon:hover {
  background: #1890ff;
  transform: translateY(-2px);
}

.social-icon svg {
  width: 20px;
  height: 20px;
  color: #fff;
}

/* 响应式适配 */
@media screen and (max-width: 1024px) {
  .nav-dots {
    right: 20px;
  }
  
  .section-title {
    font-size: 32px;
  }
  
  .hero-title {
    font-size: 48px;
  }
  
  .advantages-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tech-layer {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .cert-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .vision-pillars {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .contact-wrapper {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  
  .timeline::before {
    left: 60px;
  }
  
  .timeline-year {
    width: 60px;
  }
}

@media screen and (max-width: 768px) {
  .about-container {
    overflow-y: auto;
    height: auto;
  }
  
  .nav-dots {
    display: none;
  }
  
  .section {
    height: auto;
    min-height: 100vh;
    padding: 80px 0;
  }
  
  .section-content {
    padding: 0 24px;
  }
  
  .section-title {
    font-size: 26px;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-slogan {
    font-size: 16px;
  }
  
  .mission-quote {
    font-size: 18px;
    padding: 20px;
  }
  
  .advantages-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .stats-highlight {
    flex-direction: column;
    gap: 20px;
  }
  
  .cert-grid {
    grid-template-columns: 1fr;
  }
  
  .awards-list {
    flex-direction: column;
    align-items: center;
  }
  
  .timeline::before {
    left: 50px;
  }
  
  .timeline-item {
    gap: 16px;
  }
  
  .timeline-year {
    width: 50px;
    font-size: 16px;
  }
  
  .timeline-content {
    padding-left: 24px;
  }
  
  .vision-pillars {
    grid-template-columns: 1fr;
  }
  
  .contact-wrapper {
    grid-template-columns: 1fr;
  }
  
  .contact-info-panel,
  .contact-links-panel {
    padding: 24px;
  }
  
  .links-grid {
    grid-template-columns: 1fr;
  }
  
  .footer-links {
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .divider {
    display: none;
  }
}
</style>