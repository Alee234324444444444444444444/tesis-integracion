import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import "../styles/AdminMuestras.css";

export default function AdminMuestras() {
  const navigate = useNavigate();

  const [muestras, setMuestras] = useState([]);
  const [form, setForm] = useState({ nombre: '', descripcion: '' });

  const fetchMuestras = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/tipos-muestra/');
      const data = Array.isArray(res.data) ? res.data : res.data.results || [];
      setMuestras(data);
    } catch (err) {
      console.error('❌ Error cargando tipos de muestra:', err);
      setMuestras([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/tipos-muestra/', form);
      setForm({ nombre: '', descripcion: '' });
      fetchMuestras();
    } catch (err) {
      console.error('❌ Error creando tipo de muestra:', err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/api/tipos-muestra/${id}/`);
      fetchMuestras();
    } catch (err) {
      console.error('❌ Error eliminando tipo de muestra:', err);
    }
  };

  useEffect(() => {
    fetchMuestras();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div className="adminmuestras-container">
      <div className="adminmuestras-sidebar">
        <div className="adminmuestras-logo-section">
          <div className="adminmuestras-logo">
            <img src="/logo-white.png" alt="Logo" className="logo-white" />
            ENVIRONOVALAB
          </div>
        </div>
        <div className="adminmuestras-menu">
          <button className="adminmuestras-menu-item" onClick={() => navigate("/dashboard")}>Inicio</button>
          <button className="adminmuestras-menu-item" onClick={() => navigate("/proformas")}>Proformas</button>
          <button className="adminmuestras-menu-item active" onClick={() => navigate("/admin/tipos-muestra")}>Tipos de Muestra</button>
        </div>
        <button onClick={handleLogout} className="adminmuestras-logout-btn">Cerrar Sesión</button>
      </div>

      <div className="adminmuestras-main">
        <h1 className="adminmuestras-title">Administrar Tipos de Muestra</h1>

        <form onSubmit={handleSubmit} className="adminmuestras-form">
          <input
            type="text"
            placeholder="Nombre del tipo de muestra"
            value={form.nombre}
            onChange={e => setForm({ ...form, nombre: e.target.value })}
            required
          />
          <textarea
            placeholder="Descripción (opcional)"
            value={form.descripcion}
            onChange={e => setForm({ ...form, descripcion: e.target.value })}
          />
          <button type="submit" className="adminmuestras-button green">Agregar</button>
        </form>

        <ul className="adminmuestras-list">
          {muestras.map(m => (
            <li key={m.id} className="adminmuestras-item">
              <div>
                <strong>{m.nombre}</strong>
                {m.descripcion && <> - {m.descripcion}</>}
              </div>
              <button className="adminmuestras-button red" onClick={() => handleDelete(m.id)}>Eliminar</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
