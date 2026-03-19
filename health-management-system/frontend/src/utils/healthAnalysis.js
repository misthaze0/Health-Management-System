/**
 * 健康数据分析服务
 * 根据用户的健康数据生成专业的解读和建议
 */

// 健康指标标准范围
const HEALTH_STANDARDS = {
  restingHeartRate: { min: 60, max: 100, unit: '次/分', name: '静息心率' },
  spo2: { min: 95, max: 100, unit: '%', name: '血氧饱和度' },
  hrv: { min: 20, max: 60, unit: 'ms', name: '心率变异性' },
  sleepEfficiency: { min: 85, max: 95, unit: '%', name: '睡眠效率' },
  deepSleep: { min: 15, max: 25, unit: '%', name: '深睡占比' },
  respiration: { min: 12, max: 20, unit: '次/分', name: '呼吸频率' }
}

/**
 * 获取指标状态
 */
function getMetricStatus(value, type) {
  const standard = HEALTH_STANDARDS[type]
  if (!standard || value === null || value === undefined) return 'unknown'
  
  if (value >= standard.min && value <= standard.max) return 'normal'
  if (value < standard.min * 0.9 || value > standard.max * 1.1) return 'abnormal'
  return 'warning'
}

/**
 * 生成心率分析
 */
function analyzeHeartRate(value, history = []) {
  if (value === null || value === undefined) {
    return {
      title: '暂无数据',
      summary: '未记录静息心率数据',
      details: [],
      suggestions: []
    }
  }

  const status = getMetricStatus(value, 'restingHeartRate')
  const avg = history.length > 0 
    ? (history.reduce((a, b) => a + b, 0) / history.length).toFixed(0)
    : value
  
  let title, summary, details, suggestions

  if (status === 'normal') {
    title = '心率状态良好'
    summary = `您的静息心率为 ${value} 次/分，处于正常范围（60-100次/分）内，表明心脏功能正常，心血管系统运转良好。`
    details = `根据您的历史数据记录，您的平均心率为 ${avg} 次/分，整体波动在正常范围内。良好的静息心率说明您的心脏泵血效率较高，心血管系统处于健康状态。继续保持当前的生活方式，定期进行健康监测。`
    science = `静息心率是指人在清醒、不活动状态下每分钟心跳的次数，是评估心血管健康的重要指标。正常成年人的静息心率通常在60-100次/分之间。经常进行有氧运动的人群，由于心脏泵血效率提高，静息心率可能会更低（运动员心率可低至40-50次/分），这是心脏功能良好的表现。静息心率长期偏高可能增加心血管疾病风险。心脏每次跳动都会将富含氧气的血液输送到全身各处，心率稳定意味着心脏工作节奏良好，不需要过度努力就能满足身体的血液需求。`
    suggestions = [
      '保持规律的有氧运动，如快走、游泳、骑行等，每周至少150分钟，有助于维持心脏健康',
      '维持良好的睡眠质量，保证每晚7-9小时的充足睡眠，睡眠不足会导致心率升高',
      '定期监测心率变化趋势，建立个人健康档案，及时发现异常波动',
      '保持健康的饮食习惯，减少高盐高脂食物摄入，多吃富含钾、镁的食物如香蕉、坚果',
      '学会管理压力，长期精神紧张会导致交感神经兴奋，使心率加快',
      '限制咖啡因和酒精摄入，这些物质会刺激心脏，导致心率加快'
    ]
  } else if (value < 60) {
    title = '心率偏低'
    summary = `您的静息心率为 ${value} 次/分，低于正常范围。如果您是运动员或经常锻炼，这可能是心脏功能良好的表现；否则建议关注。`
    details = `您的心率比正常下限（60次/分）低了 ${60 - value} 次/分。请结合您的日常活动量和身体感受来判断是否需要关注。如果您经常进行体育锻炼，这通常是正常的生理现象；但如果您平时缺乏运动，或伴有头晕、乏力等症状，建议进一步检查。`
    science = `心率偏低（心动过缓）可能由多种原因引起。对于经常运动的人群，这是心脏泵血效率提高的正常表现，称为"运动员心脏"，每次心跳能泵出更多血液，因此不需要频繁跳动。但如果是非运动人群，可能与窦房结功能异常、甲状腺功能减退、电解质紊乱或某些药物（如β受体阻滞剂）有关。轻度心动过缓通常无症状，但严重时可导致头晕、乏力、胸闷甚至晕厥，因为身体各器官可能得不到足够的血液供应。`
    suggestions = [
      '如非运动员且无运动习惯，建议咨询心内科医生进行专业评估，排除病理性原因',
      '检查当前是否服用可能影响心率的药物，如降压药、镇静剂、抗心律失常药等',
      '避免过度节食或营养不良，保持均衡饮食，确保电解质平衡',
      '定期复查心电图，必要时进行24小时动态心电图监测，了解全天心率变化',
      '如出现头晕、乏力、胸闷、晕厥等症状，应及时就医，可能需要安装心脏起搏器',
      '保持适度运动，但避免突然剧烈运动，运动前后做好热身和放松'
    ]
  } else {
    title = '心率偏高'
    summary = `您的静息心率为 ${value} 次/分，高于正常范围。可能提示身体处于应激状态，长期偏高可能增加心血管负担。`
    details = `您的心率比正常上限（100次/分）高了 ${value - 100} 次/分。持续的心率偏高会使心脏长期处于高负荷工作状态，增加心肌耗氧量，加速心脏老化。建议您回顾近期生活习惯，是否存在熬夜、压力大、过量摄入咖啡因等情况，并及时调整。`
    science = `静息心率持续偏高（心动过速）通常是身体对某种刺激的反应。常见原因包括：长期精神压力导致交感神经兴奋、咖啡因或酒精摄入过量、睡眠不足、贫血、甲状腺功能亢进、脱水或发热等。研究表明，静息心率每增加10次/分，心血管疾病风险可能增加8-20%。长期心率偏高会使心脏长期处于高负荷状态，心肌耗氧量增加，冠状动脉供血不足，加速心肌耗竭，最终可能导致心力衰竭。此外，心率快的人群发生心房颤动的风险也更高。`
    suggestions = [
      '减少咖啡因和酒精摄入，避免浓茶、咖啡、能量饮料等刺激性饮品，这些物质会直接刺激心脏',
      '练习深呼吸、冥想、瑜伽等放松技巧，降低交感神经兴奋度，激活副交感神经',
      '保证充足睡眠（7-9小时），建立规律的作息时间，睡眠不足是导致心率升高的常见原因',
      '进行适度的有氧运动，如快走、慢跑、游泳，规律运动能降低静息心率',
      '如持续偏高超过100次/分，建议就医检查甲状腺功能、血常规、心电图等，排除甲亢、贫血等',
      '学会压力管理，必要时寻求心理咨询支持，长期焦虑抑郁会导致心率持续加快',
      '保持适当体重，肥胖会增加心脏负担，导致心率加快',
      '戒烟限酒，烟草中的尼古丁会刺激心脏，使心率加快'
    ]
  }

  return { title, summary, details, science, suggestions, status }
}

