import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { MdLock } from 'react-icons/md'
import '../styles/ResetPassword.css'

export default function ResetPassword() {
  const { token } = useParams()
  const navigate = useNavigate()

  const [password, setPassword] = useState('')
  const [message, setMessage] = useState(null)
  const [isSuccess, setIsSuccess] = useState(false)
  const [loading, setLoading] = useState(false) // 👈 Estado para "Cambiando..."

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true) // activar "Cambiando..."
    try {
      const res = await axios.post(`http://localhost:8000/api/auth/reset-password/${token}/`, {
        password
      })
      setMessage(res.data.msg)
      setIsSuccess(true)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Error al cambiar la contraseña'
      setMessage(errorMsg)
      setIsSuccess(false)
    } finally {
      setLoading(false) // desactivar después del intento
    }
  }

  return (
    <div className="reset-container">
      <div className="reset-card">
        <div className="reset-header">
          <div className="reset-logo-container">
            <img src="/logo.png" alt="Logo" className="reset-logo" />
          </div>
          <h2 className="reset-title">ENVIRONOVALAB</h2>
          <p className="reset-subtitle">Ingresa tu nueva contraseña para continuar</p>
        </div>

        {message && (
          <div className={isSuccess ? 'reset-success' : 'reset-error'}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="reset-form">
          <div className="reset-input-group">
            <MdLock className="reset-icon" />
            <input
              type="password"
              placeholder="Nueva contraseña"
              className="reset-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="reset-button" disabled={loading}>
            <strong>{loading ? 'Cambiando contraseña...' : 'Cambiar contraseña'}</strong>
          </button>
        </form>
      </div>
    </div>
  )
}
