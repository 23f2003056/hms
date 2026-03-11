<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Find Doctors</h1>
      <p class="page-subtitle">Search and book appointments with our specialists</p>
    </div>

    <div v-if="alert.msg" :class="`alert alert-${alert.type}`">{{ alert.msg }}</div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="p-4">
        <div class="row g-3">
          <div class="col-md-6">
            <input v-model="search" type="text" class="form-control" placeholder="Search by name or specialization..." @input="load" />
          </div>
          <div class="col-md-6">
            <select v-model="deptFilter" class="form-select" @change="load">
              <option value="">All Departments</option>
              <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" style="color:var(--primary)"></div>
    </div>

    <div class="row g-3" v-else>
      <div class="col-md-4" v-for="doc in doctors" :key="doc.id">
        <div class="doctor-card" @click="selectDoctor(doc)">
          <div class="doctor-avatar"><i class="bi bi-person-badge"></i></div>
          <h3 style="font-size:1rem;font-weight:700;color:var(--primary);margin:0 0 4px">{{ doc.full_name }}</h3>
          <div style="color:var(--primary-light);font-size:0.85rem;font-weight:500;margin-bottom:8px">{{ doc.specialization }}</div>
          <div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:12px">
            <span class="me-3"><i class="bi bi-building me-1"></i>{{ doc.department || 'General' }}</span>
            <span><i class="bi bi-briefcase me-1"></i>{{ doc.experience_years }} yrs exp</span>
          </div>
          <p v-if="doc.bio" style="font-size:0.82rem;color:var(--text-muted);margin-bottom:12px;line-height:1.5">{{ doc.bio.slice(0,80) }}{{ doc.bio.length > 80 ? '...' : '' }}</p>
          <button class="btn btn-primary btn-sm w-100">
            <i class="bi bi-calendar-plus me-1"></i> Book Appointment
          </button>
        </div>
      </div>
      <div v-if="!doctors.length" class="col-12">
        <div class="empty-state"><i class="bi bi-person-badge d-block"></i><p>No doctors found</p></div>
      </div>
    </div>

    <!-- Book Appointment Modal -->
    <div v-if="showBook" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">Book Appointment — Dr. {{ selectedDoc?.full_name }}</h5>
            <button class="btn-close" @click="showBook=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Date *</label>
                <input v-model="bookForm.date" type="date" class="form-control" :min="minDate" :max="maxDate" required @change="loadAvailability" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Time *</label>
                <select v-model="bookForm.time" class="form-select" required>
                  <option value="">-- Select time --</option>
                  <option v-for="t in timeSlots" :key="t" :value="t">{{ t }}</option>
                </select>
                <div v-if="availability.length" style="font-size:0.8rem;color:var(--success);margin-top:4px">
                  <i class="bi bi-check-circle me-1"></i>Doctor available {{ availability[0]?.start_time }} – {{ availability[0]?.end_time }}
                </div>
              </div>
              <div class="col-12">
                <label class="form-label">Reason for Visit</label>
                <textarea v-model="bookForm.reason" class="form-control" rows="3" placeholder="Briefly describe your symptoms or reason..."></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showBook=false">Cancel</button>
            <button class="btn btn-primary" @click="confirmBook" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              Confirm Booking
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import AppLayout from '../../components/AppLayout.vue'
const API = 'http://localhost:5000/api'

export default {
  name: 'PatientDoctors',
  components: { AppLayout },
  setup() {
    const route = useRoute()
    const doctors = ref([])
    const departments = ref([])
    const search = ref('')
    const deptFilter = ref(route.query.dept || '')
    const loading = ref(false)
    const showBook = ref(false)
    const selectedDoc = ref(null)
    const availability = ref([])
    const saving = ref(false)
    const alert = ref({ msg: '', type: 'success' })
    const bookForm = ref({ date: '', time: '', reason: '' })

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
        const res = await axios.get(`${API}/patient/doctors`, {
          params: { q: search.value, department_id: deptFilter.value }
        })
        doctors.value = res.data
      } finally { loading.value = false }
    }

    const loadAvailability = async () => {
      if (!selectedDoc.value || !bookForm.value.date) return
      const res = await axios.get(`${API}/patient/doctors/${selectedDoc.value.id}/availability`)
      availability.value = res.data.filter(a => a.date === bookForm.value.date)
    }

    const selectDoctor = (doc) => {
      selectedDoc.value = doc
      bookForm.value = { date: '', time: '', reason: '' }
      availability.value = []
      showBook.value = true
    }

    const confirmBook = async () => {
      if (!bookForm.value.date || !bookForm.value.time) {
        return alert.value = { msg: 'Please select date and time', type: 'danger' }
      }
      saving.value = true
      try {
        await axios.post(`${API}/patient/appointments`, {
          doctor_id: selectedDoc.value.id,
          ...bookForm.value
        })
        alert.value = { msg: 'Appointment booked successfully!', type: 'success' }
        showBook.value = false
      } catch (e) {
        alert.value = { msg: e.response?.data?.error || 'Booking failed', type: 'danger' }
      } finally {
        saving.value = false
        setTimeout(() => alert.value.msg = '', 4000)
      }
    }

    onMounted(async () => {
      await load()
      const res = await axios.get(`${API}/patient/departments`)
      departments.value = res.data
    })

    return {
      doctors, departments, search, deptFilter, loading, showBook, selectedDoc,
      availability, saving, alert, bookForm, minDate, maxDate, timeSlots,
      load, selectDoctor, loadAvailability, confirmBook
    }
  }
}
</script>