/**
 * 生成血氧分析
 */
function analyzeSpO2(value, history = []) {
  if (value === null || value === undefined) {
    return {
      title: '暂无数据',
      summary: '未记录血氧饱和度数据',
      details: [],
      suggestions: []
    }
  }

  const status = getMetricStatus(value, 'spo2')
  const avg = history.length > 0
    ? (history.reduce((a, b) => a + b, 0) / history.length).toFixed(1)
    : value

  let title, summary, details, suggestions

  if (status === 'normal') {
    title = '血氧水平优秀'
    summary = `您的血氧饱和度为 ${value}%，处于理想范围（95-100%），表明呼吸系统功能良好，血液携氧能力正常，身体各器官氧气供应充足。`
    science = `血氧饱和度（SpO2）是指血液中氧气与血红蛋白结合的比例，是评估呼吸功能和氧气输送能力的关键指标。正常人的血氧饱和度应在95%以上，低于90%即为低氧血症。血氧水平直接影响大脑、心脏等重要器官的功能，长期低氧可能导致器官损伤。夜间血氧监测对于发现睡眠呼吸暂停综合征尤为重要。`
    suggestions = [
      '继续保持良好的生活习惯，远离吸烟环境',
      '适当进行有氧运动如游泳、慢跑，增强肺功能和氧气利用效率',
      '避免长时间处于密闭、空气不流通的空间',
      '如前往高原地区，应逐步适应并监测血氧变化',
      '保持室内空气清新，可使用空气净化器'
    ]
  } else if (value >= 90 && value < 95) {
    title = '血氧轻度偏低'
    summary = `您的血氧饱和度为 ${value}%，略低于理想范围。虽然不会立即造成危险，但提示可能存在轻度呼吸问题，建议关注并改善。`
    science = `轻度低氧血症（90-94%）可能由多种因素引起，包括：轻度呼吸道阻塞、睡眠呼吸暂停综合征、慢性阻塞性肺病早期、贫血、环境因素（高海拔、密闭空间）等。虽然这个水平不会立即危及生命，但长期轻度低氧会影响睡眠质量、导致白天嗜睡、注意力不集中，并可能加重心脏负担。`
    suggestions = [
      '保持卧室和室内良好通风，增加空气流通',
      '采用侧卧睡姿，有助于减少舌根后坠，改善呼吸通畅度',
      '避免睡前饮酒，酒精会抑制呼吸中枢，加重夜间低氧',
      '控制体重，肥胖是睡眠呼吸暂停的重要危险因素',
      '如持续偏低，建议进行多导睡眠监测，排查睡眠呼吸暂停',
      '白天进行深呼吸练习，增强肺功能'
    ]
  } else {
    title = '血氧明显偏低'
    summary = `您的血氧饱和度为 ${value}%，明显低于正常范围。这可能影响身体各器官的氧气供应，存在一定的健康风险，建议及时就医。`
    science = `血氧饱和度低于90%属于低氧血症，需要高度重视。可能的原因包括：肺部疾病（肺炎、慢性阻塞性肺病、肺纤维化）、心脏疾病（心力衰竭、先天性心脏病）、睡眠呼吸暂停综合征、严重贫血、高海拔环境等。持续低氧会导致大脑、心脏等重要器官缺氧损伤，出现头晕、胸闷、呼吸困难等症状，严重时可危及生命。`
    suggestions = [
      '建议尽快就医，进行胸部X光、肺功能、心电图等检查',
      '排查可能的肺部疾病如肺炎、哮喘、慢阻肺等',
      '检查心脏功能，排除心力衰竭等心脏问题',
      '必要时在医生指导下进行家庭氧疗',
      '避免剧烈运动和过度劳累，减少氧气消耗',
      '睡眠时可适当抬高床头，改善呼吸',
      '如伴有呼吸困难、胸痛等症状，应立即急诊就医'
    ]
  }

  return { title, summary, science, suggestions, status }
}

