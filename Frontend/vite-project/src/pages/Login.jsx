import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import './Login.css'

export default function Login() {
  const { login, register, isAuthenticated } = useAuth()
  const [isRegister, setIsRegister] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (isRegister && form.password !== form.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)
    try {
      if (isRegister) {
        await register(form.name, form.email, form.password)
      } else {
        await login(form.email, form.password)
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-brand">
          <span className="login-logo">💰</span>
          <h1>DebtRelief AI</h1>
          <p>AI-Powered Debt Relief & Financial Recovery Platform</p>
        </div>

        <div className="login-card">
          <h2>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
          <p className="login-subtitle">
            {isRegister
              ? 'Register to start your financial recovery journey'
              : 'Sign in to access your financial dashboard'}
          </p>

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <Input
                label="Full Name"
                value={form.name}
                onChange={handleChange('name')}
                placeholder="John Doe"
                required
              />
            )}
            <Input
              label="Email Address"
              type="email"
              value={form.email}
              onChange={handleChange('email')}
              placeholder="you@example.com"
              required
            />
            <Input
              label="Password"
              type="password"
              value={form.password}
              onChange={handleChange('password')}
              placeholder="••••••••"
              required
              hint={isRegister ? 'Minimum 8 characters' : undefined}
            />
            {isRegister && (
              <Input
                label="Confirm Password"
                type="password"
                value={form.confirmPassword}
                onChange={handleChange('confirmPassword')}
                placeholder="••••••••"
                required
              />
            )}

            {error && <div className="login-error">{error}</div>}

            <Button type="submit" fullWidth disabled={loading}>
              {loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
            </Button>
          </form>

          <div className="login-toggle">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}
            <button
              type="button"
              className="login-toggle-btn"
              onClick={() => {
                setIsRegister(!isRegister)
                setError('')
              }}
            >
              {isRegister ? 'Sign In' : 'Register'}
            </button>
          </div>
        </div>

        <p className="login-footer">
          Secure login · Your financial data is protected
        </p>
      </div>
    </div>
  )
}
