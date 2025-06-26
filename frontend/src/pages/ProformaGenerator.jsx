import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ProformaGenerator.css";
import Cookies from "js-cookie";
import { CheckCircle, AlertCircle, Info, Trash2, FileDown } from "lucide-react";

const ProformaGenerator = () => {
  const navigate = useNavigate();
  const role = localStorage.getItem("userRole");

  // Notificaciones tipo toast stack (apiladas arriba)
  const [notifications, setNotifications] = useState([]);
  const showNotification = (type, message, time = 3500) => {
    const id = Date.now() + Math.random();
    setNotifications((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, time);
  };

  // --- ESTADOS ---
  const [clientData, setClientData] = useState({
    nombre: "",
    fecha: "",
    ruc: "",
    telefono: "",
    direccion: "",
    correo: "",
    contacto: "",
  });

  const [sections, setSections] = useState({
    agua: [],
    emisiones: [],
    ruido: [],
    logistica: [],
  });

  const [tiposMuestra, setTiposMuestra] = useState([]);
  const [lastProforma, setLastProforma] = useState(null);

  // --- Cargar Tipos de Muestra ---
  useEffect(() => {
    const fetchTiposMuestra = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/tipos-muestra/");
        const data = await res.json();
        setTiposMuestra(data);
      } catch (err) {
        showNotification("error", "Error cargando tipos de muestra");
      }
    };
    fetchTiposMuestra();
  }, []);

  // --- Cambiar datos de cliente ---
  const handleClientDataChange = (field, value) => {
    setClientData((prev) => ({ ...prev, [field]: value }));
  };

  // --- Limpiar todo (cliente y análisis) ---
  const handleClear = () => {
    setClientData({
      nombre: "",
      fecha: "",
      ruc: "",
      telefono: "",
      direccion: "",
      correo: "",
      contacto: "",
    });
    setSections({ agua: [], emisiones: [], ruido: [], logistica: [] });
    setLastProforma(null);
    showNotification("info", "Todos los campos fueron limpiados");
  };

  // --- Limpiar solo datos del cliente ---
  const handleNew = () => {
    setClientData({
      nombre: "",
      fecha: "",
      ruc: "",
      telefono: "",
      direccion: "",
      correo: "",
      contacto: "",
    });
    setLastProforma(null);
    showNotification("info", "Campos del cliente limpios");
  };

  // --- Cambiar datos de análisis ---
  const updateAnalysis = (type, id, field, value) => {
    setSections((prev) => ({
      ...prev,
      [type]: prev[type].map((item) =>
        item.id === id
          ? field
            ? { ...item, [field]: value }
            : { ...item, ...value }
          : item
      ),
    }));
  };

  const handleTipoSeleccionado = (type, id, tipoId) => {
    const tipo = tiposMuestra.find((t) => t.id === tipoId);
    if (!tipo) return;
    const updatedFields = {
      tipoId,
      tipo: tipo.tipo,
      parametro: tipo.parametro,
      parametroNombre: tipo.parametro,
      unidad: tipo.unidad,
      metodo: tipo.metodo,
      metodoNombre: tipo.metodo,
      tecnica: tipo.tecnica,
      tecnicaNombre: tipo.tecnica,
      precio: tipo.precio,
      cantidad: 1,
    };
    updateAnalysis(type, id, null, updatedFields);
  };

  const addAnalysis = (type) => {
    const newEntry = {
      id: Date.now(),
      tipoId: "",
      parametro: "",
      unidad: "",
      metodo: "",
      tecnica: "",
      precio: "",
      cantidad: 1,
    };
    setSections((prev) => ({ ...prev, [type]: [...prev[type], newEntry] }));
  };

  // --- Eliminar un análisis ---
  const removeAnalysis = (type, id) => {
    setSections((prev) => ({
      ...prev,
      [type]: prev[type].filter((item) => item.id !== id),
    }));
  };

  // --- Validación y Guardado ---
  const handleSave = async () => {
    if (!clientData.nombre || !clientData.fecha || !clientData.ruc) {
      showNotification("error", "Por favor, completa los datos obligatorios del cliente");
      return;
    }
    const allAnalyses = [
      ...sections.agua,
      ...sections.emisiones,
      ...sections.ruido,
      ...sections.logistica,
    ];
    if (allAnalyses.length === 0) {
      showNotification("error", "Debe agregar al menos un análisis");
      return;
    }
    if (allAnalyses.some((a) => !a.tipoId)) {
      showNotification("error", "Complete todos los análisis seleccionando un tipo de muestra");
      return;
    }
    try {
      await fetch("http://localhost:8000/api/csrf/", { credentials: "include" });
      const csrfToken = Cookies.get("csrftoken");
      if (!csrfToken) {
        showNotification("error", "No se pudo obtener el token CSRF");
        return;
      }

      const clientPayload = {
        name: clientData.nombre,
        ruc: clientData.ruc,
        phone: clientData.telefono,
        address: clientData.direccion,
        email: clientData.correo,
        contact_person: clientData.contacto,
      };
      const clientRes = await fetch("http://localhost:8000/api/clients/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        credentials: "include",
        body: JSON.stringify(clientPayload),
      });
      if (!clientRes.ok) {
        const error = await clientRes.json();
        showNotification("error", "Error al guardar cliente: " + JSON.stringify(error));
        return;
      }
      const client = await clientRes.json();

      const analysisPayload = allAnalyses.map((a) => ({
        parameter: a.parametro,
        unit: a.unidad,
        method: a.metodo,
        technique: a.tecnica,
        unit_price: parseFloat(a.precio),
        quantity: parseInt(a.cantidad),
      }));

      const proformaPayload = {
        client: client.id,
        date: clientData.fecha,
        status: "draft",
        created_by: localStorage.getItem("user") || "usuario",
        analysis_data: analysisPayload,
      };

      const proformaRes = await fetch("http://localhost:8000/api/proformas/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        credentials: "include",
        body: JSON.stringify(proformaPayload),
      });

      const result = await proformaRes.json();
      if (proformaRes.ok) {
        setLastProforma(result);
        showNotification("success", "¡Proforma guardada correctamente!");
      } else {
        showNotification("error", "Error al guardar: " + JSON.stringify(result));
      }
    } catch (error) {
      showNotification("error", "Error guardando proforma");
    }
  };

  // --- Renderizar análisis ---
  const renderAnalysisSection = (title, type) => (
    <div className="analysis-section">
      <h3>{title}</h3>
      {sections[type].map((entry) => (
        <div key={entry.id} className="analysis-entry">
          <div className="form-grid">
            <div className="form-group">
              <label>Tipo de Muestra</label>
              <select
                value={entry.tipoId || ""}
                onChange={(e) =>
                  handleTipoSeleccionado(type, entry.id, e.target.value)
                }
              >
                <option value="">Seleccione una opción</option>
                {tiposMuestra.map((tipo) => (
                  <option key={tipo.id} value={tipo.id}>
                    {tipo.tipo} - {tipo.parametro}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Tipo</label>
              <input type="text" value={entry.tipo || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Parámetro</label>
              <input type="text" value={entry.parametroNombre || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Método</label>
              <input type="text" value={entry.metodoNombre || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Técnica</label>
              <input type="text" value={entry.tecnicaNombre || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Precio</label>
              <input type="number" value={entry.precio} readOnly />
            </div>
            <div className="form-group">
              <label>Cantidad</label>
              <input
                type="number"
                min="1"
                value={entry.cantidad}
                onChange={(e) =>
                  updateAnalysis(type, entry.id, "cantidad", e.target.value)
                }
              />
            </div>
            <div className="form-group" style={{ display: "flex", alignItems: "center" }}>
              <button
                type="button"
                className="icon-btn"
                title="Eliminar análisis"
                onClick={() => removeAnalysis(type, entry.id)}
              >
                <Trash2 size={20} color="#e74c3c" />
              </button>
            </div>
          </div>
        </div>
      ))}
      <button className="add-analysis-btn" onClick={() => addAnalysis(type)}>
        Agregar {title}
      </button>
    </div>
  );

  // --- Logout ---
  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login");
  };

  // --- Render ---
  return (
    <>
      {/* --- Notificaciones tipo tiritas apiladas arriba --- */}
      <div className="my-toast-container">
        {notifications.map((n) => (
          <div key={n.id} className={`my-toast ${n.type}`}>
            {n.type === "success" && <CheckCircle size={22} style={{marginRight: 8}} />}
            {n.type === "error" && <AlertCircle size={22} style={{marginRight: 8}} />}
            {n.type === "info" && <Info size={22} style={{marginRight: 8}} />}
            {n.message}
          </div>
        ))}
      </div>

      <div className="container">
        <div className="sidebar">
          <div className="logo-section">
            <div className="logo">
              <img src="/logo-white.png" alt="Logo" className="logo-white" />
              ENVIRONOVALAB
            </div>
          </div>
          <div className="menu">
            <button className="menu-item" onClick={() => navigate("/dashboard")}>
              Inicio
            </button>
            <button
              className="menu-item active"
              onClick={() => navigate("/proformas")}
            >
              Proformas
            </button>
            <button className="menu-item" onClick={() => navigate("/informes")}>
              Informes
            </button>
      

          {/* Solo visible para ADMIN */}
          {role === "admin" && (
            <>
              <button className="menu-item" onClick={() => navigate("/admin/tipos-muestra")}>
                Tipos de Muestra
              </button>
              <button className="menu-item" onClick={() => navigate("/admin/usuarios")}>
                Usuarios
              </button>
            </>
          )}

          </div>
          <button onClick={handleLogout} className="logout-btn">
            Cerrar Sesión
          </button>
        </div>
        <div className="main">
          <h1 className="title">Generar Proformas</h1>
          <div className="form-card">
            <h2>Datos Cliente</h2>
            <div className="form-grid">
              <div className="form-group">
                <label>Nombre Cliente *</label>
                <input
                  type="text"
                  value={clientData.nombre}
                  onChange={(e) =>
                    handleClientDataChange("nombre", e.target.value)
                  }
                  required
                />
              </div>
              <div className="form-group">
                <label>Fecha *</label>
                <input
                  type="date"
                  value={clientData.fecha}
                  onChange={(e) =>
                    handleClientDataChange("fecha", e.target.value)
                  }
                  required
                />
              </div>
              <div className="form-group">
                <label>RUC *</label>
                <input
                  type="text"
                  value={clientData.ruc}
                  onChange={(e) => handleClientDataChange("ruc", e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Teléfono</label>
                <input
                  type="text"
                  value={clientData.telefono}
                  onChange={(e) =>
                    handleClientDataChange("telefono", e.target.value)
                  }
                />
              </div>
              <div className="form-group full">
                <label>Dirección</label>
                <input
                  type="text"
                  value={clientData.direccion}
                  onChange={(e) =>
                    handleClientDataChange("direccion", e.target.value)
                  }
                />
              </div>
              <div className="form-group">
                <label>Correo Electrónico</label>
                <input
                  type="email"
                  value={clientData.correo}
                  onChange={(e) =>
                    handleClientDataChange("correo", e.target.value)
                  }
                />
              </div>
              <div className="form-group">
                <label>Contacto</label>
                <input
                  type="text"
                  value={clientData.contacto}
                  onChange={(e) =>
                    handleClientDataChange("contacto", e.target.value)
                  }
                />
              </div>
            </div>
          </div>

          {renderAnalysisSection("Monitoreo de Agua", "agua")}
          {renderAnalysisSection("Monitoreo de Emisiones Gaseosas", "emisiones")}
          {renderAnalysisSection("Monitoreo de Ruido", "ruido")}

          <div className="button-group">
            <button className="button gray" onClick={handleNew}>
              <Info size={16} style={{marginRight: 4, marginBottom: -2}} />
              Limpiar Cliente
            </button>
            <button className="button orange" onClick={handleClear}>
              <Trash2 size={16} style={{marginRight: 4, marginBottom: -2}} />
              Limpiar Todo
            </button>
            <button className="button green" onClick={handleSave}>
              <CheckCircle size={16} style={{marginRight: 4, marginBottom: -2}} />
              Guardar
            </button>
          </div>

          {lastProforma && lastProforma.pdf_url && (
            <div style={{ marginTop: "20px" }}>
              <a
                href={`http://localhost:8000${lastProforma.pdf_url.startsWith('/') ? lastProforma.pdf_url : '/' + lastProforma.pdf_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="button blue"
                download
              >
                <FileDown size={18} style={{marginRight: 6, marginBottom: -2}} />
                Descargar PDF de Proforma
              </a>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default ProformaGenerator;
