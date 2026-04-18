<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">老人管理</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加老人
      </el-button>
    </div>

    <div class="card-container">
      <div class="search-form">
        <el-input
          v-model="searchForm.name"
          placeholder="姓名"
          style="width: 200px"
          clearable
        />
        <el-button type="primary" @click="getElderList">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>

      <el-table :data="elderList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            {{ row.gender === 1 ? '男' : row.gender === 2 ? '女' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="address" label="地址" show-overflow-tooltip />
        <el-table-column prop="emergency_contact" label="紧急联系人" />
        <el-table-column prop="emergency_phone" label="紧急联系电话" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="editElder(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteElder(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="getElderList"
        @current-change="getElderList"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEdit ? '编辑老人' : '添加老人'"
      width="600px"
    >
      <el-form ref="formRef" :model="elderForm" :rules="formRules" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="elderForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone" v-if="!isEdit">
          <el-input v-model="elderForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="elderForm.gender">
            <el-radio :label="1">男</el-radio>
            <el-radio :label="2">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="elderForm.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="elderForm.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="elderForm.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="紧急联系人">
          <el-input v-model="elderForm.emergency_contact" placeholder="请输入紧急联系人" />
        </el-form-item>
        <el-form-item label="紧急联系电话">
          <el-input v-model="elderForm.emergency_phone" placeholder="请输入紧急联系电话" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="老人详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="姓名">{{ currentElder.name }}</el-descriptions-item>
        <el-descriptions-item label="性别">
          {{ currentElder.gender === 1 ? '男' : currentElder.gender === 2 ? '女' : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="年龄">{{ currentElder.age }}</el-descriptions-item>
        <el-descriptions-item label="身份证号">{{ currentElder.id_card || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ currentElder.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="紧急联系人">{{ currentElder.emergency_contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="紧急联系电话">{{ currentElder.emergency_phone || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import api from '@/store/auth'
import type { Elder } from '@/types'

const loading = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

const elderList = ref<Elder[]>([])
const currentElder = ref<any>({})

const searchForm = reactive({
  name: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const elderForm = reactive({
  id: null as number | null,
  name: '',
  phone: '',  // 添加老人时需要
  gender: 1,
  age: null as number | null,
  id_card: '',
  address: '',
  emergency_contact: '',
  emergency_phone: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ]
}

const getElderList = async () => {
  loading.value = true
  try {
    const res: any = await api.get('/users/elder/list', {
      params: {
        ...searchForm
      }
    })
    if (res.code === 200) {
      // 后端返回的是完整列表，前端进行本地分页
      const allElders = res.data || []
      // 根据搜索条件过滤
      const filteredElders = allElders.filter((elder: any) => {
        if (searchForm.name) {
          return elder.name.includes(searchForm.name)
        }
        return true
      })
      // 计算分页
      pagination.total = filteredElders.length
      const start = (pagination.page - 1) * pagination.page_size
      const end = start + pagination.page_size
      elderList.value = filteredElders.slice(start, end)
    }
  } catch (error) {
    console.error('获取老人列表失败', error)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.name = ''
  pagination.page = 1
  getElderList()
}

const viewDetail = (row: Elder) => {
  currentElder.value = { ...row }
  showDetailDialog.value = true
}

const editElder = (row: Elder) => {
  isEdit.value = true
  Object.assign(elderForm, row)
  showAddDialog.value = true
}

const deleteElder = async (row: Elder) => {
  try {
    await ElMessageBox.confirm('确定要删除该老人吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    console.log('[Debug] 删除老人，ID:', row.id)
    const res: any = await api.delete(`/users/${row.id}`)
    console.log('[Debug] 删除响应:', res)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      getElderList()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error: any) {
    console.error('[Debug] 删除异常:', error)
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    console.log('[Debug] 提交老人表单:', elderForm, 'isEdit:', isEdit.value)

    if (isEdit.value && elderForm.id) {
      // 编辑模式：调用管理员更新用户接口
      const res: any = await api.put(`/users/${elderForm.id}`, {
        name: elderForm.name,
        gender: elderForm.gender,
        age: elderForm.age,
        id_card: elderForm.id_card,
        address: elderForm.address,
        emergency_contact: elderForm.emergency_contact,
        emergency_phone: elderForm.emergency_phone
      })
      console.log('[Debug] 更新响应:', res)
      if (res.code === 200) {
        ElMessage.success('编辑成功')
        showAddDialog.value = false
        getElderList()
      } else {
        ElMessage.error(res.message || '编辑失败')
      }
    } else {
      // 添加模式：调用管理员创建老人接口
      const res: any = await api.post('/users/elder', {
        phone: elderForm.phone,
        name: elderForm.name,
        gender: elderForm.gender,
        age: elderForm.age,
        id_card: elderForm.id_card,
        address: elderForm.address,
        emergency_contact: elderForm.emergency_contact,
        emergency_phone: elderForm.emergency_phone
      })
      console.log('[Debug] 创建响应:', res)
      if (res.code === 200) {
        ElMessage.success('添加成功')
        showAddDialog.value = false
        getElderList()
      } else {
        ElMessage.error(res.message || '添加失败')
      }
    }
  } catch (error: any) {
    console.error('提交失败', error)
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('提交失败')
    }
  }
}

onMounted(() => {
  getElderList()
})
</script>