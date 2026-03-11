<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">My Appointments</h1>
      <p class="page-subtitle">View and manage your appointments</p>
    </div>

    <div v-if="alert.msg" :class="`alert alert-${alert.type}`">{{ alert.msg }}</div>

    <ul class="nav nav-tabs mb-4">
      <li class="nav-item" v-for="tab in tabs" :key="tab.value">
        <button class="nav-link" :class="{ active: filter === tab.value }" @click="setFilter(tab.value)">{{ tab.label }}</button>
      </li>
    </ul>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" style="color:var(--primary)"></div>
    </div>

    <div v-else class="card">
      <div class="table-wrapper">
        <table class="hms-table">
          <thead><tr><th>Doctor</th><th>Specialization</th><th>Date</th><th>Time</th><th>Status</th><th>Diagnosis</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.id">
              <td>Dr. {{ a.doctor_name }}</td>
              <td>{{ a.specialization }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td><span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
              <td>{{ a.treatment?.diagnosis || '—' }}</td>
              <td>
                <button v-if="a.status === 'Booked'" class="btn btn-sm btn-outline-warning me-1" @click="openReschedule(a)">
                  <i class="bi bi-calendar-event"></i>
                </button>
                <button v-if="a.status === 'Booked'" class="btn btn-sm btn-outline-danger" @click="cancelApt(a)">
                  <i class="bi bi-x-circle"></i>
                </button>
                <button v-if="a.treatment" class="btn btn-sm btn-outline-info" @click="viewDetails(a)">
                  <i class="bi bi-file-medical"></i>
                </button>
              </td>
            </tr>
            <tr v-if="!appointments.length">
              <td colspan="7">
                <div class="empty-state"><i class="bi bi-calendar3 d-block"></i><p>No appointments found</p></div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div v-if="showReschedule" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">Reschedule Appointment</h5>
            <button class="btn-close" @click="showReschedule=false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">New Date</label>
              <input v-model="reschedForm.date" type="date" class="form-control" :min="minDate" :max="maxDate" />
            </div>
            <div class="mb-3">
              <label class="form-label">New Time</label>
              <select v-model="reschedForm.time" class="form-select">
                <option v-for="t in timeSlots" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showReschedule=false">Cancel</button>
            <button class="btn btn-warning" @click="confirmReschedule" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>Reschedule
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="showDetails" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details — {{ selected?.date }}</h5>
            <button class="btn-close" @click="showDetails=false"></button>
          </div>
          <div class="modal-body" v-if="selected">
            <div class="mb-3 p-3 rounded" style="background:#f8fafc">
              <div><strong>Doctor:</strong> Dr. {{ selected.doctor_name }}</div>
              <div><strong>Specialization:</strong> {{ selected.specialization }}</div>
              <div><strong>Date & Time:</strong> {{ selected.date }} at {{ selected.time }}</div>
            </div>
            <div v-if="selected.treatment">
              <div class="mb-3">
                <strong>Diagnosis</strong>
                <p class="p-3 rounded mt-1" style="background:#f8fafc">{{ selected.treatment.diagnosis }}</p>
              </div>
              <div class="mb-3">
                <strong>Prescription</strong>
                <p class="p-3 rounded mt-1" style="background:#f8fafc">{{ selected.treatment.prescription || '—' }}</p>
              </div>
              <div v-if="selected.treatment.notes" class="mb-3">
                <strong>Notes</strong>
                <p class="p-3 rounded mt-1" style="background:#f8fafc">{{ selected.treatment.notes }}</p>
              </div>
              <div v-if="selected.treatment.next_visit">
                <strong>Next Visit:</strong> {{ selected.treatment.next_visit }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showDetails=false">Close</button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'
const API = 'http://localhost:5000/api'

export default {
  name: 'PatientAppointments',
  components: { AppLayout },
  setup() {
    const appointments = ref([])
    const filter = ref('upcoming')
    const loading = ref(false)
    const showReschedule = ref(false)
    const showDetails = ref(false)
    const selected = ref(null)
    const saving = ref(false)
    const alert = ref({ msg: '', type: 'success' })
    const reschedForm = ref({ date: '', time: '' })

    const tabs = [
      { value: 'upcoming', label: 'Upcoming' },
      { value: 'past', label: 'Past' },
      { value: 'all', label: 'All' }
    ]

    const today = new Date()
    const minDate = today.toISOString().split('T')[0]
    const maxDate = new Date(today.getTime() + 7 * 86400000).toISOString().split('T')[0]
    const timeSlots = computed(() => {
      const slots = []
      for (let h = 8; h <= 19; h++) {
        slots.push(`${String(h).padStart(2,'0')}:00`)
        slots.push(`${String(h).padStart(2,'0')}:30`)
      }
      return slots
    })

    const load = async () => {
      loading.value = true
      try {
        const res = await axios.get(`${API}/patient/appointments`, { params: { filter: filter.value } })
        appointments.value = res.data
      } finally { loading.value = false }
    }

    const setFilter = (f) => { filter.value = f; load() }

    const openReschedule = (a) => {
      selected.value = a
      reschedForm.value = { date: a.date, time: a.time }
      showReschedule.value = true
    }

    const confirmReschedule = async () => {
      saving.value = true
      try {
        await axios.put(`${API}/patient/appointments/${selected.value.id}`, reschedForm.value)
        alert.value = { msg: 'Appointment rescheduled!', type: 'success' }
        showReschedule.value = false
        await load()
      } catch (e) {
        alert.value = { msg: e.response?.data?.error || 'Error', type: 'danger' }
      } finally {
        saving.value = false
        setTimeout(() => alert.value.msg = '', 3000)
      }
    }

    const cancelApt = async (a) => {
      if (!confirm('Cancel this appointment?')) return
      try {
        await axios.post(`${API}/patient/appointments/${a.id}/cancel`)
        alert.value = { msg: 'Appointment cancelled', type: 'success' }
        await load()
      } finally { setTimeout(() => alert.value.msg = '', 3000) }
    }

    const viewDetails = (a) => { selected.value = a; showDetails.value = true }

    onMounted(load)
    return {
      appointments, filter, loading, tabs, showReschedule, showDetails,
      selected, saving, alert, reschedForm, minDate, maxDate, timeSlots,
      setFilter, openReschedule, confirmReschedule, cancelApt, viewDetails
    }
  }
}
</script>
