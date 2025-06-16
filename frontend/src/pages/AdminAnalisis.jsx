import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import '../styles/AdminAnalisis.css'; // Asegúrate de tener este archivo CSS

export default function AdminAnalisis() {
  const navigate = useNavigate();

  const [analisis, setAnalisis] = useState([]);
  const [parametros, setParametros] = useState([]);
  const [metodos, setMetodos] = useState([]);
  const [tecnicas, setTecnicas] = useState([]);

  const [form, setForm] = useState({
    parametro: '',
    unidad: '',
    metodo: '',
    tecnica: '',
    precio: '',
    cantidad: 1
  });

  useEffect(() => {
    fetchParametros();
    fetchMetodos();
    fetchTecnicas();
    fetchAnalisis();
  }, []);

  const axiosAuth = () => {
    return axios.create({
      withCredentials: true,
      headers: {
        'X-CSRFToken': Cookies.get('csrftoken'),
        'Content-Type': 'application/json'
      }
    });
  };

  const fetchParametros = async () => {
    try {
      const res = await axiosAuth().get('http://localhost:8000/api/parameters/');
      setParametros(res.data);
    } catch (err) {
      console.error('❌ Error cargando parámetros:', err);
    }
  };

  const fetchMetodos = async () => {
    try {
      const res = await axiosAuth().get('http://localhost:8000/api/methods/');
      setMetodos(res.data);
    } catch (err) {
      console.error('❌ Error cargando métodos:', err);
    }
  };

  const fetchTecnicas = async () => {
    try {
      const res = await axiosAuth().get('http://localhost:8000/api/techniques/');
      setTecnicas(res.data);
    } catch (err) {
      console.error('❌ Error cargando técnicas:', err);
    }
  };

  const fetchAnalisis = async () => {
    try {
      const res = await axiosAuth().get('http://localhost:8000/api/analysis/');
      setAnalisis(res.data);
    } catch (err) {
      console.error('❌ Error cargando análisis:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      parameter: form.parametro,
      unit: form.unidad,
      method: form.metodo,
      technique: form.tecnica,
      unit_price: parseFloat(form.precio),
      quantity: parseInt(form.cantidad)
    };

    try {
      await axiosAuth().post('http://localhost:8000/api/analysis/', payload);
      setForm({ parametro: '', unidad: '', metodo: '', tecnica: '', precio: '', cantidad: 1 });
      fetchAnalisis();
    } catch (err) {
      console.error('❌ Error guardando análisis:', err);
      alert('Error: ' + (err.response?.data?.error || 'No autorizado'));
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
          <button className="active" onClick={() => navigate("/admin/analisis")}>Análisis</button>
        </div>
      </div>

      <div className="adminanalisis-main">
        <h1>Gestión de Análisis</h1>

        <form onSubmit={handleSubmit} className="adminanalisis-form">
          <select name="parametro" value={form.parametro} onChange={handleChange} required>
            <option value="">-- Seleccionar Parámetro --</option>
            {parametros.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>

          <input
            type="text"
            name="unidad"
            placeholder="Unidad"
            value={form.unidad}
            onChange={handleChange}
            required
          />

          <select name="metodo" value={form.metodo} onChange={handleChange} required>
            <option value="">-- Seleccionar Método --</option>
            {metodos.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
          </select>

          <select name="tecnica" value={form.tecnica} onChange={handleChange} required>
            <option value="">-- Seleccionar Técnica --</option>
            {tecnicas.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>

          <input
            type="number"
            name="precio"
            placeholder="Precio Unitario"
            value={form.precio}
            onChange={handleChange}
            required
          />

          <input
            type="number"
            name="cantidad"
            min="1"
            placeholder="Cantidad"
            value={form.cantidad}
            onChange={handleChange}
            required
          />

          <button type="submit">Agregar Análisis</button>
        </form>

        <div className="adminanalisis-list">
          <h2>Lista de Análisis Creados</h2>
          <ul>
            {analisis.map(a => (
              <li key={a.id}>
                <strong>{a.parameter_name}</strong> - {a.unit} - {a.method_name} - {a.technique_name} - ${a.unit_price} x {a.quantity}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}