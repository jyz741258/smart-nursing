# 老人界面大字模式功能说明

## 功能概述

为智慧养老系统添加了专为老年人设计的大字体功能，方便视力较弱的老人用户更轻松地使用系统。

## 主要特性

### 1. 四种字体大小可选

- **正常 (14px)** - 适合标准显示
- **中等 (18px)** - 默认设置，适合大多数老年人
- **大字 (22px)** - 大字体模式，增强可读性
- **特大 (28px)** - 超大字体，适合严重视力困难的用户

### 2. 全局应用

字体大小设置会在所有页面生效，包括：
- 老人主页 (ElderDashboard)
- 服务列表 (Services)
- 健康监测 (Health)
- 消息通知 (Notifications)
- 护理计划 (CarePlan)
- 其他所有页面

### 3. 持久化存储

用户的字体偏好设置会自动保存到 localStorage，下次访问时自动应用。

### 4. 高对比度模式（可选）

同时支持高对比度模式，为色弱或视觉障碍用户提供更好的可访问性。

## 使用方法

### 方法一：顶部导航栏切换（所有用户）

1. 在页面右上角找到字体大小指示器
2. 点击下拉箭头展开菜单
3. 选择需要的字体大小：
   - 点击 "增大字体" / "减小字体" 逐步调整
   - 点击 "恢复默认" 回到中等字体

### 方法二：老人专属悬浮按钮

在老人用户界面（ElderDashboard），右下角有一个绿色的悬浮按钮：

1. 点击悬浮按钮展开字体菜单
2. 可以看到四种字体大小的预览效果
3. 直接点击想要的字体大小即可立即切换
4. 点击 "恢复默认" 重置为中等字体

## 技术实现

### 1. Pinia Store (`frontend/src/store/settings.ts`)

```typescript
export const useSettingsStore = defineStore('settings', () => {
  const fontSize = ref<string>('medium')  // 字体大小状态
  const highContrast = ref<boolean>(false) // 高对比度模式

  const setFontSize = (size: string) => {
    fontSize.value = size
    localStorage.setItem('fontSize', size)
    applyFontSize()
  }

  const initSettings = () => {
    applyFontSize()
    applyHighContrast()
  }
})
```

### 2. 全局样式变量 (`App.vue`)

```css
:root {
  --base-font-size: 18px;  /* 动态调整 */
  --font-scale-small: 0.78;   /* 14/18 */
  --font-scale-medium: 1;      /* 18/18 */
  --font-scale-large: 1.22;    /* 22/18 */
  --font-scale-xlarge: 1.56;   /* 28/18 */
}

html {
  font-size: var(--base-font-size);
}

body {
  font-size: var(--base-font-size);
  transition: font-size 0.3s ease;
}
```

### 3. 组件实现

- **MainLayout.vue** - 在顶部导航栏添加字体控制
- **FontSizeToggle.vue** - 老人专属悬浮切换按钮
- **ElderDashboard.vue** - 集成字体切换组件

### 4. 响应式字体

所有字体使用相对单位或 `calc()` 函数，确保平滑过渡：

```scss
// 使用 em 和 rem 单位
font-size: 1em;          // 相对父元素
font-size: 1.2rem;       // 相对根元素

// 使用 calc() 动态计算
font-size: calc(1rem + 0.3vw);  // 响应式字体

// 使用 CSS 变量
font-size: var(--base-font-size);
```

## 文件修改列表

### 新增文件
- `frontend/src/store/settings.ts` - 设置状态管理
- `frontend/src/components/FontSizeToggle.vue` - 字体切换组件

### 修改文件
- `frontend/src/App.vue` - 添加全局样式变量和过渡效果
- `frontend/src/layouts/MainLayout.vue` - 添加顶部字体控制
- `frontend/src/views/ElderDashboard.vue` - 集成字体切换组件
- `frontend/src/views/ElderDashboard.vue` - 优化字体响应式样式
- `frontend/src/views/Health.vue` - 优化字体响应式样式
- `frontend/src/views/Services.vue` - 优化字体响应式样式

## 设计亮点

1. **老年友好**
   - 大按钮（最小 44px 高度）
   - 高对比度色彩
   - 清晰的字体预览
   - 直观的图标和标签

2. **易用性**
   - 一键切换，操作简单
   - 实时预览效果
   - 悬停动画反馈
   - 悬浮球方便老人操作

3. **可访问性**
   - 键盘导航支持
   - 焦点可见样式
   - 支持屏幕阅读器
   - 尊重系统偏好（prefers-reduced-motion）

4. **美观性**
   - 绿色主题，符合养老系统风格
   - 平滑的过渡动画
   - 清晰的状态指示
   - 响应式设计

## 测试建议

1. **功能测试**
   - 切换字体大小，确认所有文本随之变化
   - 刷新页面，确认设置被保存
   - 在不同页面切换，确认全局生效

2. **兼容性测试**
   - 桌面端 Chrome / Firefox / Safari / Edge
   - 移动端 iOS Safari / Android Chrome
   - 不同屏幕尺寸

3. **可访问性测试**
   - 使用键盘 Tab 键导航
   - 使用屏幕阅读器（如 NVDA、VoiceOver）
   - 高对比度模式效果

4. **用户体验测试**
   - 让老年人实际试用
   - 收集反馈意见
   - 调整字体大小阈值

## 扩展建议

未来可以进一步优化：

1. **自定义字体大小滑块** - 让用户可以精确调整字体大小
2. **行高/字间距调整** - 进一步优化可读性
3. **语音播报功能** - 为视障用户朗读页面内容
4. **简化模式** - 隐藏复杂功能，只保留核心操作
5. **一键求助** - 在字体切换界面添加紧急呼叫按钮
6. **家长控制** - 为家属提供远程调整老人界面设置的权限

## 注意事项

- 字体变化时保持布局稳定，避免页面跳动
- 特大字体下可能需要调整某些元素的布局（如按钮换行）
- 考虑打印样式的优化
- 确保高对比度模式下所有元素都清晰可辨

## 联系与反馈

如有问题或建议，欢迎提交 Issue 或 Pull Request。
