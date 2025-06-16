import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/Login.css'
import axios from 'axios'
import Cookies from 'js-cookie'

import { FaUser, FaLock } from 'react-icons/fa'
import { AiOutlineEye, AiOutlineEyeInvisible } from 'react-icons/ai'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Paso 1: obtener token CSRF y establecer la cookie
      await axios.get('http://localhost:8000/api/csrf/', {
        withCredentials: true
      })

      // Paso 2: hacer login con sesión y CSRF
      const res = await axios.post('http://localhost:8000/api/auth/login/', form, {
        withCredentials: true
      })

      // Paso 3: guardar datos en localStorage
      localStorage.setItem('auth', 'true')
      localStorage.setItem('user', res.data.username)
      localStorage.setItem('userRole', res.data.is_admin ? 'admin' : 'user')

      navigate('/dashboard')
    } catch (err) {
      console.error("❌ Login error:", err)
      setError('Usuario o contraseña incorrectos')
    } finally {
      setLoading(false)
    }
  }

  const togglePasswordVisibility = () => setShowPassword(!showPassword)
  const handleRegister = () => navigate('/register')
  const handleForgotPassword = () => navigate('/forgot-password')

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="logo-container">
            <img src="/logo.png" alt="Logo" className="logo" />
          </div>
          <h1 className="login-title">ENVIRONOVALAB</h1>
          <h2 className="login-subtitle"><strong>INICIAR SESIÓN</strong></h2>
        </div>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-input-group">
            <FaUser className="login-icon" />
            <input
              type="text"
              name="username"
              placeholder="Usuario"
              value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })}
              className="login-input"
              required
            />
          </div>

          <div className="login-input-group">
            <FaLock className="login-icon" />
            <input
              type={showPassword ? 'text' : 'password'}
              name="password"
              placeholder="Contraseña"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="login-input"
              required
            />
            <span className="login-toggle-password" onClick={togglePasswordVisibility}>
              {showPassword ? <AiOutlineEyeInvisible /> : <AiOutlineEye />}
            </span>
          </div>

          <button type="submit" className="login-button" disabled={loading}>
            <strong>{loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}</strong>
          </button>
        </form>

        <div className="login-links">
          <button type="button" onClick={handleForgotPassword} className="login-forgot-password-link">
            ¿Olvidó su contraseña?
          </button>
          <div className="login-register-text">
            ¿No tienes cuenta?{' '}
            <button type="button" onClick={handleRegister} className="login-register-link">
              Registrarse
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}