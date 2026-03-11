import { createStore } from 'vuex'
import axios from 'axios'

const API = 'http://localhost:5000/api'

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default createStore({
  state: {
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    profileId: localStorage.getItem('profileId') || null,
    loading: false,
    error: null
  },
  getters: {
    isLoggedIn: s => !!s.token,
    role: s => s.user?.role,
    userId: s => s.user?.id,
    profileId: s => s.profileId
  },
  mutations: {
    SET_AUTH(state, { user, token, profileId }) {
      state.user = user
      state.token = token
      state.profileId = profileId
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('profileId', profileId)
    },
    LOGOUT(state) {
      state.user = null
      state.token = null
      state.profileId = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('profileId')
    },
    SET_LOADING(state, v) { state.loading = v },
    SET_ERROR(state, v) { state.error = v }
  },
  actions: {
    async login({ commit }, { username, password }) {
      const res = await axios.post(`${API}/auth/login`, { username, password })
      commit('SET_AUTH', {
        user: res.data.user,
        token: res.data.access_token,
        profileId: res.data.profile_id
      })
      return res.data.user.role
    },
    async register({ commit }, payload) {
      const res = await axios.post(`${API}/auth/register`, payload)
      commit('SET_AUTH', {
        user: res.data.user,
        token: res.data.access_token,
        profileId: res.data.profile_id
      })
      return 'patient'
    },
    logout({ commit }) {
      commit('LOGOUT')
    }
  }
})