/**
 * 生成HRV分析
 */
function analyzeHRV(value, history = []) {
  if (value === null || value === undefined) {
    return {
      title: '暂无数据',
      summary: '未记录心率变异性数据',
      details: [],
      suggestions: []
    }
  }

  const status = getMetricStatus(value, 'hrv')
  const avg = history.length > 0
    ? (history.reduce((a, b) => a + b, 0) / history.length).toFixed(0)
    : value

  let title, summary, details, suggestions

  if (status === 'normal') {
    title = '自主神经功能良好'
    summary = `您的心率变异性为 ${value}ms，处于正常范围（20-60ms），表明自主神经系统平衡良好，身体适应能力强。`
    details = [
      `当前数值：${value} ms`,
      `正常范围：20-60 ms`,
      `历史均值：${avg} ms`,
      `神经平衡：良好`
    ]
    suggestions = [
      '继续保持规律的作息时间',
      '进行冥想或瑜伽练习',
      '维持良好的压力管理',
      '定期监测HRV变化'
    ]
  } else if (value < 20) {
    title = 'HRV偏低'
    summary = `您的心率变异性为 ${value}ms，低于正常范围。这可能提示身体处于压力状态或恢复不足。`
    details = [
      `当前数值：${value} ms`,
      `正常范围：20-60 ms`,
      `可能原因：压力过大、睡眠不足、过度训练`,
      `身体状态：需恢复`
    ]
    suggestions = [
      '增加休息时间，避免过度训练',
      '练习深呼吸和放松技巧',
      '改善睡眠质量',
      '适当减少工作压力'
    ]
  } else {
    title = 'HRV偏高'
    summary = `您的心率变异性为 ${value}ms，高于正常范围。对于年轻人和运动员来说这是好事，表明心脏适应能力强。`
    details = [
      `当前数值：${value} ms`,
      `正常范围：20-60 ms`,
      `解读：心脏适应能力强`,
      `常见于：运动员、年轻人`
    ]
    suggestions = [
      '继续保持当前的运动习惯',
      '这是心脏健康的积极信号',
      '可作为训练效果的参考指标',
      '如非运动员且感觉不适，建议咨询医生'
    ]
  }

  return { title, summary, details, suggestions, status }
}

