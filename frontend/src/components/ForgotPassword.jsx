import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/ForgotPassword.css'
import axios from 'axios'
import { MdEmail } from 'react-icons/md'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState(null)
  const [isSuccess, setIsSuccess] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await axios.post('http://localhost:8000/api/auth/forgot-password/', { email })
      setMessage(res.data.msg || 'Solicitud enviada')
      setIsSuccess(true)
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'No se pudo procesar la solicitud'
      setMessage(errorMsg)
      setIsSuccess(false)
    }
  }

  return (
    <div className="fp-container">
      <div className="fp-card">
        <div className="fp-header">
          <h1 className="fp-title">Recuperar Contraseña</h1>
          <p className="fp-subtitle">Ingresa tu correo electrónico para restablecer tu contraseña</p>
        </div>

        {message && (
          <div className={`fp-message ${isSuccess ? 'fp-success' : 'fp-error'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="fp-form">
          <div className="fp-input-group">
            <MdEmail className="fp-icon" />
            <input
              type="email"
              placeholder="Correo electrónico"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="fp-input"
              required
            />
          </div>
          <button type="submit" className="fp-button">
            Enviar solicitud
          </button>
        </form>

        <div className="fp-back">
          <button onClick={() => navigate('/login')} className="fp-back-button">
            Volver al login
          </button>
        </div>
      </div>
    </div>
  )
}
