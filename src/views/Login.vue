<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <div class="login-logo-icon"><i class="bi bi-hospital"></i></div>
        <h1>MediCare</h1>
        <p>Hospital Management System</p>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label">Username</label>
          <input v-model="form.username" type="text" class="form-control" placeholder="Enter username" required />
        </div>
        <div class="mb-4">
          <label class="form-label">Password</label>
          <input v-model="form.password" type="password" class="form-control" placeholder="Enter password" required />
        </div>
        <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Sign In
        </button>
      </form>

      <hr class="my-4" />
      <p class="text-center mb-0" style="font-size:0.9rem;color:#6b7c93">
        New patient?
        <router-link to="/register" style="color:var(--primary-light);font-weight:600">Register here</router-link>
      </p>

      <div class="mt-4 p-3 rounded" style="background:#f8fafc;font-size:0.8rem;color:#6b7c93">
        <strong>Demo Credentials:</strong><br>
        Admin: <code>admin / admin123</code>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const form = ref({ username: '', password: '' })
    const loading = ref(false)
    const error = ref(null)

    const handleLogin = async () => {
      loading.value = true
      error.value = null
      try {
        const role = await store.dispatch('login', form.value)
        router.push(`/${role}/dashboard`)
      } catch (e) {
        error.value = e.response?.data?.error || 'Login failed'
      } finally {
        loading.value = false
      }
    }
    return { form, loading, error, handleLogin }
  }
}
</script>
