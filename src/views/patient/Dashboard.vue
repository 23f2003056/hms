<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Patient Dashboard</h1>
      <p class="page-subtitle">Hello, {{ data.patient?.full_name }}. How are you feeling today?</p>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" style="color:var(--primary)"></div>
    </div>

    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="stat-card blue">
            <div class="stat-icon blue"><i class="bi bi-calendar-check"></i></div>
            <div class="stat-number">{{ data.upcoming_appointments }}</div>
            <div class="stat-label">Upcoming Appointments</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card green">
            <div class="stat-icon green"><i class="bi bi-check-circle"></i></div>
            <div class="stat-number">{{ data.completed_appointments }}</div>
            <div class="stat-label">Completed Visits</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card gold">
            <div class="stat-icon gold"><i class="bi bi-clipboard2-pulse"></i></div>
            <div class="stat-number">{{ data.total_appointments }}</div>
            <div class="stat-label">Total Appointments</div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Departments</h2>
              <router-link to="/patient/doctors" class="btn btn-sm btn-outline-primary">Find Doctors</router-link>
            </div>
            <div class="p-3">
              <div class="row g-2">
                <div class="col-6 col-md-4" v-for="dept in data.departments" :key="dept.id">
                  <router-link
                    :to="`/patient/doctors?dept=${dept.id}`"
                    class="d-block p-3 rounded text-center text-decoration-none"
                    style="background:#f8fafc;border:1px solid var(--border);transition:all 0.2s"
                  >
                    <div style="font-size:1.5rem;margin-bottom:6px">{{ deptIcon(dept.name) }}</div>
                    <div style="font-weight:600;font-size:0.85rem;color:var(--primary)">{{ dept.name }}</div>
                    <div style="font-size:0.75rem;color:var(--text-muted)">{{ dept.doctor_count }} doctors</div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100">
            <div class="card-header">
              <h2 class="card-title">Quick Actions</h2>
            </div>
            <div class="p-4 d-flex flex-column gap-2">
              <router-link to="/patient/doctors" class="btn btn-primary text-start">
                <i class="bi bi-search-heart me-2"></i> Book Appointment
              </router-link>
              <router-link to="/patient/appointments" class="btn btn-outline-secondary text-start">
                <i class="bi bi-calendar3 me-2"></i> My Appointments
              </router-link>
              <router-link to="/patient/profile" class="btn btn-outline-secondary text-start">
                <i class="bi bi-person-circle me-2"></i> Edit Profile
              </router-link>
              <button class="btn btn-outline-success text-start" @click="exportCSV">
                <i class="bi bi-download me-2"></i> Export History CSV
              </button>
            </div>
            <div v-if="exportMsg" class="mx-4 mb-4">
              <div class="alert alert-success py-2 mb-0" style="font-size:0.85rem">{{ exportMsg }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'
const API = 'http://localhost:5000/api'

export default {
  name: 'PatientDashboard',
  components: { AppLayout },
  setup() {
    const data = ref({})
    const loading = ref(true)
    const exportMsg = ref('')

    const icons = {
      Cardiology: '🫀', Neurology: '🧠', Orthopedics: '🦴',
      'General Medicine': '🩺', Pediatrics: '👶', Dermatology: '🧬'
    }
    const deptIcon = (name) => icons[name] || '🏥'

    const exportCSV = async () => {
      try {
        const res = await axios.post(`${API}/patient/export-csv`)
        exportMsg.value = 'Export started! You will be notified when ready.'
        setTimeout(() => exportMsg.value = '', 5000)
      } catch (e) {
        exportMsg.value = 'Export triggered (Redis/Celery required for background job)'
        setTimeout(() => exportMsg.value = '', 5000)
      }
    }

    onMounted(async () => {
      try {
        const res = await axios.get(`${API}/patient/dashboard`)
        data.value = res.data
      } finally { loading.value = false }
    })
    return { data, loading, exportMsg, deptIcon, exportCSV }
  }
}
</script>