/**
 * 生成睡眠分析
 */
function analyzeSleep(efficiency, deepSleep) {
  if (efficiency === null || efficiency === undefined) {
    return {
      title: '暂无数据',
      summary: '未记录睡眠数据',
      details: [],
      suggestions: []
    }
  }

  const effStatus = getMetricStatus(efficiency, 'sleepEfficiency')
  const deepStatus = deepSleep !== null ? getMetricStatus(deepSleep, 'deepSleep') : 'unknown'

  let title, summary, details, suggestions, status

  if (effStatus === 'normal' && (deepStatus === 'normal' || deepStatus === 'unknown')) {
    title = '睡眠质量优秀'
    summary = `您的睡眠效率为 ${efficiency}%，${deepSleep ? `深睡占比 ${deepSleep}%，` : ''}各项指标均处于理想范围，表明睡眠质量良好，身体能够得到充分的休息和恢复。`
    science = `睡眠效率是指实际睡眠时间与躺在床上时间的比例，是衡量睡眠质量的重要指标。理想的睡眠效率应在85%以上。深度睡眠（慢波睡眠）是睡眠周期中最重要的阶段，占整个睡眠时间的15-25%，在此期间身体会分泌生长激素，促进组织修复、肌肉生长和免疫系统强化。良好的睡眠对于记忆巩固、情绪调节和代谢健康都至关重要。`
    suggestions = [
      '继续保持规律的作息时间，每天同一时间上床和起床',
      '睡前1小时避免使用手机、电脑等电子设备，减少蓝光刺激',
      '保持卧室温度在18-22℃，这是最适合睡眠的温度范围',
      '避免睡前2-3小时大量进食，特别是高脂肪、辛辣食物',
      '建立固定的睡前放松仪式，如泡脚、听轻音乐、阅读等',
      '白天适当进行户外运动，有助于夜间更好入睡'
    ]
    status = 'normal'
  } else if (efficiency < 85) {
    title = '睡眠效率偏低'
    summary = `您的睡眠效率为 ${efficiency}%，低于理想范围（85%以上）。这表明您在床上花费的时间较多，但实际睡眠时间不足，可能存在入睡困难、夜间觉醒频繁等问题。`
    science = `睡眠效率偏低通常意味着存在睡眠维持困难。常见原因包括：失眠症（入睡困难或早醒）、睡眠呼吸暂停综合征（夜间反复觉醒）、周期性肢体运动障碍、焦虑或抑郁等心理因素、不规律的作息时间、睡前使用电子设备等。长期睡眠效率低会导致白天嗜睡、注意力不集中、记忆力下降、免疫力降低，并增加心血管疾病和代谢综合征的风险。`
    suggestions = [
      '建立固定的睡前仪式，如温水泡脚、冥想、轻柔拉伸等，帮助身体进入睡眠状态',
      '避免午后2点后摄入咖啡因，包括咖啡、浓茶、巧克力等',
      '睡前进行放松活动如阅读纸质书籍、听轻音乐，避免刺激性内容',
      '如果卧床20分钟仍无法入睡，应起床进行放松活动，有睡意时再回床',
      '保持卧室安静、黑暗、凉爽，使用遮光窗帘和耳塞',
      '限制白天小睡时间，不超过30分钟，避免影响夜间睡眠',
      '如问题持续超过1个月，建议咨询睡眠专科医生或心理科'
    ]
    status = 'warning'
  } else {
    title = '睡眠质量需改善'
    summary = `您的睡眠效率虽然正常，但${deepSleep && deepSleep < 15 ? `深睡占比仅为${deepSleep}%，明显偏低` : '可能存在其他影响睡眠质量的因素'}。深度睡眠对身体恢复和大脑清理代谢废物至关重要。`
    science = `深度睡眠（慢波睡眠）是睡眠周期中最重要的阶段，主要出现在前半夜。在此期间，大脑会清除β-淀粉样蛋白等代谢废物，身体分泌生长激素促进组织修复，免疫系统得到强化。深睡不足会导致：身体恢复不良、免疫力下降、记忆力减退、情绪不稳定、代谢紊乱等。常见原因包括：年龄增长（深睡随年龄减少）、睡眠呼吸暂停、慢性疼痛、酒精摄入、某些药物、压力和焦虑等。`
    suggestions = [
      '增加日间运动量，特别是有氧运动，但避免睡前3小时内剧烈运动',
      '睡前绝对避免酒精摄入，酒精会抑制深睡阶段，导致睡眠质量下降',
      '创造安静、黑暗、凉爽的睡眠环境，必要时使用白噪音机',
      '尝试睡前冥想、渐进式肌肉放松或4-7-8呼吸法',
      '保持规律的作息时间，包括周末，帮助稳定生物钟',
      '检查是否服用可能影响睡眠的药物，必要时咨询医生',
      '如怀疑睡眠呼吸暂停（打鼾、白天嗜睡），应进行睡眠监测'
    ]
    status = 'warning'
  }

  return { title, summary, science, suggestions, status }
}

