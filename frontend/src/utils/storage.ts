/**
 * localStorage工具函数
 */

const STORAGE_PREFIX = 'exam_system_'

export const storage = {
  /**
   * 设置值
   */
  set(key: string, value: any): void {
    try {
      const item = JSON.stringify(value)
      localStorage.setItem(STORAGE_PREFIX + key, item)
    } catch (e) {
      console.error('存储数据失败', e)
    }
  },

  /**
   * 获取值
   */
  get<T = any>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(STORAGE_PREFIX + key)
      if (item) {
        return JSON.parse(item) as T
      }
      return defaultValue || null
    } catch (e) {
      console.error('读取数据失败', e)
      return defaultValue || null
    }
  },

  /**
   * 删除值
   */
  remove(key: string): void {
    localStorage.removeItem(STORAGE_PREFIX + key)
  },

  /**
   * 清空所有
   */
  clear(): void {
    const keys = Object.keys(localStorage)
    keys.forEach((key) => {
      if (key.startsWith(STORAGE_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  }
}

