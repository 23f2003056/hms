<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">My Profile</h1>
      <p class="page-subtitle">Manage your personal information</p>
    </div>

    <div v-if="alert.msg" :class="`alert alert-${alert.type}`">{{ alert.msg }}</div>

    <div class="row g-4">
      <div class="col-md-4">
        <div class="card text-center p-4">
          <div class="user-avatar mx-auto mb-3" style="width:72px;height:72px;font-size:1.5rem;border-radius:50%;background:var(--primary);display:flex;align-items:center;justify-content:center;color:white">
            {{ initials }}
          </div>
          <h3 style="font-size:1.2rem;font-weight:700;color:var(--primary)">{{ form.full_name }}</h3>
          <p style="color:var(--text-muted);font-size:0.85rem">{{ user?.email }}</p>
          <span class="badge-status badge-completed">Patient</span>
          <hr />
          <div class="text-start" style="font-size:0.85rem">
            <div class="mb-2"><strong>Blood Group:</strong> {{ form.blood_group || '—' }}</div>
            <div class="mb-2"><strong>Gender:</strong> {{ form.gender || '—' }}</div>
            <div class="mb-2"><strong>Phone:</strong> {{ form.phone || '—' }}</div>
            <div><strong>Emergency:</strong> {{ form.emergency_contact || '—' }}</div>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Edit Profile</h2>
          </div>
          <div class="p-4">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Full Name</label>
                <input v-model="form.full_name" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Date of Birth</label>
                <input v-model="form.date_of_birth" type="date" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Gender</label>
                <select v-model="form.gender" class="form-select">
                  <option value="">Select</option>
                  <option>Male</option><option>Female</option><option>Other</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Blood Group</label>
                <select v-model="form.blood_group" class="form-select">
                  <option value="">Select</option>
                  <option v-for="bg in bloodGroups" :key="bg">{{ bg }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Emergency Contact</label>
                <input v-model="form.emergency_contact" class="form-control" />
              </div>
              <div class="col-12">
                <label class="form-label">Address</label>
                <textarea v-model="form.address" class="form-control" rows="2"></textarea>
              </div>
            </div>
            <button class="btn btn-primary mt-4 px-4" @click="save" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useStore } from 'vuex'
import AppLayout from '../../components/AppLayout.vue'
const API = 'http://localhost:5000/api'

export default {
  name: 'PatientProfile',
  components: { AppLayout },
  setup() {
    const store = useStore()
    const user = computed(() => store.state.user)
    const form = ref({
      full_name: '', phone: '', date_of_birth: '', gender: '',
      blood_group: '', emergency_contact: '', address: ''
    })
    const saving = ref(false)
    const alert = ref({ msg: '', type: 'success' })
    const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    const initials = computed(() => form.value.full_name.slice(0, 2).toUpperCase())

    const save = async () => {
      saving.value = true
      try {
        await axios.put(`${API}/patient/profile`, form.value)
        alert.value = { msg: 'Profile updated successfully!', type: 'success' }
      } catch (e) {
        alert.value = { msg: 'Update failed', type: 'danger' }
      } finally {
        saving.value = false
        setTimeout(() => alert.value.msg = '', 3000)
      }
    }

    onMounted(async () => {
      const res = await axios.get(`${API}/auth/me`)
      if (res.data.profile) Object.assign(form.value, res.data.profile)
    })

    return { user, form, saving, alert, bloodGroups, initials, save }
  }
}
</script>
