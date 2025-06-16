import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import "../styles/AdminAnalisis.css";

export default function AdminCatalogoAnalisis() {
  const navigate = useNavigate();
  const [catalogo, setCatalogo] = useState([]);
  const [form, setForm] = useState({
    tipo: 'agua',
    parametro: '',
    unidad: '',
    metodo: '',
    tecnica: '',
    precio: ''
  });

  const fetchCSRF = async () => {
    try {
      await axios.get('http://localhost:8000/api/csrf/', { withCredentials: true });
    } catch (err) {
      console.error('⚠️ Error obteniendo CSRF:', err);
    }
  };

  const fetchCatalogo = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/catalogo-analisis/', {
        withCredentials: true,
        headers: { 'X-CSRFToken': Cookies.get('csrftoken') }
      });
      setCatalogo(res.data);
    } catch (err) {
      console.error('❌ Error cargando catálogo:', err);
    }
  };

  useEffect(() => {
  const fetchAll = async () => {
    try {
      // 1️⃣ Asegurar que el backend envía el csrf cookie
      await axios.get('http://localhost:8000/api/csrf/', {
        withCredentials: true,
      });

      // 2️⃣ Obtener catálogo de análisis con sesión y csrf válidos
      const res = await axios.get('http://localhost:8000/api/catalogo-analisis/', {
        withCredentials: true,
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
        },
      });

      setCatalogo(res.data);
    } catch (err) {
      console.error('❌ Error cargando catálogo:', err);
    }
  };

  fetchAll();
}, []);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await fetchCSRF();
      await axios.post('http://localhost:8000/api/catalogo-analisis/', form, {
        withCredentials: true,
        headers: { 'X-CSRFToken': Cookies.get('csrftoken') }
      });
      setForm({ tipo: 'agua', parametro: '', unidad: '', metodo: '', tecnica: '', precio: '' });
      fetchCatalogo();
    } catch (err) {
      console.error('❌ Error al crear análisis:', err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await fetchCSRF();
      await axios.delete(`http://localhost:8000/api/catalogo-analisis/${id}/`, {
        withCredentials: true,
        headers: { 'X-CSRFToken': Cookies.get('csrftoken') }
      });
      fetchCatalogo();
    } catch (err) {
      console.error('❌ Error al eliminar análisis:', err);
    }
  };

  return (
    <div className="adminanalisis-container">
      <div className="adminanalisis-sidebar">
        <div className="adminanalisis-logo">ENVIRONOVALAB</div>
        <div className="adminanalisis-menu">
          <button onClick={() => navigate("/dashboard")}>Inicio</button>
          <button onClick={() => navigate("/proformas")}>Proformas</button>
          <button onClick={() => navigate("/admin/tipos-muestra")}>Tipos de Muestra</button>
          <button className="active" onClick={() => navigate("/admin/catalogo-analisis")}>Catálogo Análisis</button>
        </div>
      </div>

      <div className="adminanalisis-main">
        <h1>Catálogo de Análisis</h1>

        <form onSubmit={handleSubmit} className="adminanalisis-form">
          <select name="tipo" value={form.tipo} onChange={handleChange} required>
            <option value="agua">Agua</option>
            <option value="ruido">Ruido</option>
            <option value="emisiones">Emisiones</option>
            <option value="logistica">Logística</option>
          </select>
          <input name="parametro" value={form.parametro} onChange={handleChange} placeholder="Parámetro" required />
          <input name="unidad" value={form.unidad} onChange={handleChange} placeholder="Unidad" required />
          <input name="metodo" value={form.metodo} onChange={handleChange} placeholder="Método" required />
          <input name="tecnica" value={form.tecnica} onChange={handleChange} placeholder="Técnica" required />
          <input name="precio" type="number" step="0.01" value={form.precio} onChange={handleChange} placeholder="Precio" required />
          <button type="submit">Agregar</button>
        </form>

        <div className="adminanalisis-list">
          <h2>Lista de Análisis</h2>
          <ul>
            {catalogo.map((item) => (
              <li key={item.id}>
                <strong>{item.tipo.toUpperCase()}</strong> - {item.parametro} | {item.unidad} | {item.metodo} | {item.tecnica} | ${item.precio}
                <button style={{ marginLeft: '10px', color: 'red' }} onClick={() => handleDelete(item.id)}>Eliminar</button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
