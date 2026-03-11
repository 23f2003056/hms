<template>
  <AppLayout>
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h1 class="page-title">My Availability</h1>
        <p class="page-subtitle">Set available slots for the next 7 days</p>
      </div>
      <button class="btn btn-primary" @click="showModal=true">
        <i class="bi bi-plus-lg me-2"></i>Add Slot
      </button>
    </div>

    <div v-if="alert.msg" :class="`alert alert-${alert.type}`">{{ alert.msg }}</div>

    <div class="card">
      <div class="table-wrapper">
        <table class="hms-table">
          <thead><tr><th>Date</th><th>Start Time</th><th>End Time</th><th>Max Appointments</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="a in availabilities" :key="a.id">
              <td>{{ a.date }}</td>
              <td>{{ a.start_time }}</td>
              <td>{{ a.end_time }}</td>
              <td>{{ a.max_appointments }}</td>
              <td>
                <button class="btn btn-sm btn-outline-danger" @click="deleteSlot(a)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="!availabilities.length">
              <td colspan="5">
                <div class="empty-state"><i class="bi bi-clock d-block"></i><p>No availability set for the next 7 days</p></div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Modal -->
    <div v-if="showModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">Add Availability Slot</h5>
            <button class="btn-close" @click="showModal=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12">
                <label class="form-label">Date *</label>
                <input v-model="form.date" type="date" class="form-control" :min="minDate" :max="maxDate" required />
              </div>
              <div class="col-6">
                <label class="form-label">Start Time</label>
                <input v-model="form.start_time" type="time" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label">End Time</label>
                <input v-model="form.end_time" type="time" class="form-control" />
              </div>
              <div class="col-12">
                <label class="form-label">Max Appointments</label>
                <input v-model.number="form.max_appointments" type="number" class="form-control" min="1" max="30" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="saveSlot" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>Save
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
import AppLayout from '../../components/AppLayout.vue'
const API = 'http://localhost:5000/api'

export default {
  name: 'DoctorAvailability',
  components: { AppLayout },
  setup() {
    const availabilities = ref([])
    const showModal = ref(false)
    const saving = ref(false)
    const alert = ref({ msg: '', type: 'success' })
    const form = ref({ date: '', start_time: '09:00', end_time: '17:00', max_appointments: 10 })

    const today = new Date()
    const minDate = today.toISOString().split('T')[0]
    const maxDate = new Date(today.getTime() + 7 * 86400000).toISOString().split('T')[0]

    const load = async () => {
      const res = await axios.get(`${API}/doctor/availability`)
      availabilities.value = res.data
    }

    const saveSlot = async () => {
      if (!form.value.date) return
      saving.value = true
      try {
        await axios.post(`${API}/doctor/availability`, form.value)
        alert.value = { msg: 'Availability saved!', type: 'success' }
        showModal.value = false
        await load()
      } catch (e) {
        alert.value = { msg: e.response?.data?.error || 'Error', type: 'danger' }
      } finally {
        saving.value = false
        setTimeout(() => alert.value.msg = '', 3000)
      }
    }

    const deleteSlot = async (a) => {
      if (!confirm('Delete this slot?')) return
      await axios.delete(`${API}/doctor/availability/${a.id}`)
      await load()
    }

    onMounted(load)
    return { availabilities, showModal, form, saving, alert, minDate, maxDate, saveSlot, deleteSlot }
  }
}
</script>
