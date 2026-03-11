<template>
  <div class="login-page">
    <div class="login-card" style="max-width:520px">
      <div class="login-logo">
        <div class="login-logo-icon"><i class="bi bi-person-plus"></i></div>
        <h1>Register</h1>
        <p>Create your patient account</p>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <form @submit.prevent="handleRegister">
        <div class="row g-3">
          <div class="col-6">
            <label class="form-label">Username *</label>
            <input v-model="form.username" type="text" class="form-control" required />
          </div>
          <div class="col-6">
            <label class="form-label">Full Name *</label>
            <input v-model="form.full_name" type="text" class="form-control" required />
          </div>
          <div class="col-12">
            <label class="form-label">Email *</label>
            <input v-model="form.email" type="email" class="form-control" required />
          </div>
          <div class="col-6">
            <label class="form-label">Password *</label>
            <input v-model="form.password" type="password" class="form-control" required minlength="6" />
          </div>
          <div class="col-6">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" type="text" class="form-control" />
          </div>
          <div class="col-6">
            <label class="form-label">Gender</label>
            <select v-model="form.gender" class="form-select">
              <option value="">Select</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>
          <div class="col-6">
            <label class="form-label">Blood Group</label>
            <select v-model="form.blood_group" class="form-select">
              <option value="">Select</option>
              <option v-for="bg in bloodGroups" :key="bg">{{ bg }}</option>
            </select>
          </div>
        </div>

        <button type="submit" class="btn btn-primary w-100 py-2 mt-4" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Create Account
        </button>
      </form>

      <p class="text-center mt-3 mb-0" style="font-size:0.9rem;color:#6b7c93">
        Already have an account?
        <router-link to="/login" style="color:var(--primary-light);font-weight:600">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'RegisterView',
  setup() {
    const store = useStore()
    const router = useRouter()
    const form = ref({
      username: '', full_name: '', email: '', password: '',
      phone: '', gender: '', blood_group: ''
    })
    const loading = ref(false)
    const error = ref(null)
    const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    const handleRegister = async () => {
      loading.value = true
      error.value = null
      try {
        await store.dispatch('register', form.value)
        router.push('/patient/dashboard')
      } catch (e) {
        error.value = e.response?.data?.error || 'Registration failed'
      } finally {
        loading.value = false
      }
    }
    return { form, loading, error, bloodGroups, handleRegister }
  }
}
</script>
