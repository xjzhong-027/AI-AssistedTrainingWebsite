/**
 * Duolingo 交互动效工具
 * 轻量级、可复用的动画效果
 */

// ==================== 点击波纹效果 ====================
export const createRipple = (event: MouseEvent, color: string = 'rgba(255, 255, 255, 0.5)') => {
  const button = event.currentTarget as HTMLElement
  const ripple = document.createElement('span')
  const rect = button.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  ripple.style.cssText = `
    position: absolute;
    width: ${size}px;
    height: ${size}px;
    border-radius: 50%;
    background: ${color};
    left: ${x}px;
    top: ${y}px;
    pointer-events: none;
    animation: ripple-animation 0.6s ease-out;
  `

  button.style.position = 'relative'
  button.style.overflow = 'hidden'
  button.appendChild(ripple)

  setTimeout(() => ripple.remove(), 600)
}

// ==================== 成功动画 ====================
export const playSuccessAnimation = (element: HTMLElement) => {
  element.style.animation = 'duo-success-bounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)'
  setTimeout(() => {
    element.style.animation = ''
  }, 600)
}

// ==================== 错误抖动动画 ====================
export const playErrorShake = (element: HTMLElement) => {
  element.style.animation = 'duo-error-shake 0.5s ease-in-out'
  setTimeout(() => {
    element.style.animation = ''
  }, 500)
}

// ==================== 数字滚动动画 ====================
export const animateNumber = (
  element: HTMLElement,
  start: number,
  end: number,
  duration: number = 1000
) => {
  const startTime = Date.now()
  const range = end - start

  const update = () => {
    const now = Date.now()
    const progress = Math.min((now - startTime) / duration, 1)
    const easeProgress = 1 - Math.pow(1 - progress, 3) // easeOutCubic
    const current = start + range * easeProgress

    element.textContent = Math.round(current).toString()

    if (progress < 1) {
      requestAnimationFrame(update)
    }
  }

  requestAnimationFrame(update)
}

// ==================== 淡入动画 ====================
export const fadeIn = (element: HTMLElement, duration: number = 300) => {
  element.style.opacity = '0'
  element.style.transition = `opacity ${duration}ms ease-out`

  requestAnimationFrame(() => {
    element.style.opacity = '1'
  })
}

// ==================== 滑入动画 ====================
export const slideIn = (
  element: HTMLElement,
  direction: 'up' | 'down' | 'left' | 'right' = 'up',
  duration: number = 300
) => {
  const transforms = {
    up: 'translateY(20px)',
    down: 'translateY(-20px)',
    left: 'translateX(20px)',
    right: 'translateX(-20px)'
  }

  element.style.opacity = '0'
  element.style.transform = transforms[direction]
  element.style.transition = `opacity ${duration}ms ease-out, transform ${duration}ms ease-out`

  requestAnimationFrame(() => {
    element.style.opacity = '1'
    element.style.transform = 'translate(0, 0)'
  })
}

// ==================== 脉冲动画 ====================
export const pulse = (element: HTMLElement, scale: number = 1.05) => {
  element.style.transition = 'transform 0.3s ease-out'
  element.style.transform = `scale(${scale})`

  setTimeout(() => {
    element.style.transform = 'scale(1)'
  }, 300)
}

// ==================== 添加全局动画样式 ====================
export const injectAnimationStyles = () => {
  if (document.getElementById('duo-animations')) return

  const style = document.createElement('style')
  style.id = 'duo-animations'
  style.textContent = `
    @keyframes ripple-animation {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }

    @keyframes duo-success-bounce {
      0% { transform: scale(1); }
      25% { transform: scale(1.1); }
      50% { transform: scale(0.95); }
      75% { transform: scale(1.05); }
      100% { transform: scale(1); }
    }

    @keyframes duo-error-shake {
      0%, 100% { transform: translateX(0); }
      10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
      20%, 40%, 60%, 80% { transform: translateX(10px); }
    }

    @keyframes duo-fade-in {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes duo-slide-up {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes duo-pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.05); }
    }

    /* 工具类 */
    .duo-animate-fade-in {
      animation: duo-fade-in 0.3s ease-out;
    }

    .duo-animate-slide-up {
      animation: duo-slide-up 0.3s ease-out;
    }

    .duo-animate-pulse {
      animation: duo-pulse 0.6s ease-in-out;
    }
  `

  document.head.appendChild(style)
}

// 自动注入样式
if (typeof window !== 'undefined') {
  injectAnimationStyles()
}
