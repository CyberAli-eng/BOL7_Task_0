import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// withCredentials is essential: it tells the browser to send/receive the
// HTTP-only cookies that hold our JWT access/refresh tokens.
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
})

let isRefreshing = false
let queue = []

const processQueue = (error) => {
  queue.forEach(({ resolve, reject }) => (error ? reject(error) : resolve()))
  queue = []
}

// If a protected request comes back 401, try to silently refresh the
// access token cookie once, then retry the original request.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    const isAuthEndpoint = ['/login/', '/register/', '/token/refresh/'].some((p) =>
      originalRequest.url?.includes(p)
    )

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ resolve, reject })
        }).then(() => api(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await api.post('/token/refresh/')
        processQueue(null)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api