/**
 * 生成呼吸分析
 */
function analyzeRespiration(value) {
  if (value === null || value === undefined) {
    return {
      title: '暂无数据',
      summary: '未记录呼吸频率数据',
      details: [],
      suggestions: []
    }
  }

  const status = getMetricStatus(value, 'respiration')
  let title, summary, details, suggestions

  if (status === 'normal') {
    title = '呼吸频率正常'
    summary = `您的呼吸频率为 ${value} 次/分，处于正常范围（12-20次/分），表明呼吸系统功能正常。`
    details = [
      `当前数值：${value} 次/分`,
      `正常范围：12-20 次/分`,
      `呼吸模式：正常`,
      `肺功能：良好`
    ]
    suggestions = [
      '继续保持深呼吸习惯',
      '练习腹式呼吸增强肺功能',
      '避免吸烟和二手烟',
      '定期进行户外活动'
    ]
  } else if (value < 12) {
    title = '呼吸频率偏低'
    summary = `您的呼吸频率为 ${value} 次/分，低于正常范围。可能是深度放松状态，也可能是呼吸系统问题。`
    details = [
      `当前数值：${value} 次/分`,
      `正常范围：12-20 次/分`,
      `可能原因：深度放松、药物影响`,
      `注意：如伴随不适需就医`
    ]
    suggestions = [
      '确认是否在深度放松或睡眠状态',
      '检查是否服用镇静类药物',
      '如清醒时持续偏低，建议就医',
      '避免过度换气'
    ]
  } else {
    title = '呼吸频率偏快'
    summary = `您的呼吸频率为 ${value} 次/分，高于正常范围。可能提示身体处于应激状态或存在呼吸问题。`
    details = [
      `当前数值：${value} 次/分`,
      `正常范围：12-20 次/分`,
      `可能原因：焦虑、发热、缺氧`,
      `身体状态：需关注`
    ]
    suggestions = [
      '练习深呼吸和放松技巧',
      '检查是否有发热或感染',
      '确保环境通风良好',
      '如持续偏快，建议就医检查'
    ]
  }

  return { title, summary, details, suggestions, status }
}

