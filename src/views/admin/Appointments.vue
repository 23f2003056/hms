<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Appointments</h1>
      <p class="page-subtitle">View and manage all hospital appointments</p>
    </div>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">All Appointments</h2>
        <select v-model="filterStatus" class="form-select w-auto">
          <option value="">All Status</option>
          <option>Booked</option><option>Completed</option><option>Cancelled</option>
        </select>
      </div>
      <div class="table-wrapper">
        <table class="hms-table">
          <thead>
            <tr><th>Patient</th><th>Doctor</th><th>Specialization</th><th>Date</th><th>Time</th><th>Status</th><th>Reason</th></tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>{{ a.patient_name }}</td>
              <td>{{ a.doctor_name }}</td>
              <td>{{ a.specialization }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>
                <span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span>
              </td>
              <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis">{{ a.reason || '—' }}</td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7">
                <div class="empty-state"><i class="bi bi-calendar3 d-block"></i><p>No appointments</p></div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'

export default {
  name: 'AdminAppointments',
  components: { AppLayout },
  setup() {
    const appointments = ref([])
    const filterStatus = ref('')

    const filtered = computed(() => {
      if (!filterStatus.value) return appointments.value
      return appointments.value.filter(a => a.status === filterStatus.value)
    })

    onMounted(async () => {
      const res = await axios.get('http://localhost:5000/api/admin/appointments')
      appointments.value = res.data
    })

    return { appointments, filterStatus, filtered }
  }
}
</script>
