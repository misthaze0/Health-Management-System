import { ref, onMounted } from 'vue'

/**
 * 数字滚动动画 - 使用 requestAnimationFrame
 * @param {Ref} targetRef - 目标数值的ref
 * @param {number} endValue - 结束值
 * @param {number} duration - 动画时长(毫秒)
 */
export function useCountUp(targetRef, endValue, duration = 1500) {
  const animatedValue = ref(0)

  onMounted(() => {
    if (endValue !== null && endValue !== undefined) {
      const startTime = performance.now()

      const animate = (currentTime) => {
        const elapsed = currentTime - startTime
        const progress = Math.min(elapsed / duration, 1)
        // ease-out 效果
        const easeProgress = 1 - Math.pow(1 - progress, 3)
        animatedValue.value = endValue * easeProgress
        targetRef.value = Math.round(animatedValue.value * 10) / 10

        if (progress < 1) {
          requestAnimationFrame(animate)
        }
      }

      requestAnimationFrame(animate)
    }
  })
}

/**
 * 元素入场动画 - 使用 CSS 类
 * @param {string} selector - CSS选择器
 * @param {object} options - 动画配置
 */
export function useEntranceAnimation(selector, options = {}) {
  onMounted(() => {
    const elements = document.querySelectorAll(selector)
    const defaults = {
      delay: 0,
      stagger: 100, // 毫秒
    }
    const config = { ...defaults, ...options }

    elements.forEach((el, index) => {
      el.style.opacity = '0'
      el.style.transform = 'translateY(30px)'
      el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out'

      setTimeout(() => {
        el.style.opacity = '1'
        el.style.transform = 'translateY(0)'
      }, config.delay + index * config.stagger)
    })
  })
}

/**
 * 卡片悬浮效果 - 使用 CSS 类
 * @param {HTMLElement} element - DOM元素
 */
export function useHoverEffect(element) {
  if (!element) return

  element.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease'

  element.addEventListener('mouseenter', () => {
    element.style.transform = 'translateY(-5px)'
    element.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.15)'
  })

  element.addEventListener('mouseleave', () => {
    element.style.transform = 'translateY(0)'
    element.style.boxShadow = '0 2px 12px rgba(0, 0, 0, 0.1)'
  })
}

/**
 * 脉冲动画 - 使用 CSS 类
 * @param {HTMLElement} element - DOM元素
 */
export function usePulseAnimation(element) {
  if (!element) return

  element.classList.add('pulse-animation')
}

/**
 * 渐变背景动画 - 使用 CSS
 * @param {HTMLElement} element - DOM元素
 */
export function useGradientAnimation(element) {
  if (!element) return

  element.classList.add('gradient-animation')
}
