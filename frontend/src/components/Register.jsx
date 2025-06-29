import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/Register.css'
import axios from 'axios'

import { FaUser, FaLock } from 'react-icons/fa'
import { MdEmail } from 'react-icons/md'
import { AiOutlineEye, AiOutlineEyeInvisible } from 'react-icons/ai'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [message, setMessage] = useState(null)
  const [isSuccess, setIsSuccess] = useState(false)
  const [loading, setLoading] = useState(false) // 👈 nuevo estado
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true) // 👈 mostrar "Registrando..."
    try {
      const res = await axios.post('http://localhost:8000/api/register/', form, {
        headers: { 'Content-Type': 'application/json' }
      })
      setMessage(res.data.msg || 'Usuario creado correctamente')
      setIsSuccess(true)
      setTimeout(() => navigate('/login'), 1500)
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Error al registrar'
      setMessage(errorMsg)
      setIsSuccess(false)
    } finally {
      setLoading(false) // 👈 restaurar al final
    }
  }

  const togglePasswordVisibility = () => setShowPassword(!showPassword)
  const handleGoToLogin = () => navigate('/login')

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <div className="logo-container">
            <img src="/logo.png" alt="Logo" className="logo" />
          </div>
          <h1 className="register-title">ENVIRONOVALAB</h1>
          <h2 className="register-subtitle">REGISTRARSE</h2>
        </div>

        {message && (
          <div className={`register-message ${isSuccess ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="register-form">
          <div className="input-group">
            <FaUser className="input-icon" />
            <input
              type="text"
              name="username"
              placeholder="Usuario"
              value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })}
              className="register-input"
              required
            />
          </div>

          <div className="input-group">
            <MdEmail className="input-icon" />
            <input
              type="email"
              name="email"
              placeholder="Correo electrónico"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              className="register-input"
              required
            />
          </div>

          <div className="input-group">
            <FaLock className="input-icon" />
            <input
              type={showPassword ? 'text' : 'password'}
              name="password"
              placeholder="Contraseña"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="register-input"
              required
            />
            <span className="toggle-password" onClick={togglePasswordVisibility}>
              {showPassword ? <AiOutlineEyeInvisible /> : <AiOutlineEye />}
            </span>
          </div>

          <button type="submit" className="register-button" disabled={loading}>
            <strong>{loading ? 'Registrando...' : 'Registrarse'}</strong>
          </button>
        </form>

        <div className="register-links">
          <div className="register-text">
            ¿Ya tienes cuenta?{' '}
            <button type="button" onClick={handleGoToLogin} className="register-link">
              Inicia sesión
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
