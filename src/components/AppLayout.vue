<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <p class="brand-name">MediCare</p>
        <p class="brand-sub">Hospital Management</p>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
        >
          <i :class="'bi bi-' + item.icon"></i>
          {{ item.label }}
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-badge">
          <div class="user-avatar">{{ initials }}</div>
          <div>
            <div class="user-name">{{ user?.username }}</div>
            <div class="user-role">{{ user?.role }}</div>
          </div>
        </div>
        <button class="nav-item mt-3 text-danger" @click="logout" style="color:#ff6b6b!important">
          <i class="bi bi-box-arrow-left"></i> Logout
        </button>
      </div>
    </aside>

    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const NAV = {
  admin: [
    { path: '/admin/dashboard', icon: 'grid', label: 'Dashboard' },
    { path: '/admin/doctors', icon: 'person-badge', label: 'Doctors' },
    { path: '/admin/patients', icon: 'people', label: 'Patients' },
    { path: '/admin/appointments', icon: 'calendar3', label: 'Appointments' },
    { path: '/admin/search', icon: 'search', label: 'Search' },
  ],
  doctor: [
    { path: '/doctor/dashboard', icon: 'grid', label: 'Dashboard' },
    { path: '/doctor/appointments', icon: 'calendar3', label: 'Appointments' },
    { path: '/doctor/patients', icon: 'people', label: 'My Patients' },
    { path: '/doctor/availability', icon: 'clock', label: 'Availability' },
  ],
  patient: [
    { path: '/patient/dashboard', icon: 'grid', label: 'Dashboard' },
    { path: '/patient/doctors', icon: 'person-badge', label: 'Find Doctors' },
    { path: '/patient/appointments', icon: 'calendar3', label: 'Appointments' },
    { path: '/patient/profile', icon: 'person-circle', label: 'My Profile' },
  ]
}

export default {
  name: 'AppLayout',
  setup() {
    const store = useStore()
    const router = useRouter()
    const user = computed(() => store.state.user)
    const role = computed(() => store.getters.role)
    const navItems = computed(() => NAV[role.value] || [])
    const initials = computed(() => {
      const u = user.value?.username || ''
      return u.slice(0, 2).toUpperCase()
    })
    const logout = () => {
      store.dispatch('logout')
      router.push('/login')
    }
    return { user, navItems, initials, logout }
  }
}
</script>
