// Archivo: pages/ProformaGenerator.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/ProformaGenerator.css'; // Asegúrate de tener este archivo CSS
import Cookies from 'js-cookie';

const ProformaGenerator = () => {
  const navigate = useNavigate();

  const [clientData, setClientData] = useState({
    nombre: '', fecha: '', ruc: '', telefono: '', direccion: '', correo: '', contacto: ''
  });

  const [sections, setSections] = useState({
    agua: [], emisiones: [], ruido: [], logistica: []
  });

  const handleClientDataChange = (field, value) => {
    setClientData(prev => ({ ...prev, [field]: value }));
  };

  const handleNew = () => {
    setClientData({ nombre: '', fecha: '', ruc: '', telefono: '', direccion: '', correo: '', contacto: '' });
    setSections({ agua: [], emisiones: [], ruido: [], logistica: [] });
  };

  const handleSave = async () => {
  try {
    // ✅ Paso 1: fuerza a Django a mandar la cookie CSRF
    await fetch('http://localhost:8000/api/csrf/', {
      credentials: 'include'
    });

    // ✅ Paso 2: ahora sí puedes leer el token
    const csrfToken = Cookies.get('csrftoken');

    if (!csrfToken) {
      alert("No se pudo obtener el token CSRF");
      return;
    }

    const clientPayload = {
      name: clientData.nombre,
      ruc: clientData.ruc,
      phone: clientData.telefono,
      address: clientData.direccion,
      email: clientData.correo,
      contact_person: clientData.contacto
    };

    // Crear cliente
    const clientRes = await fetch('http://localhost:8000/api/clients/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'include',
      body: JSON.stringify(clientPayload)
    });

    if (!clientRes.ok) {
  const error = await clientRes.json();
  console.error("Error al guardar cliente:", error);
  alert("Error al guardar cliente: " + JSON.stringify(error));
  return; // Detiene la ejecución si falla
}

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
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'include',
      body: JSON.stringify(proformaPayload)
    });

    if (proformaRes.ok) {
      const result = await proformaRes.json();
      alert("Proforma guardada correctamente");
      console.log(result);
    } else {
      const error = await proformaRes.json();
      alert("Error al guardar: " + JSON.stringify(error));
    }

  } catch (error) {
    console.error("Error guardando proforma:", error);
    alert("Error al guardar la proforma");
  }
};

  const handlePreview = async () => {
  try {
    const idProforma = prompt("Ingrese ID de la proforma a previsualizar:");
    if (!idProforma) return;

    const response = await fetch(`http://localhost:8000/api/proformas/${idProforma}/preview/`);
    const html = await response.text();
    const previewWindow = window.open('', '_blank');
    previewWindow.document.open();
    previewWindow.document.write(html);
    previewWindow.document.close();
  } catch (err) {
    console.error("Error generando preview:", err);
    alert("Error generando la vista previa");
  }
};

  const handlePreviewSinGuardar = async () => {
    try {
      const csrfToken = Cookies.get('csrftoken');

      const clientPayload = {
        name: clientData.nombre,
        ruc: clientData.ruc,
        phone: clientData.telefono,
        address: clientData.direccion,
        email: clientData.correo,
        contact_person: clientData.contacto
      };

      const allAnalyses = [...sections.agua, ...sections.emisiones, ...sections.ruido, ...sections.logistica];
      const analysisPayload = allAnalyses.map(a => ({
        parameter: a.parametro,
        unit: a.unidad,
        method: a.metodo,
        technique: a.tecnica,
        unit_price: parseFloat(a.precio),
        quantity: parseInt(a.cantidad)
      }));

      const bodyData = {
        client_data: clientPayload,
        date: clientData.fecha,
        analysis_data: analysisPayload
      };

      const res = await fetch('http://localhost:8000/api/proformas/preview_temp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        credentials: 'include',
        body: JSON.stringify(bodyData)
      });

      const html = await res.text();
      const previewWindow = window.open('', '_blank');
      previewWindow.document.open();
      previewWindow.document.write(html);
      previewWindow.document.close();

    } catch (err) {
      console.error("Error al generar vista previa temporal:", err);
      alert("Error al generar previsualización sin guardar.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login");
  };

  const addAnalysis = (type) => {
    const newEntry = {
      id: Date.now(), parametro: '', unidad: '', metodo: '', tecnica: '', precio: '', cantidad: 1
    };
    setSections(prev => ({ ...prev, [type]: [...prev[type], newEntry] }));
  };

  const updateAnalysis = (type, id, field, value) => {
    setSections(prev => ({
      ...prev,
      [type]: prev[type].map(item => item.id === id ? { ...item, [field]: value } : item)
    }));
  };

  const renderAnalysisSection = (title, type) => (
    <div className="analysis-section">
      <h3>{title}</h3>
      {sections[type].map(entry => (
        <div key={entry.id} className="analysis-entry">
          <div className="form-grid">
            <div className="form-group">
              <label>Parámetro</label>
              <input type="text" value={entry.parametro} onChange={(e) => updateAnalysis(type, entry.id, 'parametro', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Unidad</label>
              <input type="text" value={entry.unidad} onChange={(e) => updateAnalysis(type, entry.id, 'unidad', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Método</label>
              <input type="text" value={entry.metodo} onChange={(e) => updateAnalysis(type, entry.id, 'metodo', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Técnica</label>
              <input type="text" value={entry.tecnica} onChange={(e) => updateAnalysis(type, entry.id, 'tecnica', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Precio</label>
              <input type="number" value={entry.precio} onChange={(e) => updateAnalysis(type, entry.id, 'precio', e.target.value)} />
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
        <button onClick={handleLogout} className="logout-btn">Cerrar Sesión</button>
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
          <button className="button blue" onClick={handlePreviewSinGuardar}>Previsualizar</button>
        </div>
      </div>
    </div>
  );
};

export default ProformaGenerator;
