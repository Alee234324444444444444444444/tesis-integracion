import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import Cookies from 'js-cookie';
import Sidebar from '../components/Sidebar';
import {
  ClipboardList,
  Pen,
  Ruler,
  FlaskConical,
  DollarSign,
  Plus,
  Save,
  X,
  CheckCircle,
  AlertCircle,
  Info,
  Trash
} from 'lucide-react';
import "../styles/Dashboard.css";
import "../styles/AdminMuestras.css";

export default function AdminMuestras() {
  const [catalogo, setCatalogo] = useState([]);
  const [form, setForm] = useState({ tipo: '', parametro: '', unidad: '', metodo: '', tecnica: '', precio: '' });
  const [editId, setEditId] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const showNotification = (type, message, time = 3500) => {
    const id = Date.now() + Math.random();
    setNotifications((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, time);
  };

  const fetchCatalogo = useCallback(async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/tipos-muestra/', {
        withCredentials: true,
        headers: { 'X-CSRFToken': Cookies.get('csrftoken') }
      });
      setCatalogo(res.data);
    } catch {
      showNotification("error", "Error cargando catálogo");
    }
  }, []);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        await axios.get('http://localhost:8000/api/csrf/', { withCredentials: true });
        await fetchCatalogo();
      } catch {
        showNotification("error", "Error inicial");
      }
    };
    fetchAll();
  }, [fetchCatalogo]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const camposIncompletos = () => {
    return !form.tipo || !form.parametro || !form.unidad || !form.metodo || !form.tecnica || !form.precio;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (camposIncompletos()) {
      showNotification("error", "Todos los campos son obligatorios");
      return;
    }
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
        showNotification("success", "Muestra actualizada correctamente");
      } else {
        await axios.post(`http://localhost:8000/api/tipos-muestra/`, form, config);
        showNotification("success", "Muestra agregada correctamente");
      }

      setForm({ tipo: '', parametro: '', unidad: '', metodo: '', tecnica: '', precio: '' });
      setEditId(null);
      setModalOpen(false);
      fetchCatalogo();
    } catch {
      showNotification("error", "Error al guardar muestra");
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
      showNotification("success", "Muestra eliminada correctamente");
      fetchCatalogo();
    } catch {
      showNotification("error", "Error al eliminar muestra");
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
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditId(null);
    setForm({ tipo: '', parametro: '', unidad: '', metodo: '', tecnica: '', precio: '' });
  };

  const iconMap = {
    tipo: <ClipboardList size={18} />,
    parametro: <Pen size={18} />,
    unidad: <Ruler size={18} />,
    metodo: <FlaskConical size={18} />,
    tecnica: <FlaskConical size={18} />,
    precio: <DollarSign size={18} />
  };

  const renderInput = (field) => (
    <div key={field} className="form-field">
      <div className="input-icon-wrapper">
        {iconMap[field]}
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
  );

  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="main-content">
        <div className="my-toast-container">
          {notifications.map((n) => (
            <div key={n.id} className={`my-toast ${n.type}`}>
              {n.type === "success" && <CheckCircle size={20} />}
              {n.type === "error" && <AlertCircle size={20} />}
              {n.type === "info" && <Info size={20} />}
              {n.message}
            </div>
          ))}
        </div>

        <h1 className="section-title">Tipos de Muestra</h1>

        <form onSubmit={handleSubmit} className="adminmuestras-form">
          {['tipo', 'parametro', 'unidad', 'metodo', 'tecnica', 'precio'].map(renderInput)}
          <div className="button-group">
            <button type="submit" className="add-button">
              <Plus size={18} />
              <strong>{editId ? 'Actualizar' : 'Agregar'}</strong>
            </button>
          </div>
        </form>

        {modalOpen && (
          <div className="modal-backdrop">
            <div className="modal">
              <h2>Editar Tipo de Muestra</h2>
              <form onSubmit={handleSubmit}>
                {['tipo', 'parametro', 'unidad', 'metodo', 'tecnica', 'precio'].map(renderInput)}
                <div className="button-group">
                  <button type="submit" className="add-button">
                    <Save size={18} /> Guardar
                  </button>
                  <button type="button" className="clear-button" onClick={closeModal}>
                    <X size={18} /> Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

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
                  <button className="edit-button" onClick={() => handleEdit(item)}><Pen size={16} /></button>
                  <button className="delete-button" onClick={() => handleDelete(item.id || item._id?.$oid)}><Trash size={16} /></button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
