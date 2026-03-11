<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Patients</h1>
      <p class="page-subtitle">Manage patient records</p>
    </div>

    <div v-if="alert.msg" :class="`alert alert-${alert.type}`">{{ alert.msg }}</div>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">All Patients ({{ patients.length }})</h2>
        <input v-model="search" type="text" class="form-control w-auto" placeholder="Search by name/phone..." style="max-width:240px" @input="loadPatients" />
      </div>
      <div class="table-wrapper">
        <table class="hms-table">
          <thead>
            <tr><th>Name</th><th>Email</th><th>Phone</th><th>Blood Group</th><th>Gender</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="p in patients" :key="p.id">
              <td>
                <div style="font-weight:600">{{ p.full_name }}</div>
              </td>
              <td>{{ p.email }}</td>
              <td>{{ p.phone || '—' }}</td>
              <td>{{ p.blood_group || '—' }}</td>
              <td>{{ p.gender || '—' }}</td>
              <td>
                <span :class="p.is_active !== false ? 'badge-status badge-completed' : 'badge-status badge-cancelled'">
                  {{ p.is_active !== false ? 'Active' : 'Blacklisted' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(p)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="toggleBlacklist(p)">
                  <i class="bi bi-slash-circle"></i>
                </button>
              </td>
            </tr>
            <tr v-if="!patients.length">
              <td colspan="7">
                <div class="empty-state"><i class="bi bi-people d-block"></i><p>No patients found</p></div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">Edit Patient</h5>
            <button class="btn-close" @click="showModal=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-6">
                <label class="form-label">Full Name</label>
                <input v-model="form.full_name" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label">Blood Group</label>
                <input v-model="form.blood_group" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label">Emergency Contact</label>
                <input v-model="form.emergency_contact" class="form-control" />
              </div>
              <div class="col-12">
                <label class="form-label">Address</label>
                <textarea v-model="form.address" class="form-control" rows="2"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="savePatient" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>Update
            </button>
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
  name: 'AdminPatients',
  components: { AppLayout },
  setup() {
    const patients = ref([])
    const search = ref('')
    const showModal = ref(false)
    const editId = ref(null)
    const saving = ref(false)
    const alert = ref({ msg: '', type: 'success' })
    const form = ref({})

    const loadPatients = async () => {
      const res = await axios.get(`${API}/admin/patients`, { params: { q: search.value } })
      patients.value = res.data
    }

    const openEdit = (p) => {
      editId.value = p.id
      form.value = { ...p }
      showModal.value = true
    }

    const savePatient = async () => {
      saving.value = true
      try {
        await axios.put(`${API}/admin/patients/${editId.value}`, form.value)
        alert.value = { msg: 'Patient updated!', type: 'success' }
        showModal.value = false
        await loadPatients()
      } catch (e) {
        alert.value = { msg: 'Error updating', type: 'danger' }
      } finally {
        saving.value = false
        setTimeout(() => alert.value.msg = '', 3000)
      }
    }

    const toggleBlacklist = async (p) => {
      if (!confirm('Toggle blacklist status for this patient?')) return
      await axios.post(`${API}/admin/patients/${p.id}/blacklist`)
      await loadPatients()
    }

    onMounted(loadPatients)
    return { patients, search, showModal, form, saving, alert, loadPatients, openEdit, savePatient, toggleBlacklist }
  }
}
</script>
