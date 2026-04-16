# 📊 数据导入导出组件使用指南

## 组件概述

`ImporterExporter.vue` 是一个功能强大的数据导入导出组件，支持：

- ✅ **Excel 导入** (.xlsx, .xls)
- ✅ **CSV 导入** (.csv)
- ✅ **Excel 导出** (.xlsx)
- ✅ **CSV 导出** (UTF-8 编码，解决中文乱码)
- ✅ **PDF 导出** (支持自定义样式)

---

## 快速开始

### 1. 基础使用

```vue
<template>
  <ImporterExporter
    :data="tableData"
    :columns="columns"
    @success="handleSuccess"
    @error="handleError"
  />
</template>

<script setup>
import { ref } from 'vue'
import ImporterExporter from '@/components/ImporterExporter.vue'

const tableData = ref([
  { name: '张三', age: 25, phone: '13800138000' },
  { name: '李四', age: 30, phone: '13900139000' }
])

const columns = [
  { label: '姓名', prop: 'name', width: 100 },
  { label: '年龄', prop: 'age', width: 80 },
  { label: '电话', prop: 'phone', width: 120 }
]

const handleSuccess = (result) => {
  console.log('操作成功:', result)
}

const handleError = (error) => {
  console.error('操作失败:', error)
}
</script>
```

---

## 完整示例

### 员工管理页面

```vue
<template>
  <div class="employee-management">
    <!-- 操作栏 -->
    <div class="operation-bar">
      <h2>员工管理</h2>

      <div class="actions">
        <!-- 搜索框 -->
        <el-input
          v-model="searchQuery"
          placeholder="搜索员工..."
          style="width: 200px"
        />

        <!-- 导入导出组件 -->
        <ImporterExporter
          :data="filteredEmployees"
          :columns="columns"
          :show-import="true"
          :show-export="true"
          type="primary"
          @import="handleImport"
          @success="handleSuccess"
          @error="handleError"
        />

        <!-- 添加员工按钮 -->
        <el-button type="primary" @click="addEmployee">
          <el-icon><Plus /></el-icon>
          添加员工
        </el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table :data="filteredEmployees" stripe border>
      <el-table-column label="姓名" prop="name" width="120" />
      <el-table-column label="工号" prop="employeeId" width="100" />
      <el-table-column label="部门" prop="department" width="120" />
      <el-table-column label="职位" prop="position" width="120" />
      <el-table-column label="电话" prop="phone" width="130" />
      <el-table-column label="入职日期" prop="joinDate" width="120" />
      <el-table-column label="状态" prop="status" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '在职' : '离职' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right" width="180">
        <template #default="{ row }">
          <el-button link type="primary" @click="editEmployee(row)">
            编辑
          </el-button>
          <el-button link type="danger" @click="deleteEmployee(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import ImporterExporter from '@/components/ImporterExporter.vue'

// ========================
// 数据定义
// ========================
const employees = ref([
  {
    name: '王建国',
    employeeId: 'EMP001',
    department: '护理部',
    position: '护士长',
    phone: '13800001001',
    joinDate: '2020-05-15',
    status: 'active'
  },
  {
    name: '刘美玲',
    employeeId: 'EMP002',
    department: '护理部',
    position: '高级护士',
    phone: '13800001002',
    joinDate: '2021-03-20',
    status: 'active'
  },
  {
    name: '陈志强',
    employeeId: 'EMP003',
    department: '医疗部',
    position: '主治医生',
    phone: '13800001003',
    joinDate: '2019-08-10',
    status: 'active'
  },
  {
    name: '赵小红',
    employeeId: 'EMP004',
    department: '后勤部',
    position: '保洁主管',
    phone: '13800001004',
    joinDate: '2022-01-05',
    status: 'active'
  },
  {
    name: '孙伟明',
    employeeId: 'EMP005',
    department: '餐饮部',
    position: '厨师长',
    phone: '13800001005',
    joinDate: '2021-06-18',
    status: 'inactive'
  }
])

// 表格列配置
const columns = [
  { label: '姓名', prop: 'name', width: 120 },
  { label: '工号', prop: 'employeeId', width: 100 },
  { label: '部门', prop: 'department', width: 120 },
  { label: '职位', prop: 'position', width: 120 },
  { label: '电话', prop: 'phone', width: 130 },
  { label: '入职日期', prop: 'joinDate', width: 120 },
  {
    label: '状态',
    prop: 'status',
    width: 100,
    formatter: (row) => row.status === 'active' ? '在职' : '离职'
  }
]

// 搜索和分页
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => filteredEmployees.value.length)

// 过滤后的数据
const filteredEmployees = computed(() => {
  if (!searchQuery.value) return employees.value

  const query = searchQuery.value.toLowerCase()
  return employees.value.filter(emp =>
    emp.name.toLowerCase().includes(query) ||
    emp.employeeId.toLowerCase().includes(query) ||
    emp.department.toLowerCase().includes(query)
  )
})

// ========================
// 方法
// ========================

// 导入处理
const handleImport = (importResult) => {
  console.log('导入的数据:', importResult)

  // 假设导入的数据格式正确
  const newEmployees = importResult.objects.map((obj, index) => ({
    name: obj['姓名'] || obj.name || `员工${index + 1}`,
    employeeId: obj['工号'] || obj.employeeId || `EMP${Date.now()}`,
    department: obj['部门'] || obj.department || '未分配',
    position: obj['职位'] || obj.position || '员工',
    phone: obj['电话'] || obj.phone || '',
    joinDate: obj['入职日期'] || obj.joinDate || new Date().toISOString().slice(0, 10),
    status: obj['状态'] === '在职' || obj.status === 'active' ? 'active' : 'inactive'
  }))

  // 合并到现有数据
  employees.value = [...employees.value, ...newEmployees]

  ElMessage.success(`成功导入 ${newEmployees.length} 条记录`)
}

// 成功处理
const handleSuccess = (result) => {
  console.log('操作成功:', result)
}

// 错误处理
const handleError = (error) => {
  console.error('操作失败:', error)
  ElMessage.error('操作失败，请重试')
}

// 添加员工
const addEmployee = () => {
  ElMessage.info('打开添加员工对话框...')
}

// 编辑员工
const editEmployee = (row) => {
  ElMessage.info(`编辑员工: ${row.name}`)
}

// 删除员工
const deleteEmployee = (row) => {
  ElMessageBox.confirm(
    `确定要删除员工 "${row.name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    employees.value = employees.value.filter(e => e.employeeId !== row.employeeId)
    ElMessage.success('删除成功')
  }).catch(() => {})
}
</script>

