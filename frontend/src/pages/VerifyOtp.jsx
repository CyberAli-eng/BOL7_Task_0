import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import api from '../api/axios'

export default function VerifyOtp() {
  const location = useLocation()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: location.state?.email || '', otp: '' })
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [loading, setLoading] = useState(false)
  const [resending, setResending] = useState(false)

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setInfo('')
    setLoading(true)
    try {
      await api.post('/verify-otp/', form)
      navigate('/login', { state: { verified: true, email: form.email } })
    } catch (err) {
      const data = err.response?.data
      setError(data?.otp || data?.email || data?.detail || 'Verification failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setError('')
    setInfo('')
    setResending(true)
    try {
      await api.post('/resend-otp/', { email: form.email })
      setInfo('A new OTP has been sent to your email.')
    } catch (err) {
      setError(err.response?.data?.email || 'Could not resend OTP.')
    } finally {
      setResending(false)
    }
  }

  return (
    <div className="page-center">
      <form className="card" onSubmit={handleSubmit}>
        <h1>Verify your email</h1>
        <p className="subtitle">Enter the 6-digit code sent to your email. It expires in 5 minutes.</p>

        <label>Email</label>
        <input type="email" name="email" value={form.email} onChange={handleChange} required />

        <label>OTP</label>
        <input
          name="otp"
          value={form.otp}
          onChange={handleChange}
          maxLength={6}
          pattern="\d{6}"
          required
        />

        {error && <span className="error">{error}</span>}
        {info && <span className="info">{info}</span>}

        <button type="submit" disabled={loading}>
          {loading ? 'Verifying...' : 'Verify OTP'}
        </button>

        <button type="button" className="secondary" onClick={handleResend} disabled={resending}>
          {resending ? 'Resending...' : 'Resend OTP'}
        </button>
      </form>
    </div>
  )
}
