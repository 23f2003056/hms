<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Appointments</h1>
    </div>

    <div v-if="alert.msg" :class="`alert alert-${alert.type}`">{{ alert.msg }}</div>

    <ul class="nav nav-tabs mb-4">
      <li class="nav-item" v-for="tab in tabs" :key="tab.value">
        <button class="nav-link" :class="{ active: filter === tab.value }" @click="setFilter(tab.value)">{{ tab.label }}</button>
      </li>
    </ul>

    <div class="card">
      <div class="table-wrapper">
        <table class="hms-table">
          <thead><tr><th>Patient</th><th>Date</th><th>Time</th><th>Reason</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.id">
              <td>{{ a.patient_name }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>{{ a.reason || '—' }}</td>
              <td><span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
              <td>
                <button v-if="a.status === 'Booked'" class="btn btn-sm btn-success me-1" @click="openComplete(a)">
                  <i class="bi bi-check2"></i> Complete
                </button>
                <button v-if="a.status === 'Booked'" class="btn btn-sm btn-outline-danger" @click="cancelApt(a)">
                  <i class="bi bi-x"></i>
                </button>
                <button v-if="a.treatment" class="btn btn-sm btn-outline-info" @click="viewTreatment(a)">
                  <i class="bi bi-file-medical"></i>
                </button>
              </td>
            </tr>
            <tr v-if="!appointments.length">
              <td colspan="6">
                <div class="empty-state"><i class="bi bi-calendar3 d-block"></i><p>No appointments</p></div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Complete Modal -->
    <div v-if="showComplete" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">Complete Appointment — {{ selected?.patient_name }}</h5>
            <button class="btn-close" @click="showComplete=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12">
                <label class="form-label">Diagnosis *</label>
                <textarea v-model="treatForm.diagnosis" class="form-control" rows="3" placeholder="Enter diagnosis..."></textarea>
              </div>
              <div class="col-12">
                <label class="form-label">Prescription</label>
                <textarea v-model="treatForm.prescription" class="form-control" rows="3" placeholder="Medications, dosage..."></textarea>
              </div>
              <div class="col-12">
                <label class="form-label">Doctor Notes</label>
                <textarea v-model="treatForm.notes" class="form-control" rows="2" placeholder="Additional notes..."></textarea>
              </div>
              <div class="col-6">
                <label class="form-label">Next Visit Date</label>
                <input v-model="treatForm.next_visit" type="date" class="form-control" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showComplete=false">Cancel</button>
            <button class="btn btn-success" @click="completeApt" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Treatment View Modal -->
    <div v-if="showTreatment" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">Treatment Record</h5>
            <button class="btn-close" @click="showTreatment=false"></button>
          </div>
          <div class="modal-body" v-if="selected?.treatment">
            <div class="mb-3"><strong>Diagnosis:</strong><p class="mt-1 p-3 rounded" style="background:#f8fafc">{{ selected.treatment.diagnosis }}</p></div>
            <div class="mb-3"><strong>Prescription:</strong><p class="mt-1 p-3 rounded" style="background:#f8fafc">{{ selected.treatment.prescription }}</p></div>
            <div class="mb-3" v-if="selected.treatment.notes"><strong>Notes:</strong><p class="mt-1 p-3 rounded" style="background:#f8fafc">{{ selected.treatment.notes }}</p></div>
            <div v-if="selected.treatment.next_visit"><strong>Next Visit:</strong> {{ selected.treatment.next_visit }}</div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showTreatment=false">Close</button>
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
  name: 'DoctorAppointments',
  components: { AppLayout },
  setup() {
    const appointments = ref([])
    const filter = ref('upcoming')
    const showComplete = ref(false)
    const showTreatment = ref(false)
    const selected = ref(null)
    const saving = ref(false)
    const alert = ref({ msg: '', type: 'success' })
    const treatForm = ref({ diagnosis: '', prescription: '', notes: '', next_visit: '' })
    const tabs = [
      { value: 'today', label: 'Today' },
      { value: 'upcoming', label: 'Upcoming' },
      { value: 'past', label: 'Past' },
      { value: '', label: 'All' }
    ]

    const load = async () => {
      const res = await axios.get(`${API}/doctor/appointments`, { params: { filter: filter.value } })
      appointments.value = res.data
    }

    const setFilter = (f) => { filter.value = f; load() }

    const openComplete = (a) => {
      selected.value = a
      treatForm.value = { diagnosis: '', prescription: '', notes: '', next_visit: '' }
      showComplete.value = true
    }

    const completeApt = async () => {
      if (!treatForm.value.diagnosis) return alert.value = { msg: 'Diagnosis is required', type: 'danger' }
      saving.value = true
      try {
        await axios.post(`${API}/doctor/appointments/${selected.value.id}/complete`, treatForm.value)
        alert.value = { msg: 'Appointment completed!', type: 'success' }
        showComplete.value = false
        await load()
      } finally {
        saving.value = false
        setTimeout(() => alert.value.msg = '', 3000)
      }
    }

    const cancelApt = async (a) => {
      if (!confirm('Cancel this appointment?')) return
      await axios.post(`${API}/doctor/appointments/${a.id}/cancel`)
      await load()
    }

    const viewTreatment = (a) => { selected.value = a; showTreatment.value = true }

    onMounted(load)
    return { appointments, filter, tabs, showComplete, showTreatment, selected, treatForm, saving, alert, setFilter, openComplete, completeApt, cancelApt, viewTreatment }
  }
}
</script>
