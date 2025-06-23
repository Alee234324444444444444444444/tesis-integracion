import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ProformaGenerator.css";
import Cookies from "js-cookie";

const ProformaGenerator = () => {
  const navigate = useNavigate();

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

  useEffect(() => {
    const fetchTiposMuestra = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/tipos-muestra/");
        const data = await res.json();
        setTiposMuestra(data);
      } catch (err) {
        console.error("Error cargando tipos de muestra:", err);
      }
    };
    fetchTiposMuestra();
  }, []);

  const handleClientDataChange = (field, value) => {
    setClientData((prev) => ({ ...prev, [field]: value }));
  };

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
    setSections({ agua: [], emisiones: [], ruido: [], logistica: [] });
  };

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
      unidad: tipo.unidad,
      metodo: tipo.metodo,
      tecnica: tipo.tecnica,
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

  const handleSave = async () => {
    try {
      await fetch("http://localhost:8000/api/csrf/", {
        credentials: "include",
      });
      const csrfToken = Cookies.get("csrftoken");
      if (!csrfToken) return alert("No se pudo obtener el token CSRF");

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
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify(clientPayload),
      });

      if (!clientRes.ok) {
        const error = await clientRes.json();
        alert("Error al guardar cliente: " + JSON.stringify(error));
        return;
      }

      const client = await clientRes.json();

      const allAnalyses = [
        ...sections.agua,
        ...sections.emisiones,
        ...sections.ruido,
        ...sections.logistica,
      ];
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
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify(proformaPayload),
      });

      const result = await proformaRes.json();
      if (proformaRes.ok) {
        alert("Proforma guardada correctamente");
        console.log(result);
      } else {
        alert("Error al guardar: " + JSON.stringify(result));
      }
    } catch (error) {
      console.error("Error guardando proforma:", error);
      alert("Error al guardar la proforma");
    }
  };

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
                    {tipo.parametro} - {tipo.metodo}
                  </option>
                ))}
              </select>
            </div>
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
              <input type="text" value={entry.tipo} readOnly />
            </div>
            <div className="form-group">
              <label>Parámetro</label>
              <input type="text" value={entry.parametro} readOnly />
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
              <input
                type="number"
                min="1"
                value={entry.cantidad}
                onChange={(e) =>
                  updateAnalysis(type, entry.id, "cantidad", e.target.value)
                }
              />
            </div>
          </div>
        </div>
      ))}
      <button className="add-analysis-btn" onClick={() => addAnalysis(type)}>
        Agregar {title}
      </button>
    </div>
  );

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login");
  };

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
          <button className="menu-item" onClick={() => navigate("/dashboard")}>
            Inicio
          </button>
          <button
            className="menu-item active"
            onClick={() => navigate("/proformas")}
          >
            Proformas
          </button>
          <button
            className="menu-item"
            onClick={() => console.log("Ir a Informes")}
          >
            Informes
          </button>
          <button
            className="menu-item"
            onClick={() => console.log("Ir a Admin")}
          >
            Administrar Documentos
          </button>
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
              <label>Nombre Cliente</label>
              <input
                type="text"
                value={clientData.nombre}
                onChange={(e) =>
                  handleClientDataChange("nombre", e.target.value)
                }
              />
            </div>
            <div className="form-group">
              <label>Fecha</label>
              <input
                type="date"
                value={clientData.fecha}
                onChange={(e) =>
                  handleClientDataChange("fecha", e.target.value)
                }
              />
            </div>
            <div className="form-group">
              <label>RUC</label>
              <input
                type="text"
                value={clientData.ruc}
                onChange={(e) => handleClientDataChange("ruc", e.target.value)}
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
            Nuevo
          </button>
          <button className="button green" onClick={handleSave}>
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProformaGenerator;
