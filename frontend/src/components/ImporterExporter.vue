<template>
  <div class="importer-exporter">
    <!-- 导入按钮 -->
    <el-dropdown v-if="showImport" @command="handleImport">
      <el-button :type="type" :size="size" :icon="Upload" :disabled="disabled">
        导入
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="excel">
            <span class="dropdown-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="12" y1="18" x2="12" y2="12" />
                <line x1="9" y1="15" x2="15" y2="15" />
              </svg>
              导入 Excel (.xlsx, .xls)
            </span>
          </el-dropdown-item>
          <el-dropdown-item command="csv">
            <span class="dropdown-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="8" y1="13" x2="16" y2="13" />
                <line x1="8" y1="17" x2="16" y2="17" />
              </svg>
              导入 CSV (.csv)
            </span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 导出按钮 -->
    <el-dropdown v-if="showExport" @command="handleExport">
      <el-button :type="type" :size="size" :icon="Download" :disabled="disabled">
        导出
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="excel">
            <span class="dropdown-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              导出 Excel (.xlsx)
            </span>
          </el-dropdown-item>
          <el-dropdown-item command="csv">
            <span class="dropdown-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              导出 CSV
            </span>
          </el-dropdown-item>
          <el-dropdown-item command="pdf">
            <span class="dropdown-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              导出 PDF
            </span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 隐藏的文件输入框 -->
    <input
      ref="fileInput"
      type="file"
      accept=".xlsx,.xls,.csv"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Download } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { jsPDF } from 'jspdf'
import 'jspdf-autotable'

interface Props {
  data?: any[] // 要导出的数据
  columns?: any[] // 列配置（用于导出）
  showImport?: boolean // 是否显示导入按钮
  showExport?: boolean // 是否显示导出按钮
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'large' | 'default' | 'small'
  disabled?: boolean
  importOptions?: {
    accept?: string // 接受的文件类型
    multiple?: boolean // 是否允许多选
  }
  exportOptions?: {
    filename?: string // 导出文件名
    sheetName?: string // Excel sheet 名称
    pdfOptions?: {
      title?: string // PDF 标题
      orientation?: 'portrait' | 'landscape'
      unit?: 'pt' | 'mm' | 'cm' | 'in'
      format?: 'a4' | 'a3' | string
    }
  }
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  columns: () => [],
  showImport: true,
  showExport: true,
  type: 'primary',
  size: 'default',
  disabled: false,
  importOptions: () => ({
    accept: '.xlsx,.xls,.csv',
    multiple: false
  }),
  exportOptions: () => ({
    filename: '导出数据',
    sheetName: 'Sheet1',
    pdfOptions: {
      title: '数据报表',
      orientation: 'landscape',
      unit: 'mm',
      format: 'a4'
    }
  })
})

const emit = defineEmits(['import', 'export', 'error', 'success'])

const fileInput = ref<HTMLInputElement>()

// ========================
// 导入处理
// ========================
const handleImport = async (command: string) => {
  try {
    // 触发文件选择
    fileInput.value?.click()
  } catch (error) {
    emit('error', error)
    ElMessage.error('导入失败')
  }
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  try {
    const result = await readFile(file)
    emit('import', result)

    ElMessage.success('导入成功')
    emit('success', { type: 'import', data: result })
  } catch (error) {
    console.error('导入错误:', error)
    ElMessage.error('导入失败，请检查文件格式')
    emit('error', error)
  } finally {
    // 重置 input，允许重复选择同一文件
    target.value = ''
  }
}

const readFile = (file: File): Promise<any> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = (e) => {
      try {
        const data = e.target?.result
        const workbook = XLSX.read(data, { type: 'binary' })
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]]

        // 转换为 JSON
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, {
          header: 1, // 数组格式，保留原始结构
          blankrows: false
        })

        // 提取表头（第一行）
        const headers = jsonData[0] as string[]
        const rows = jsonData.slice(1)

        // 转换为对象数组
        const objects = rows.map(row => {
          const obj: any = {}
          headers.forEach((header, index) => {
            obj[header] = row[index]
          })
          return obj
        })

        resolve({
          headers,
          rows,
          objects,
          workbook,
          filename: file.name,
          fileSize: file.size
        })
      } catch (error) {
        reject(error)
      }
    }

    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsBinaryString(file)
  })
}

// ========================
// 导出处理
// ========================
const handleExport = async (format: 'excel' | 'csv' | 'pdf') => {
  if (!props.data.length) {
    ElMessage.warning('没有数据可导出')
    return
  }

  try {
    switch (format) {
      case 'excel':
        exportExcel()
        break
      case 'csv':
        exportCSV()
        break
      case 'pdf':
        await exportPDF()
        break
    }

    ElMessage.success(`成功导出 ${props.data.length} 条记录`)
    emit('success', { type: 'export', format, count: props.data.length })
  } catch (error) {
    console.error('导出错误:', error)
    ElMessage.error('导出失败')
    emit('error', error)
  }
}

