<template>
  <AppLayout>
    <div class="page-header">
      <h1 class="page-title">Search</h1>
      <p class="page-subtitle">Find doctors, patients, and specializations</p>
    </div>

    <div class="card mb-4">
      <div class="p-4">
        <div class="input-group">
          <input v-model="query" type="text" class="form-control form-control-lg" placeholder="Search by name, specialization..." @keyup.enter="doSearch" />
          <button class="btn btn-primary px-4" @click="doSearch" :disabled="loading">
            <i class="bi bi-search me-1"></i> Search
          </button>
        </div>
      </div>
    </div>

    <div v-if="searched">
      <div class="row g-4">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Doctors ({{ results.doctors.length }})</h2>
            </div>
            <div class="table-wrapper">
              <table class="hms-table">
                <thead><tr><th>Name</th><th>Specialization</th><th>Department</th></tr></thead>
                <tbody>
                  <tr v-for="d in results.doctors" :key="d.id">
                    <td>{{ d.full_name }}</td>
                    <td>{{ d.specialization }}</td>
                    <td>{{ d.department || '—' }}</td>
                  </tr>
                  <tr v-if="!results.doctors.length">
                    <td colspan="3" class="text-center text-muted py-3">No doctors found</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Patients ({{ results.patients.length }})</h2>
            </div>
            <div class="table-wrapper">
              <table class="hms-table">
                <thead><tr><th>Name</th><th>Phone</th><th>Blood Group</th></tr></thead>
                <tbody>
                  <tr v-for="p in results.patients" :key="p.id">
                    <td>{{ p.full_name }}</td>
                    <td>{{ p.phone || '—' }}</td>
                    <td>{{ p.blood_group || '—' }}</td>
                  </tr>
                  <tr v-if="!results.patients.length">
                    <td colspan="3" class="text-center text-muted py-3">No patients found</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import AppLayout from '../../components/AppLayout.vue'

export default {
  name: 'AdminSearch',
  components: { AppLayout },
  setup() {
    const query = ref('')
    const results = ref({ doctors: [], patients: [] })
    const loading = ref(false)
    const searched = ref(false)

    const doSearch = async () => {
      if (!query.value.trim()) return
      loading.value = true
      try {
        const res = await axios.get('http://localhost:5000/api/admin/search', { params: { q: query.value } })
        results.value = res.data
        searched.value = true
      } finally { loading.value = false }
    }
    return { query, results, loading, searched, doSearch }
  }
}
</script>
