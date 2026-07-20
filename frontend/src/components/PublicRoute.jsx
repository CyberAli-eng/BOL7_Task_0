// src/components/PublicRoute.jsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function PublicRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <div className="page-center">Loading...</div>
  }

  // If user is already logged in, redirect them to dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  // If not logged in, render the login/register page as normal
  return children
}