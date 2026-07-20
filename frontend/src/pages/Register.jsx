import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm_password: '' })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      await api.post('/register/', form)
      navigate('/verify-otp', { state: { email: form.email } })
    } catch (err) {
      setErrors(err.response?.data || { detail: 'Registration failed.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-center">
      <form className="card" onSubmit={handleSubmit}>
        <h1>Create account</h1>
        <p className="subtitle">Sign up to get started</p>

        <label>Name</label>
        <input name="name" value={form.name} onChange={handleChange} required />
        {errors.name && <span className="error">{errors.name}</span>}

        <label>Email</label>
        <input type="email" name="email" value={form.email} onChange={handleChange} required />
        {errors.email && <span className="error">{errors.email}</span>}

        <label>Password</label>
        <input type="password" name="password" value={form.password} onChange={handleChange} required />
        {errors.password && <span className="error">{errors.password}</span>}

        <label>Confirm Password</label>
        <input
          type="password"
          name="confirm_password"
          value={form.confirm_password}
          onChange={handleChange}
          required
        />
        {errors.confirm_password && <span className="error">{errors.confirm_password}</span>}

        {errors.non_field_errors && <span className="error">{errors.non_field_errors}</span>}
        {errors.detail && <span className="error">{errors.detail}</span>}

        <button type="submit" disabled={loading}>
          {loading ? 'Creating account...' : 'Register'}
        </button>

        <p className="muted">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  )
}
