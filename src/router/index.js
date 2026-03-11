import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import AdminDoctors from '../views/admin/Doctors.vue'
import AdminPatients from '../views/admin/Patients.vue'
import AdminAppointments from '../views/admin/Appointments.vue'
import AdminSearch from '../views/admin/Search.vue'
import DoctorDashboard from '../views/doctor/Dashboard.vue'
import DoctorAppointments from '../views/doctor/Appointments.vue'
import DoctorPatients from '../views/doctor/Patients.vue'
import DoctorAvailability from '../views/doctor/Availability.vue'
import PatientDashboard from '../views/patient/Dashboard.vue'
import PatientDoctors from '../views/patient/Doctors.vue'
import PatientAppointments from '../views/patient/Appointments.vue'
import PatientProfile from '../views/patient/Profile.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login, meta: { guest: true } },
  { path: '/register', component: Register, meta: { guest: true } },
  { path: '/admin/dashboard', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/doctors', component: AdminDoctors, meta: { role: 'admin' } },
  { path: '/admin/patients', component: AdminPatients, meta: { role: 'admin' } },
  { path: '/admin/appointments', component: AdminAppointments, meta: { role: 'admin' } },
  { path: '/admin/search', component: AdminSearch, meta: { role: 'admin' } },
  { path: '/doctor/dashboard', component: DoctorDashboard, meta: { role: 'doctor' } },
  { path: '/doctor/appointments', component: DoctorAppointments, meta: { role: 'doctor' } },
  { path: '/doctor/patients', component: DoctorPatients, meta: { role: 'doctor' } },
  { path: '/doctor/availability', component: DoctorAvailability, meta: { role: 'doctor' } },
  { path: '/patient/dashboard', component: PatientDashboard, meta: { role: 'patient' } },
  { path: '/patient/doctors', component: PatientDoctors, meta: { role: 'patient' } },
  { path: '/patient/appointments', component: PatientAppointments, meta: { role: 'patient' } },
  { path: '/patient/profile', component: PatientProfile, meta: { role: 'patient' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const loggedIn = store.getters.isLoggedIn
  const role = store.getters.role

  if (to.meta.guest) {
    if (loggedIn) return next(`/${role}/dashboard`)
    return next()
  }
  if (!loggedIn) return next('/login')
  if (to.meta.role && to.meta.role !== role) return next(`/${role}/dashboard`)
  next()
})

export default router
