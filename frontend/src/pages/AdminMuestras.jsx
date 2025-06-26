import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Cookies from 'js-cookie';
import {
  FaTrash, FaEdit, FaFlask, FaMoneyBill, FaRuler,
  FaClipboardList, FaPen, FaPlus
} from 'react-icons/fa';
import "../styles/Dashboard.css";
import "../styles/AdminMuestras.css";

export default function AdminMuestras() {
  const navigate = useNavigate();
  const [catalogo, setCatalogo] = useState([]);
  const [form, setForm] = useState({
    tipo: '', parametro: '', unidad: '', metodo: '', tecnica: '', precio: ''
  });
  const [errors, setErrors] = useState({});
  const [editId, setEditId] = useState(null);

  const fetchCatalogo = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/tipos-muestra/', {
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
        await axios.get('http://localhost:8000/api/csrf/', { withCredentials: true });
        await fetchCatalogo();
      } catch (err) {
        console.error('❌ Error inicial:', err);
      }
    };
    fetchAll();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const validate = () => {
    const newErrors = {};
    for (const field in form) {
      if (!form[field].trim()) {
        newErrors[field] = `⚠️ El campo "${field}" es obligatorio.`;
      }
    }

    if (form.precio && (isNaN(form.precio) || Number(form.precio) <= 0)) {
      newErrors.precio = '⚠️ El precio debe ser un número mayor que 0.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await axios.get('http://localhost:8000/api/csrf/', { withCredentials: true });
      const config = {
        withCredentials: true,
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
          'Content-Type': 'application/json'
        }
      };

      if (editId) {
        await axios.put(`http://localhost:8000/api/tipos-muestra/${editId}/`, form, config);
      } else {
        await axios.post(`http://localhost:8000/api/tipos-muestra/`, form, config);
      }

      setForm({ tipo: '', parametro: '', unidad: '', metodo: '', tecnica: '', precio: '' });
      setEditId(null);
      fetchCatalogo();
    } catch (err) {
      console.error('❌ Error al guardar muestra:', err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.get('http://localhost:8000/api/csrf/', { withCredentials: true });
      await axios.delete(`http://localhost:8000/api/tipos-muestra/${id}/`, {
        withCredentials: true,
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
          'Content-Type': 'application/json'
        }
      });
      fetchCatalogo();
    } catch (err) {
      console.error('❌ Error al eliminar muestra:', err);
    }
  };

  const handleEdit = (item) => {
    setEditId(item.id || item._id?.$oid);
    setForm({
      tipo: item.tipo || '',
      parametro: item.parametro || '',
      unidad: item.unidad || '',
      metodo: item.metodo || '',
      tecnica: item.tecnica || '',
      precio: item.precio || ''
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    localStorage.removeItem("userRole");
    navigate("/login");
  };

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <div className="logo-section">
          <div className="logo">
            <img src="/logo-white.png" alt="Logo" className="logo-white" />
            ENVIRONOVALAB
          </div>
        </div>
        <div className="menu">
          <button className="menu-item" onClick={() => navigate("/dashboard")}>Inicio</button>
          <button className="menu-item" onClick={() => navigate("/proformas")}>Proformas</button>
          <button className="menu-item" onClick={() => navigate("/informes")}>Informes</button>
          <button className="menu-item active" onClick={() => navigate("/admin/tipos-muestra")}>Tipos de Muestra</button>
          <button className="menu-item" onClick={() => navigate("/admin/usuarios")}>Usuarios</button>
        </div>
        <button onClick={handleLogout} className="logout-btn">Cerrar Sesión</button>
      </div>

      <div className="main-content">
        <h1 className="section-title">Tipos de Muestra</h1>
        <form onSubmit={handleSubmit} className="adminmuestras-form">
          {['tipo', 'parametro', 'unidad', 'metodo', 'tecnica', 'precio'].map((field) => (
            <div key={field} className="form-field">
              <div className="input-icon-wrapper">
                {errors[field] && <p className="input-error">{errors[field]}</p>}
                {{
                  tipo: <FaClipboardList />,
                  parametro: <FaPen />,
                  unidad: <FaRuler />,
                  metodo: <FaFlask />,
                  tecnica: <FaFlask />,
                  precio: <FaMoneyBill />
                }[field]}
                {field === 'tipo' ? (
                  <select name="tipo" value={form.tipo} onChange={handleChange}>
                    <option value="">Seleccionar tipo de muestra</option>
                    <option value="agua">Agua</option>
                    <option value="ruido">Ruido</option>
                    <option value="emisiones">Emisiones</option>
                    <option value="logistica">Logística</option>
                  </select>
                ) : field === 'unidad' ? (
                  <select name="unidad" value={form.unidad} onChange={handleChange}>
                    <option value="">Seleccionar unidad</option>
                    <option value="mg/l">mg/l</option>
                    <option value="NMP/100 ml">NMP/100 ml</option>
                    <option value="AUSENCIA">AUSENCIA</option>
                    <option value="Presencia/Ausencia">Presencia/Ausencia</option>
                    <option value="U pH">U pH</option>
                    <option value="uS/cm">uS/cm</option>
                  </select>
                ) : (
                  <input
                    name={field}
                    type={field === 'precio' ? 'number' : 'text'}
                    step={field === 'precio' ? '0.01' : undefined}
                    value={form[field]}
                    onChange={handleChange}
                    placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
                  />
                )}
              </div>
            </div>
          ))}
          <button type="submit" className="add-button">
            <FaPlus style={{ marginRight: "6px" }} />
            {editId ? "Actualizar" : "Agregar"}
          </button>
        </form>

        <div className="adminmuestras-list">
          <h2>Lista de Tipos de Muestra</h2>
          <div className="card-container">
            {catalogo.map((item) => (
              <div key={item.id || item._id?.$oid} className="card-item">
                <h3 className="card-title">{item.tipo?.toUpperCase?.()}</h3>
                <p><strong>Parámetro:</strong> {item.parametro}</p>
                <p><strong>Unidad:</strong> {item.unidad}</p>
                <p><strong>Método:</strong> {item.metodo}</p>
                <p><strong>Técnica:</strong> {item.tecnica}</p>
                <p><strong>Precio:</strong> ${parseFloat(item.precio).toFixed(2)}</p>
                <div className="card-actions">
                  <button className="edit-button" onClick={() => handleEdit(item)}><FaEdit /></button>
                  <button className="delete-button" onClick={() => handleDelete(item.id || item._id?.$oid)}><FaTrash /></button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
