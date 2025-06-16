import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ProformaGenerator.css';
import Cookies from 'js-cookie';

const ProformaGenerator = () => {
  const navigate = useNavigate();

  const [clientData, setClientData] = useState({
    nombre: '', fecha: '', ruc: '', telefono: '', direccion: '', correo: '', contacto: ''
  });

  const [catalogo, setCatalogo] = useState({ agua: [], emisiones: [], ruido: [], logistica: [] });
  const [sections, setSections] = useState({ agua: [], emisiones: [], ruido: [], logistica: [] });

  useEffect(() => {
    fetchCatalogo();
  }, []);

  const fetchCatalogo = async () => {
    const tipos = ["agua", "emisiones", "ruido", "logistica"];
    const base = 'http://localhost:8000/api/catalogo-analisis/?tipo=';
    const all = {};
    for (const tipo of tipos) {
      const res = await fetch(base + tipo, { credentials: 'include' });
      const data = await res.json();
      all[tipo] = data;
    }
    setCatalogo(all);
  };

  const handleClientDataChange = (field, value) => {
    setClientData(prev => ({ ...prev, [field]: value }));
  };

  const handleNew = () => {
    setClientData({ nombre: '', fecha: '', ruc: '', telefono: '', direccion: '', correo: '', contacto: '' });
    setSections({ agua: [], emisiones: [], ruido: [], logistica: [] });
  };

  const handleSave = async () => {
    try {
      await fetch('http://localhost:8000/api/csrf/', { credentials: 'include' });
      const csrfToken = Cookies.get('csrftoken');
      if (!csrfToken) return alert("No se pudo obtener el token CSRF");

      const clientPayload = {
        name: clientData.nombre,
        ruc: clientData.ruc,
        phone: clientData.telefono,
        address: clientData.direccion,
        email: clientData.correo,
        contact_person: clientData.contacto
      };

      const clientRes = await fetch('http://localhost:8000/api/clients/', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        credentials: 'include', body: JSON.stringify(clientPayload)
      });
      if (!clientRes.ok) return alert("Error al guardar cliente");
      const client = await clientRes.json();

      const allAnalyses = [...sections.agua, ...sections.emisiones, ...sections.ruido, ...sections.logistica];
      const analysisPayload = allAnalyses.map(a => ({
        parameter: a.parametro,
        unit: a.unidad,
        method: a.metodo,
        technique: a.tecnica,
        unit_price: parseFloat(a.precio),
        quantity: parseInt(a.cantidad)
      }));

      const proformaPayload = {
        client: client.id,
        date: clientData.fecha,
        status: "draft",
        created_by: localStorage.getItem("user") || "usuario",
        analysis_data: analysisPayload
      };

      const proformaRes = await fetch('http://localhost:8000/api/proformas/', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        credentials: 'include', body: JSON.stringify(proformaPayload)
      });

      if (proformaRes.ok) alert("Proforma guardada correctamente");
      else alert("Error al guardar la proforma");
    } catch (error) {
      console.error("Error guardando proforma:", error);
      alert("Error al guardar la proforma");
    }
  };

  const addAnalysis = (type) => {
    const newEntry = { id: Date.now(), catalogoId: '', parametro: '', unidad: '', metodo: '', tecnica: '', precio: '', cantidad: 1 };
    setSections(prev => ({ ...prev, [type]: [...prev[type], newEntry] }));
  };

  const updateAnalysis = (type, id, field, value) => {
    setSections(prev => ({
      ...prev,
      [type]: prev[type].map(item => {
        if (item.id === id) {
          if (field === 'catalogoId') {
            const found = catalogo[type].find(c => c.id === value);
            return found ? {
              ...item,
              catalogoId: value,
              parametro: found.parametro,
              unidad: found.unidad,
              metodo: found.metodo,
              tecnica: found.tecnica,
              precio: found.precio
            } : item;
          }
          return { ...item, [field]: value };
        }
        return item;
      })
    }));
  };

  const renderAnalysisSection = (title, type) => (
    <div className="analysis-section">
      <h3>{title}</h3>
      {sections[type].map(entry => (
        <div key={entry.id} className="analysis-entry">
          <div className="form-grid">
            <div className="form-group">
              <label>Catálogo</label>
              <select value={entry.catalogoId} onChange={e => updateAnalysis(type, entry.id, 'catalogoId', e.target.value)}>
                <option value="">-- Seleccionar --</option>
                {catalogo[type].map(item => (
                  <option key={item.id} value={item.id}>{item.parametro} - ${item.precio}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Unidad</label>
              <input type="text" value={entry.unidad} readOnly />
            </div>
            <div className="form-group">
              <label>Método</label>
              <input type="text" value={entry.metodo} readOnly />
            </div>
            <div className="form-group">
              <label>Técnica</label>
              <input type="text" value={entry.tecnica} readOnly />
            </div>
            <div className="form-group">
              <label>Precio</label>
              <input type="number" value={entry.precio} readOnly />
            </div>
            <div className="form-group">
              <label>Cantidad</label>
              <input type="number" min="1" value={entry.cantidad} onChange={(e) => updateAnalysis(type, entry.id, 'cantidad', e.target.value)} />
            </div>
          </div>
        </div>
      ))}
      <button className="add-analysis-btn" onClick={() => addAnalysis(type)}>Agregar {title}</button>
    </div>
  );

  return (
    <div className="container">
      <div className="sidebar">
        <div className="logo-section">
          <div className="logo">
            <img src="/logo-white.png" alt="Logo" className="logo-white" />
            ENVIRONOVALAB
          </div>
        </div>
        <div className="menu">
          <button className="menu-item" onClick={() => navigate("/dashboard")}>Inicio</button>
          <button className="menu-item active" onClick={() => navigate("/proformas")}>Proformas</button>
          <button className="menu-item" onClick={() => console.log("Ir a Informes")}>Informes</button>
          <button className="menu-item" onClick={() => console.log("Ir a Admin")}>Administrar Documentos</button>
        </div>
        <button onClick={() => navigate("/login")} className="logout-btn">Cerrar Sesión</button>
      </div>
      <div className="main">
        <h1 className="title">Generar Proformas</h1>
        <div className="form-card">
          <h2>Datos Cliente</h2>
          <div className="form-grid">
            <div className="form-group">
              <label>Nombre Cliente</label>
              <input type="text" value={clientData.nombre} onChange={(e) => handleClientDataChange('nombre', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Fecha</label>
              <input type="date" value={clientData.fecha} onChange={(e) => handleClientDataChange('fecha', e.target.value)} />
            </div>
            <div className="form-group">
              <label>RUC</label>
              <input type="text" value={clientData.ruc} onChange={(e) => handleClientDataChange('ruc', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Teléfono</label>
              <input type="text" value={clientData.telefono} onChange={(e) => handleClientDataChange('telefono', e.target.value)} />
            </div>
            <div className="form-group full">
              <label>Dirección</label>
              <input type="text" value={clientData.direccion} onChange={(e) => handleClientDataChange('direccion', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Correo Electrónico</label>
              <input type="email" value={clientData.correo} onChange={(e) => handleClientDataChange('correo', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Contacto</label>
              <input type="text" value={clientData.contacto} onChange={(e) => handleClientDataChange('contacto', e.target.value)} />
            </div>
          </div>
        </div>

        {renderAnalysisSection('Monitoreo de Agua', 'agua')}
        {renderAnalysisSection('Monitoreo de Emisiones Gaseosas', 'emisiones')}
        {renderAnalysisSection('Monitoreo de Ruido', 'ruido')}

        <div className="button-group">
          <button className="button gray" onClick={handleNew}>Nuevo</button>
          <button className="button green" onClick={handleSave}>Guardar</button>
        </div>
      </div>
    </div>
  );
};

export default ProformaGenerator;
