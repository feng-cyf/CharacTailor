// localStorage工具函数

/**
 * 获取localStorage中的值
 * @param {string} key - 存储键名
 * @param {*} defaultValue - 默认值（当键不存在时返回）
 * @returns {*} 存储的值或默认值
 */
export const getLocalStorage = (key, defaultValue = null) => {
  try {
    const value = localStorage.getItem(key);
    return value !== null ? JSON.parse(value) : defaultValue;
  } catch (error) {
    console.error(`Error getting ${key} from localStorage:`, error);
    return defaultValue;
  }
};

/**
 * 设置localStorage中的值
 * @param {string} key - 存储键名
 * @param {*} value - 要存储的值
 * @returns {boolean} 是否设置成功
 */
export const setLocalStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`Error setting ${key} to localStorage:`, error);
    return false;
  }
};

/**
 * 从localStorage中删除值
 * @param {string} key - 要删除的键名
 * @returns {boolean} 是否删除成功
 */
export const removeLocalStorage = (key) => {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Error removing ${key} from localStorage:`, error);
    return false;
  }
};

/**
 * 清空localStorage
 * @returns {boolean} 是否清空成功
 */
export const clearLocalStorage = () => {
  try {
    localStorage.clear();
    return true;
  } catch (error) {
    console.error('Error clearing localStorage:', error);
    return false;
  }
};