<style scoped lang="scss">
.employee-management {
  padding: 20px;
}

.operation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}
</style>
```

---

## API 参考

### Props

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| `data` | 要导出的数据数组 | `any[]` | `[]` |
| `columns` | 列配置数组 | `ColumnConfig[]` | `[]` |
| `showImport` | 是否显示导入按钮 | `boolean` | `true` |
| `showExport` | 是否显示导出按钮 | `boolean` | `true` |
| `type` | 按钮类型 | `'primary' \| 'success' \| 'warning' \| 'danger' \| 'info'` | `'primary'` |
| `size` | 按钮大小 | `'large' \| 'default' \| 'small'` | `'default'` |
| `disabled` | 是否禁用 | `boolean` | `false` |
| `importOptions` | 导入选项 | `ImportOptions` | `{}` |
| `exportOptions` | 导出选项 | `ExportOptions` | `{}` |

### ColumnConfig

```typescript
interface ColumnConfig {
  label: string      // 列标题
  prop: string       // 数据字段名（支持嵌套如 'user.name'）
  width?: number     // 列宽（字符数）
  formatter?: Function // 格式化函数
}
```

### ImportOptions

```typescript
interface ImportOptions {
  accept?: string    // 接受的文件类型，默认为 '.xlsx,.xls,.csv'
  multiple?: boolean  // 是否允许多选，默认为 false
}
```

### ExportOptions

```typescript
interface ExportOptions {
  filename?: string           // 导出文件名，默认为 '导出数据'
  sheetName?: string          // Excel sheet 名称，默认为 'Sheet1'
  pdfOptions?: {
    title?: string                              // PDF 标题
    orientation?: 'portrait' | 'landscape'      // 页面方向
    unit?: 'pt' | 'mm' | 'cm' | 'in'           // 单位
    format?: 'a4' | 'a3' | string              // 纸张格式
  }
}
```

### Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| `import` | 导入成功时触发 | `ImportResult` |
| `export` | 导出成功时触发 | `{ format, count }` |
| `success` | 任何操作成功时触发 | 操作结果 |
| `error` | 操作失败时触发 | 错误对象 |

### ImportResult

```typescript
interface ImportResult {
  headers: string[]           // 表头数组
  rows: any[][]               // 行数据（数组格式）
  objects: any[]              // 行数据（对象格式）
  workbook: any               // 原始工作簿对象
  filename: string            // 文件名
  fileSize: number            // 文件大小
}
```

---

## 使用场景示例

### 1. 仅导出（无导入）

```vue
<ImporterExporter
  :data="reportData"
  :columns="reportColumns"
  :show-import="false"