// 导出 Excel
const exportExcel = () => {
  const { filename, sheetName } = props.exportOptions

  // 创建工作簿
  const workbook = XLSX.utils.book_new()

  // 准备数据
  const exportData = prepareExportData()

  // 创建工作表
  const worksheet = XLSX.utils.json_to_sheet(exportData, {
    header: props.columns.map(col => col.prop || col.label),
    skipHeader: false
  })

  // 设置列宽
  worksheet['!cols'] = props.columns.map(col => ({
    wch: col.width || 15 // 字符宽度
  }))

  // 添加到工作簿
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)

  // 生成文件名
  const timestamp = new Date().toISOString().slice(0, 10)
  const fullFilename = `${filename}_${timestamp}.xlsx`

  // 导出文件
  XLSX.writeFile(workbook, fullFilename)
}

// 导出 CSV
const exportCSV = () => {
  const { filename } = props.exportOptions
  const exportData = prepareExportData()

  // 添加 BOM 解决中文乱码
  const BOM = '\uFEFF'

  // 构建 CSV 内容
  const headers = props.columns.map(col => col.prop || col.label)
  const csvContent = [
    headers.join(','),
    ...exportData.map(row =>
      headers.map(header => {
        const value = row[header]
        // 处理包含逗号、引号或换行的值
        if (value && (value.toString().includes(',') || value.toString().includes('"') || value.toString().includes('\n'))) {
          return `"${value.toString().replace(/"/g, '""')}"`
        }
        return value
      }).join(',')
    )
  ].join('\n')

  // 创建 Blob 并下载
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${filename}_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

// 导出 PDF
const exportPDF = async () => {
  const { filename, pdfOptions } = props.exportOptions
  const { jsPDF } = await import('jspdf')
  const autoTable = (await import('jspdf-autotable')).default

  const doc = new jsPDF({
    orientation: pdfOptions.orientation,
    unit: pdfOptions.unit,
    format: pdfOptions.format
  })

  // 添加标题
  if (pdfOptions.title) {
    doc.setFontSize(18)
    doc.text(pdfOptions.title, 14, 22)
    doc.setFontSize(11)
  }

  // 准备表格数据
  const headers = props.columns.map(col => ({
    header: col.label || col.prop,
    dataKey: col.prop || col.label
  }))

  const rows = props.data.map(item =>
    headers.map(header => item[header.dataKey] || '')
  )

  // 生成表格
  ;(doc as any).autoTable({
    startY: pdfOptions.title ? 30 : 20,
    head: [headers.map(h => h.header)],
    body: rows,
    theme: 'grid',
    styles: {
      fontSize: 9,
      cellPadding: 3,
      valign: 'middle'
    },
    headStyles: {
      fillColor: [102, 126, 234],
      textColor: 255,
      fontStyle: 'bold'
    },
    alternateRowStyles: {
      fillColor: [245, 247, 250]
    },
    margin: { left: 14, right: 14 },
    tableWidth: 'auto'
  })

  // 添加页脚
  const pageCount = doc.getNumberOfPages()
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i)
    doc.setFontSize(9)
    doc.text(
      `第 ${i} 页 / 共 ${pageCount} 页`,
      doc.internal.pageSize.width / 2,
      doc.internal.pageSize.height - 10,
      { align: 'center' }
    )
  }

  // 保存文件
  const fullFilename = `${filename}_${new Date().toISOString().slice(0, 10)}.pdf`
  doc.save(fullFilename)
}

// 准备导出数据（处理嵌套字段）
const prepareExportData = () => {
  return props.data.map(item => {
    const row: any = {}
    props.columns.forEach(col => {
      const key = col.prop || col.label

      // 支持嵌套字段，如 "user.name"
      if (key.includes('.')) {
        const keys = key.split('.')
        let value = item
        for (const k of keys) {
          value = value?.[k]
        }
        row[key] = value
      } else {
        row[key] = item[key]
      }
    })
    return row
  })
}

// 暴露方法供父组件调用
defineExpose({
  triggerImport: () => fileInput.value?.click()
})
</script>

<style scoped lang="scss">
.importer-exporter {
  display: inline-flex;
  gap: 8px;
  align-items: center;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;

  svg {
    width: 16px;
    height: 16px;
    color: var(--text-secondary);
  }
}

/* 音效反馈 */
.importer-exporter :deep(.el-button) {
  position: relative;
  overflow: hidden;

  &:active {
    transform: scale(0.98);
  }
}

/* 悬停动画 */
.importer-exporter :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}
</style>
