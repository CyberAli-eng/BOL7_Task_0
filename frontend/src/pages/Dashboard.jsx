import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="page-center">
      <div className="card">
        <h1>Dashboard</h1>
        <p className="subtitle">You're logged in.</p>

        <div className="profile-row">
          <span className="label">Name</span>
          <span>{user?.name}</span>
        </div>
        <div className="profile-row">
          <span className="label">Email</span>
          <span>{user?.email}</span>
        </div>
        <div className="profile-row">
          <span className="label">Verification status</span>
          <span className={user?.is_verified ? 'badge success' : 'badge pending'}>
            {user?.is_verified ? 'Verified' : 'Not verified'}
          </span>
        </div>

        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  )
}
