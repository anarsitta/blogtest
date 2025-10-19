<template>
  <el-dialog
    :model-value="visible"
    :title="isLogin ? 'Авторизация' : 'Регистрация'"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="isLogin ? {} : rules" label-position="top" @submit.prevent="handleSubmit" class="auth-form-centered">
      <el-form-item label="Email" prop="email">
        <el-input v-model="form.email" autocomplete="username" :prefix-icon="Message" type="message" placeholder="Email" />
      </el-form-item>
      <el-form-item v-if="!isLogin" label="Логин" prop="username">
        <el-input v-model="form.username" autocomplete="username" :prefix-icon="User" placeholder="Логин" />
      </el-form-item>
      <el-form-item label="Пароль" prop="password">
        <el-input v-model="form.password" type="password" autocomplete="current-password" :prefix-icon="Lock" placeholder="Пароль" show-password />
      </el-form-item>
      <el-form-item v-if="!isLogin" label="Подтвердите пароль" prop="password_confirm">
        <el-input v-model="form.password_confirm" type="password" autocomplete="new-password" :prefix-icon="Lock" placeholder="Подтвердите пароль" show-password />
      </el-form-item>
      <el-form-item>
        <el-row justify="center" gutter="12">
          <el-col :span="24">
            <el-button type="primary" @click="handleSubmit" :loading="loading" class="auth-main-btn">
              <template #icon>
                <el-icon><i class="el-icon-unlock" /></el-icon>
              </template>
              {{ isLogin ? 'Войти' : 'Зарегистрироваться' }}
            </el-button>
          </el-col>
          <el-col :span="24">
            <el-button type="text" @click="toggleMode" class="auth-switch-btn">
              {{ isLogin ? 'Нет аккаунта? Зарегистрироваться' : 'Уже есть аккаунт? Войти' }}
            </el-button>
          </el-col>
        </el-row>
      </el-form-item>
      <div class="error-block">
        <el-alert v-if="error" :title="error" type="error" show-icon class="auth-error-alert" />
      </div>
    </el-form>
    <div class="auth-footer">
      <el-divider />
      <div class="auth-footer-text">
        <el-icon class="auth-footer-icon"><i class="el-icon-user-solid" /></el-icon>
        <span>BlogTest — современная система управления пользователями и блогами</span>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAuthStore } from '../../store/auth.js'
import { Lock } from '@element-plus/icons-vue'

const visible  = defineModel('visible')
const emit = defineEmits(['close', 'success'])

const isLogin = ref(true)
const form = ref({
  email: '',
  password: '',
  username: '',
  password_confirm: ''
})
const loading = ref(false)
const error = ref(null)
const auth = useAuthStore()

// rules для валидации
const rules = {
  email: [
    { required: true, message: 'Введите email', trigger: 'blur' },
    { type: 'email', message: 'Некорректный email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Введите пароль', trigger: 'blur' },
    { min: 6, message: 'Минимум 6 символов', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: 'Подтвердите пароль', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (value !== form.value.password) {
        callback(new Error('Пароли не совпадают'))
      } else {
        callback()
      }
    }, trigger: 'blur' }
  ],
  username: [
    { required: true, message: 'Введите имя пользователя', trigger: 'blur' }
  ],
}

const formRef = ref()

watch(() => visible.value, (val) => {
  if (!val) resetForm()
  isLogin.value = true
})

function resetForm() {
  error.value = null
  loading.value = false
  formRef.value?.resetFields()
  formRef.value?.clearValidate()
}

function handleClose() {
  resetForm()
  visible.value = false
}

function toggleMode() {
  isLogin.value = !isLogin.value
  resetForm()
}


async function handleSubmit() {
  error.value = null
  loading.value = true
  if (!isLogin.value) {
    try {
      await formRef.value.validate()
    } catch (e) {
      error.value = e?.fields ? Object.values(e.fields).map(arr => arr[0].message).join(', ') : 'Проверьте форму'
      loading.value = false
      return
    }
  }
  try {
    if (isLogin.value) {
      await auth.login(form.value.email, form.value.password)
      handleClose()
    } else {
      await auth.register(form.value)
      isLogin.value = true
    }
    resetForm()
  } catch (e) {
    error.value = e.message || 'Ошибка'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.el-dialog__header {
  padding-bottom: 6px;
}
.el-form-item__content {
  justify-content: center;
}
.el-divider--horizontal {
  margin: 10px 0;
}
.el-form-item--label-top .el-form-item__label {
  margin-bottom: 2px;
}
.error-block {
  min-height: 28px;
  margin-top: 12px;
}
.auth-form-centered {
  max-width: 340px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 12px 18px 0 18px;
  box-shadow: 0 2px 16px #409eff22;
}
.auth-col {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.el-form {
  padding-top: 18px;
  padding-bottom: 8px;
}
.el-form-item {
  margin-bottom: 18px;
}
.auth-footer {
  margin-top: 18px;
  text-align: center;
}
.auth-footer-text {
  font-size: 1.08rem;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.auth-main-btn {
  width: 100%;
  margin-bottom: 8px;
  margin-top: 10px;
}
.auth-switch-btn {
  width: 100%;
}
.auth-error-alert {
  border-radius: 8px;
}
.auth-footer-icon {
  vertical-align: middle;
  color: #409EFF;
  margin-right: 6px;
}
</style>