<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Welcome back, Admin. Here's today's overview.</p>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" style="color:var(--primary)"></div>
    </div>

    <div v-else>
      <div class="row g-3 mb-4">
        <div class="col-md-3">
          <div class="stat-card blue">
            <div class="stat-icon blue"><i class="bi bi-person-badge"></i></div>
            <div class="stat-number">{{ stats.total_doctors }}</div>
            <div class="stat-label">Total Doctors</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card gold">
            <div class="stat-icon gold"><i class="bi bi-people"></i></div>
            <div class="stat-number">{{ stats.total_patients }}</div>
            <div class="stat-label">Total Patients</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card green">
            <div class="stat-icon green"><i class="bi bi-calendar-check"></i></div>
            <div class="stat-number">{{ stats.completed }}</div>
            <div class="stat-label">Completed</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card red">
            <div class="stat-icon red"><i class="bi bi-calendar3"></i></div>
            <div class="stat-number">{{ stats.booked }}</div>
            <div class="stat-label">Upcoming</div>
          </div>
        </div>
      </div>

      <div class="row g-3">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Appointment Summary</h2>
            </div>
            <div class="p-4">
              <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border)">
                <span>Total Appointments</span>
                <strong>{{ stats.total_appointments }}</strong>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border)">
                <span>Booked</span>
                <span class="badge-status badge-booked">{{ stats.booked }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-3 pb-3" style="border-bottom:1px solid var(--border)">
                <span>Completed</span>
                <span class="badge-status badge-completed">{{ stats.completed }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <span>Cancelled</span>
                <span class="badge-status badge-cancelled">{{ stats.cancelled }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              <h2 class="card-title">Quick Actions</h2>
            </div>
            <div class="p-4 d-flex flex-column gap-2">
              <router-link to="/admin/doctors" class="btn btn-outline-primary text-start">
                <i class="bi bi-person-plus me-2"></i> Add New Doctor
              </router-link>
              <router-link to="/admin/patients" class="btn btn-outline-secondary text-start">
                <i class="bi bi-people me-2"></i> View All Patients
              </router-link>
              <router-link to="/admin/appointments" class="btn btn-outline-success text-start">
                <i class="bi bi-calendar3 me-2"></i> View All Appointments
              </router-link>
              <router-link to="/admin/search" class="btn btn-outline-info text-start">
                <i class="bi bi-search me-2"></i> Search Records
              </router-link>
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

export default {
  name: 'AdminDashboard',
  components: { AppLayout },
  setup() {
    const stats = ref({})
    const loading = ref(true)

    onMounted(async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/admin/dashboard')
        stats.value = res.data
      } catch (e) { console.error(e) }
      finally { loading.value = false }
    })

    return { stats, loading }
  }
}
</script>
