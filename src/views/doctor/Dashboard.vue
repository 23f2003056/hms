<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Doctor Dashboard</h1>
      <p class="page-subtitle">Welcome, Dr. {{ stats.doctor?.full_name }}</p>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" style="color:var(--primary)"></div>
    </div>

    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="stat-card blue">
            <div class="stat-icon blue"><i class="bi bi-calendar-day"></i></div>
            <div class="stat-number">{{ stats.today_appointments }}</div>
            <div class="stat-label">Today's Appointments</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card gold">
            <div class="stat-icon gold"><i class="bi bi-calendar-week"></i></div>
            <div class="stat-number">{{ stats.week_appointments }}</div>
            <div class="stat-label">This Week</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card green">
            <div class="stat-icon green"><i class="bi bi-people"></i></div>
            <div class="stat-number">{{ stats.total_patients }}</div>
            <div class="stat-label">Total Patients</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Today's Appointments</h2>
          <router-link to="/doctor/appointments" class="btn btn-sm btn-outline-primary">View All</router-link>
        </div>
        <div class="table-wrapper">
          <table class="hms-table">
            <thead><tr><th>Patient</th><th>Time</th><th>Reason</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="a in todayApts" :key="a.id">
                <td>{{ a.patient_name }}</td>
                <td>{{ a.time }}</td>
                <td>{{ a.reason || '—' }}</td>
                <td><span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
              </tr>
              <tr v-if="!todayApts.length">
                <td colspan="4">
                  <div class="empty-state"><i class="bi bi-calendar-check d-block"></i><p>No appointments today</p></div>
                </td>
              </tr>
            </tbody>
          </table>
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
  name: 'DoctorDashboard',
  components: { AppLayout },
  setup() {
    const stats = ref({ doctor: {} })
    const todayApts = ref([])
    const loading = ref(true)

    onMounted(async () => {
      try {
        const [s, a] = await Promise.all([
          axios.get(`${API}/doctor/dashboard`),
          axios.get(`${API}/doctor/appointments`, { params: { filter: 'today' } })
        ])
        stats.value = s.data
        todayApts.value = a.data
      } finally { loading.value = false }
    })
    return { stats, todayApts, loading }
  }
}
</script>