/**
 * 生成综合健康评分
 */
function generateHealthScore(metrics) {
  const { heartRate, spo2, hrv, sleepEfficiency, deepSleep, respiration } = metrics
  let score = 100
  let factors = []

  // 心率评分
  if (heartRate !== null && heartRate !== undefined) {
    if (heartRate >= 60 && heartRate <= 100) {
      factors.push({ name: '心率', score: 100, status: 'normal' })
    } else {
      const deviation = Math.min(Math.abs(heartRate - 80), 40)
      const penalty = Math.round((deviation / 40) * 30)
      score -= penalty
      factors.push({ name: '心率', score: 100 - penalty, status: 'warning' })
    }
  }

  // 血氧评分
  if (spo2 !== null && spo2 !== undefined) {
    if (spo2 >= 95) {
      factors.push({ name: '血氧', score: 100, status: 'normal' })
    } else {
      const penalty = Math.round((95 - spo2) * 5)
      score -= penalty
      factors.push({ name: '血氧', score: 100 - penalty, status: spo2 < 90 ? 'abnormal' : 'warning' })
    }
  }

  // 睡眠评分
  if (sleepEfficiency !== null && sleepEfficiency !== undefined) {
    if (sleepEfficiency >= 85) {
      factors.push({ name: '睡眠', score: 100, status: 'normal' })
    } else {
      const penalty = Math.round((85 - sleepEfficiency) * 2)
      score -= penalty
      factors.push({ name: '睡眠', score: 100 - penalty, status: 'warning' })
    }
  }

  // HRV评分
  if (hrv !== null && hrv !== undefined) {
    if (hrv >= 20 && hrv <= 60) {
      factors.push({ name: 'HRV', score: 100, status: 'normal' })
    } else if (hrv < 20) {
      const penalty = Math.round((20 - hrv) * 2)
      score -= penalty
      factors.push({ name: 'HRV', score: 100 - penalty, status: 'warning' })
    } else {
      factors.push({ name: 'HRV', score: 95, status: 'normal' })
    }
  }

  // 呼吸评分
  if (respiration !== null && respiration !== undefined) {
    if (respiration >= 12 && respiration <= 20) {
      factors.push({ name: '呼吸', score: 100, status: 'normal' })
    } else {
      const deviation = Math.min(Math.abs(respiration - 16), 8)
      const penalty = Math.round((deviation / 8) * 20)
      score -= penalty
      factors.push({ name: '呼吸', score: 100 - penalty, status: 'warning' })
    }
  }

  // 确定整体状态
  let overallStatus = 'excellent'
  if (score < 60) overallStatus = 'poor'
  else if (score < 80) overallStatus = 'fair'
  else if (score < 90) overallStatus = 'good'

  return {
    score: Math.max(0, Math.min(100, score)),
    status: overallStatus,
    factors
  }
}

/**
 * 主分析函数
 */
