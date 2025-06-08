import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function ResetPassword() {
  const { token } = useParams()
  const navigate = useNavigate()

  const [password, setPassword] = useState('')
  const [message, setMessage] = useState(null)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
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
    }
  }

  return (
    <div className="fp-container">
      <div className="fp-card">
        <h1 className="fp-title">Nueva Contraseña</h1>
        <p className="fp-subtitle">Ingresa tu nueva contraseña</p>

        {message && (
          <div className={`fp-message ${isSuccess ? 'fp-success' : 'fp-error'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="fp-form">
          <input
            type="password"
            placeholder="Nueva contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="fp-input"
            required
          />
          <button type="submit" className="fp-button">
            Cambiar contraseña
          </button>
        </form>
      </div>
    </div>
  )
}
