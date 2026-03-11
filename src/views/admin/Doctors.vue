<template>
  <AppLayout>
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h1 class="page-title">Doctors</h1>
        <p class="page-subtitle">Manage doctor profiles and credentials</p>
      </div>
      <button class="btn btn-primary" @click="openAdd">
        <i class="bi bi-plus-lg me-2"></i>Add Doctor
      </button>
    </div>

    <div v-if="alert.msg" :class="`alert alert-${alert.type}`">{{ alert.msg }}</div>

    <div class="card">
      <div class="card-header">
        <h2 class="card-title">All Doctors ({{ doctors.length }})</h2>
        <input v-model="search" type="text" class="form-control w-auto" placeholder="Search..." style="max-width:220px" />
      </div>
      <div class="table-wrapper">
        <table class="hms-table">
          <thead>
            <tr>
              <th>Name</th><th>Specialization</th><th>Department</th>
              <th>Phone</th><th>Exp. (yrs)</th><th>Status</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in filtered" :key="d.id">
              <td>
                <div class="d-flex align-items-center gap-2">
                  <div class="user-avatar" style="width:32px;height:32px;font-size:0.75rem;border-radius:50%;background:var(--primary);display:flex;align-items:center;justify-content:center;color:white">
                    {{ d.full_name.slice(0,2).toUpperCase() }}
                  </div>
                  <div>
                    <div style="font-weight:600">{{ d.full_name }}</div>
                    <div style="font-size:0.78rem;color:var(--text-muted)">{{ d.email }}</div>
                  </div>
                </div>
              </td>
              <td>{{ d.specialization }}</td>
              <td>{{ d.department || '—' }}</td>
              <td>{{ d.phone || '—' }}</td>
              <td>{{ d.experience_years }}</td>
              <td>
                <span :class="d.is_available ? 'badge-status badge-completed' : 'badge-status badge-cancelled'">
                  {{ d.is_available ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(d)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="removeDoctor(d)">
                  <i class="bi bi-person-x"></i>
                </button>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7">
                <div class="empty-state"><i class="bi bi-person-badge d-block"></i><p>No doctors found</p></div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" style="border-radius:14px">
          <div class="modal-header">
            <h5 class="modal-title">{{ editMode ? 'Edit Doctor' : 'Add New Doctor' }}</h5>
            <button class="btn-close" @click="showModal=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div v-if="!editMode" class="col-6">
                <label class="form-label">Username *</label>
                <input v-model="form.username" class="form-control" required />
              </div>
              <div v-if="!editMode" class="col-6">
                <label class="form-label">Email *</label>
                <input v-model="form.email" type="email" class="form-control" required />
              </div>
              <div v-if="!editMode" class="col-6">
                <label class="form-label">Password *</label>
                <input v-model="form.password" type="password" class="form-control" required />
              </div>
              <div class="col-6">
                <label class="form-label">Full Name *</label>
                <input v-model="form.full_name" class="form-control" required />
              </div>
              <div class="col-6">
                <label class="form-label">Specialization</label>
                <input v-model="form.specialization" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label">Department</label>
                <select v-model="form.department_id" class="form-select">
                  <option value="">Select</option>
                  <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                </select>
              </div>
              <div class="col-6">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control" />
              </div>
              <div class="col-6">
                <label class="form-label">Experience (years)</label>
                <input v-model.number="form.experience_years" type="number" class="form-control" />
              </div>
              <div class="col-12">
                <label class="form-label">Bio</label>
                <textarea v-model="form.bio" class="form-control" rows="2"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="saveDoctor" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ editMode ? 'Update' : 'Add Doctor' }}
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
  name: 'AdminDoctors',
  components: { AppLayout },
  setup() {
    const doctors = ref([])
    const departments = ref([])
    const search = ref('')
    const showModal = ref(false)
    const editMode = ref(false)
    const editId = ref(null)
    const saving = ref(false)
    const alert = ref({ msg: '', type: 'success' })
    const form = ref({
      username: '', email: '', password: '', full_name: '',
      specialization: '', department_id: '', phone: '', experience_years: 0, bio: ''
    })

    const filtered = computed(() => {
      if (!search.value) return doctors.value
      const q = search.value.toLowerCase()
      return doctors.value.filter(d =>
        d.full_name.toLowerCase().includes(q) || (d.specialization||'').toLowerCase().includes(q)
      )
    })

    const load = async () => {
      const [dr, dep] = await Promise.all([
        axios.get(`${API}/admin/doctors`),
        axios.get(`${API}/admin/departments`)
      ])
      doctors.value = dr.data
      departments.value = dep.data
    }

    const openAdd = () => {
      editMode.value = false
      form.value = { username: '', email: '', password: '', full_name: '', specialization: '', department_id: '', phone: '', experience_years: 0, bio: '' }
      showModal.value = true
    }

    const openEdit = (d) => {
      editMode.value = true
      editId.value = d.id
      form.value = { ...d }
      showModal.value = true
    }

    const saveDoctor = async () => {
      saving.value = true
      try {
        if (editMode.value) {
          await axios.put(`${API}/admin/doctors/${editId.value}`, form.value)
          alert.value = { msg: 'Doctor updated!', type: 'success' }
        } else {
          await axios.post(`${API}/admin/doctors`, form.value)
          alert.value = { msg: 'Doctor added!', type: 'success' }
        }
        showModal.value = false
        await load()
      } catch (e) {
        alert.value = { msg: e.response?.data?.error || 'Error', type: 'danger' }
      } finally {
        saving.value = false
        setTimeout(() => alert.value.msg = '', 3000)
      }
    }

    const removeDoctor = async (d) => {
      if (!confirm(`Deactivate Dr. ${d.full_name}?`)) return
      await axios.delete(`${API}/admin/doctors/${d.id}`)
      await load()
    }

    onMounted(load)
    return { doctors, departments, search, filtered, showModal, editMode, form, saving, alert, openAdd, openEdit, saveDoctor, removeDoctor }
  }
}
</script>