export function analyzeHealthData(metrics) {
  const { 
    heartRate, 
    spo2, 
    hrv, 
    sleepEfficiency, 
    deepSleep, 
    respiration,
    heartRateHistory = [],
    spo2History = [],
    hrvHistory = []
  } = metrics

  // 生成各指标分析
  const analyses = {
    heartRate: analyzeHeartRate(heartRate, heartRateHistory),
    spo2: analyzeSpO2(spo2, spo2History),
    hrv: analyzeHRV(hrv, hrvHistory),
    sleep: analyzeSleep(sleepEfficiency, deepSleep),
    respiration: analyzeRespiration(respiration)
  }

  // 生成综合评分
  const healthScore = generateHealthScore({
    heartRate, spo2, hrv, sleepEfficiency, deepSleep, respiration
  })

  // 生成综合建议
  const overallSuggestions = generateOverallSuggestions(analyses, healthScore)

  return {
    analyses,
    healthScore,
    overallSuggestions,
    analysisDate: new Date().toISOString()
  }
}

/**
 * 生成综合建议
 */
function generateOverallSuggestions(analyses, healthScore) {
  const suggestions = []
  
  // 根据评分给出总体建议
  if (healthScore.score >= 90) {
    suggestions.push('您的整体健康状况良好，请继续保持！')
  } else if (healthScore.score >= 80) {
    suggestions.push('您的健康状况良好，但仍有提升空间。')
  } else if (healthScore.score >= 60) {
    suggestions.push('您的健康状况一般，建议关注以下方面：')
  } else {
    suggestions.push('您的健康状况需要关注，建议采取以下措施：')
  }

  // 找出需要关注的指标
  const concerns = []
  Object.entries(analyses).forEach(([key, analysis]) => {
    if (analysis.status === 'abnormal' || analysis.status === 'warning') {
      concerns.push(analysis.title)
    }
  })

  if (concerns.length > 0) {
    suggestions.push(`需要关注的指标：${concerns.join('、')}`)
  }

  // 添加通用建议
  suggestions.push('保持规律作息，每天保证7-9小时睡眠')
  suggestions.push('每周进行至少150分钟中等强度运动')
  suggestions.push('保持均衡饮食，多吃蔬菜水果')
  suggestions.push('定期体检，及时关注身体变化')

  return suggestions
}

/**
 * 生成单日数据解读
 */
export function analyzeDailyData(date, records) {
  const metrics = {}
  records.forEach(record => {
    const type = record.metricType || record.metric_type
    const value = record.metricValue !== undefined ? record.metricValue : record.metric_value
    switch (type) {
      case 'resting_heart_rate':
        metrics.heartRate = value
        break
      case 'spo2':
        metrics.spo2 = value
        break
      case 'hrv':
        metrics.hrv = value
        break
      case 'sleep_efficiency':
        metrics.sleepEfficiency = value
        break
      case 'deep_sleep':
        metrics.deepSleep = value
        break
      case 'respiratory_rate':
        metrics.respiration = value
        break
    }
  })

  const analysis = analyzeHealthData(metrics)
  
  return {
    date,
    ...analysis,
    summary: generateDailySummary(analysis, date)
  }
}

/**
 * 生成单日总结
 */
function generateDailySummary(analysis, date) {
  const { healthScore, analyses } = analysis
  const dateStr = new Date(date).toLocaleDateString('zh-CN', {
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })

  let summary = `${dateStr}的健康数据分析：`
  
  // 添加评分
  summary += `\n\n综合健康评分：${healthScore.score}分`
  
  // 添加各指标状态
  const statusList = []
  Object.entries(analyses).forEach(([key, item]) => {
    if (item.title !== '暂无数据') {
      const emoji = item.status === 'normal' ? '✓' : item.status === 'warning' ? '!' : '✗'
      statusList.push(`${emoji} ${item.title}`)
    }
  })
  
  if (statusList.length > 0) {
    summary += `\n\n指标状态：\n${statusList.join('\n')}`
  }

  return summary
}

export default {
  analyzeHealthData,
  analyzeDailyData,
  getMetricStatus,
  HEALTH_STANDARDS
}