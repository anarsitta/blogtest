<!-- ChangePasswordModal.vue -->
<template>
  <el-dialog
    :model-value="visible"
    title="Смена пароля"
    width="400px"
    :before-close="handleClose"
  >
    <el-form 
      :model="form" 
      label-position="top"
      :rules="rules"
      ref="formRef"
    >
      <el-form-item label="Старый пароль" prop="old_password">
        <el-input 
          type="password" 
          v-model="form.old_password" 
          show-password
          placeholder="Введите старый пароль"
        />
      </el-form-item>
      <el-form-item label="Новый пароль" prop="new_password">
        <el-input 
          type="password" 
          v-model="form.new_password" 
          show-password
          placeholder="Введите новый пароль"
        />
      </el-form-item>
      <el-form-item label="Подтвердите пароль" prop="confirm_password">
        <el-input 
          type="password" 
          v-model="form.confirm_password" 
          show-password
          placeholder="Повторите новый пароль"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">Отмена</el-button>
      <el-button 
        type="primary" 
        @click="handleConfirm" 
        :loading="loading"
      >
        Сменить пароль
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:visible', 'confirm'])

const loading = ref(false)
const formRef = ref()

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.new_password) {
    callback(new Error('Пароли не совпадают'))
  } else {
    callback()
  }
}

const rules = {
  old_password: [
    { required: true, message: 'Введите старый пароль', trigger: 'blur' },
    { min: 6, message: 'Пароль должен быть не менее 6 символов', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: 'Введите новый пароль', trigger: 'blur' },
    { min: 6, message: 'Пароль должен быть не менее 6 символов', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: 'Подтвердите новый пароль', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const resetForm = () => {
  form.old_password = ''
  form.new_password = ''
  form.confirm_password = ''
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const handleClose = () => {
  resetForm()
  emit('update:visible', false)
}

const handleConfirm = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (valid) {
      loading.value = true
      emit('confirm', {
        old_password: form.old_password,
        new_password: form.new_password
      })
    }
  } catch (error) {
    // Валидация не прошла
    console.log('Validation failed:', error)
  } finally {
    loading.value = false
  }
}
</script>