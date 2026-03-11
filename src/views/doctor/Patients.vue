<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">My Patients</h1>
      <p class="page-subtitle">View patient history and records</p>
    </div>

    <div class="row g-3">
      <div class="col-md-4">
        <div class="card">
          <div class="card-header"><h2 class="card-title">Patient List</h2></div>
          <div style="max-height:600px;overflow-y:auto">
            <div v-if="!patients.length" class="empty-state p-4">
              <i class="bi bi-people d-block"></i><p>No patients yet</p>
            </div>
            <div
              v-for="p in patients" :key="p.id"
              class="p-3 d-flex align-items-center gap-3"
              style="border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.15s"
              :style="selected?.id === p.id ? 'background:#f0f5ff' : ''"
              @click="loadHistory(p)"
            >
              <div class="user-avatar" style="width:40px;height:40px;font-size:0.85rem;border-radius:50%;background:var(--primary);display:flex;align-items:center;justify-content:center;color:white;flex-shrink:0">
                {{ p.full_name.slice(0,2).toUpperCase() }}
              </div>
              <div>
                <div style="font-weight:600;font-size:0.92rem">{{ p.full_name }}</div>
                <div style="font-size:0.78rem;color:var(--text-muted)">{{ p.phone || p.email }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">{{ selected ? selected.full_name + ' — History' : 'Select a patient' }}</h2>
          </div>
          <div v-if="!selected" class="empty-state p-5">
            <i class="bi bi-person-lines-fill d-block"></i>
            <p>Click a patient to view their treatment history</p>
          </div>
          <div v-else class="table-wrapper">
            <table class="hms-table">
              <thead><tr><th>Date</th><th>Status</th><th>Diagnosis</th><th>Prescription</th><th>Next Visit</th></tr></thead>
              <tbody>
                <tr v-for="a in history" :key="a.id">
                  <td>{{ a.date }}</td>
                  <td><span :class="`badge-status badge-${a.status.toLowerCase()}`">{{ a.status }}</span></td>
                  <td>{{ a.treatment?.diagnosis || '—' }}</td>
                  <td>{{ a.treatment?.prescription || '—' }}</td>
                  <td>{{ a.treatment?.next_visit || '—' }}</td>
                </tr>
                <tr v-if="!history.length">
                  <td colspan="5" class="text-center text-muted py-4">No history found</td>
                </tr>
              </tbody>
            </table>
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
  name: 'DoctorPatients',
  components: { AppLayout },
  setup() {
    const patients = ref([])
    const selected = ref(null)
    const history = ref([])

    const loadHistory = async (p) => {
      selected.value = p
      const res = await axios.get(`${API}/doctor/patients/${p.id}/history`)
      history.value = res.data
    }

    onMounted(async () => {
      const res = await axios.get(`${API}/doctor/patients`)
      patients.value = res.data
    })
    return { patients, selected, history, loadHistory }
  }
}
</script>