/>
```

### 2. 自定义导出文件名

```vue
<ImporterExporter
  :data="employees"
  :columns="columns"
  :export-options="{
    filename: '员工信息表',
    sheetName: '员工列表',
    pdfOptions: {
      title: '智慧养老系统 - 员工信息报表',
      orientation: 'landscape'
    }
  }"
/>
```

### 3. 嵌套字段导出

```typescript
// 数据结构
const orders = [
  {
    id: 'ORD001',
    customer: {
      name: '张三',
      phone: '13800001000'
    },
    total: 2999.00,
    status: 'completed'
  }
]

// 列配置（支持嵌套字段）
const columns = [
  { label: '订单号', prop: 'id' },
  { label: '客户姓名', prop: 'customer.name' },  // 嵌套字段
  { label: '联系电话', prop: 'customer.phone' }, // 嵌套字段
  { label: '订单金额', prop: 'total' },
  { label: '订单状态', prop: 'status' }
]
```

### 4. 格式化列数据

```typescript
const columns = [
  { label: '订单号', prop: 'id' },
  {
    label: '订单金额',
    prop: 'total',
    formatter: (row) => `¥${row.total.toFixed(2)}`
  },
  {
    label: '订单状态',
    prop: 'status',
    formatter: (row) => {
      const statusMap = {
        pending: '待处理',
        processing: '处理中',
        completed: '已完成',
        cancelled: '已取消'
      }
      return statusMap[row.status] || row.status
    }
  }
]
```

---

## 注意事项

### 1. 数据格式要求

**导入**：
- Excel/CSV 文件第一行应为表头
- 支持中文字段名（如"姓名"、"年龄"）
- 日期格式建议使用 ISO 格式 (YYYY-MM-DD)

**导出**：
- 确保 `columns` 配置中的 `prop` 与 `data` 中的字段匹配
- 支持嵌套字段（如 `user.name`）

### 2. 性能考虑

- 大数据量导出时（> 10000 条），建议显示加载状态
- PDF 导出对于超大数据集可能会较慢

### 3. 中文编码

- CSV 导出自动添加 BOM 头，解决 Excel 打开乱码问题
- 确保数据中不包含非法字符

### 4. 浏览器兼容性

- 需要现代浏览器支持（Chrome、Firefox、Safari、Edge）
- IE 11 不支持

---

## 高级用法

### 1. 自定义导入后处理

```javascript
const handleImport = (result) => {
  // 数据验证
  const validData = result.objects.filter(item => {
    return item['姓名'] && item['电话']
  })

  // 数据转换
  const transformedData = validData.map(item => ({
    name: item['姓名'],
    phone: item['电话'],
    // ... 其他字段映射
  }))

  // 批量插入
  batchInsert(transformedData)
}
```

### 2. 分批导出大数据

```javascript
const exportLargeData = async () => {
  const batchSize = 5000
  const total = await fetchTotalCount()

  for (let i = 0; i < total; i += batchSize) {
    const batch = await fetchData(i, batchSize)
    // 追加到导出文件
    appendToExcel(batch)
  }

  downloadExcel()
}
```

### 3. 导入模板下载

```vue
<template>
  <div>
    <el-button @click="downloadTemplate">
      下载导入模板
    </el-button>

    <ImporterExporter :show-export="false" @import="handleImport" />
  </div>
</template>

<script setup>
const downloadTemplate = () => {
  const template = [
    { '姓名': '示例', '电话': '13800000000', '部门': '护理部' }
  ]

  const workbook = XLSX.utils.book_new()
  const worksheet = XLSX.utils.json_to_sheet(template)
  XLSX.utils.book_append_sheet(workbook, worksheet, '导入模板')
  XLSX.writeFile(workbook, '导入模板.xlsx')
}
</script>
```

---

## 故障排除

### 导入失败

1. **文件格式错误**
   - 确保是 .xlsx、.xls 或 .csv 格式
   - 不要导入加密或受保护的文件

2. **文件内容为空**
   - 检查文件是否包含数据
   - 确保表头在第一行

3. **编码问题**
   - CSV 文件确保是 UTF-8 编码

### 导出失败

1. **无数据**
   - 确保 `data` 属性有数据
   - 检查数据格式是否正确

2. **列配置错误**
   - 确保 `columns` 中的 `prop` 与数据字段匹配
   - 支持嵌套字段使用点号分隔

3. **浏览器阻止**
   - 检查浏览器是否阻止了弹出窗口
   - 尝试使用不同的下载方式

---

**版本**：1.0.0
**最后更新**：2026-04-14
**依赖**：`xlsx`, `jspdf`, `jspdf-autotable`

🎉 **享受强大的数据导入导出功能吧！**
