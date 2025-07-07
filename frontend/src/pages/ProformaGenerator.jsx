// ProformaGenerator.jsx (modificado con sistema de "ítems" unificados)
import React, { useState, useEffect } from "react";
import "../styles/ProformaGenerator.css";
import Cookies from "js-cookie";
import { CheckCircle, AlertCircle, Info, Trash2, FileDown } from "lucide-react";
import Sidebar from "../components/Sidebar";

const ProformaGenerator = () => {
  const [notifications, setNotifications] = useState([]);
  const showNotification = (type, message, time = 3500) => {
    const id = Date.now() + Math.random();
    setNotifications((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, time);
  };

  const [clientData, setClientData] = useState({
    nombre: "",
    fecha: "",
    ruc: "",
    telefono: "",
    direccion: "",
    correo: "",
    contacto: "",
  });

  const [items, setItems] = useState([]);
  const [tiposMuestra, setTiposMuestra] = useState([]);
  const [lastProforma, setLastProforma] = useState(null);

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

  const handleClientDataChange = (field, value) => {
    setClientData((prev) => ({ ...prev, [field]: value }));
  };

  const handleClear = () => {
    setClientData({ nombre: "", fecha: "", ruc: "", telefono: "", direccion: "", correo: "", contacto: "" });
    setItems([]);
    setLastProforma(null);
    showNotification("info", "Todos los campos fueron limpiados");
  };

  const handleNew = () => {
    setClientData({ nombre: "", fecha: "", ruc: "", telefono: "", direccion: "", correo: "", contacto: "" });
    setLastProforma(null);
    showNotification("info", "Campos del cliente limpios");
  };

  const addItem = () => {
    const newItem = {
      id: Date.now(),
      itemNumber: items.length + 1,
      title: "",
      tipoId: "",
      parametro: "",
      unidad: "",
      metodo: "",
      tecnica: "",
      precio: "",
      cantidad: 1,
    };
    setItems((prev) => [...prev, newItem]);
  };

  const updateItem = (id, field, value) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, [field]: value } : item))
    );
  };

  const removeItem = (id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const handleTipoSeleccionado = (group, id, tipoId) => {
    const tipo = tiposMuestra.find((t) => t.id === tipoId);
    if (!tipo) return;

    const updatedFields = {
      tipoId,
      parametro: tipo.parametro,
      unidad: tipo.unidad,
      metodo: tipo.metodo,
      tecnica: tipo.tecnica,
      precio: tipo.precio,
    };

    Object.entries(updatedFields).forEach(([key, val]) => {
      updateItem(id, key, val);
    });
  };

  const handleSave = async () => {
    if (!clientData.nombre || !clientData.fecha || !clientData.ruc) {
      showNotification("error", "Por favor, completa los datos obligatorios del cliente");
      return;
    }
    if (items.length === 0) {
      showNotification("error", "Debe agregar al menos un ítem de monitoreo");
      return;
    }
    if (items.some((a) => !a.tipoId)) {
      showNotification("error", "Complete todos los ítems seleccionando un tipo de muestra");
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

      const analysisPayload = items.map((a) => ({
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

  const renderItems = () => (
    <div className="analysis-section">
      <h3>Ítems de Monitoreo</h3>
      {items.map((item) => (
        <div key={item.id} className="analysis-entry">
          <label><strong>Inicio Ítem #{item.itemNumber}</strong></label>
          <div className="form-group full">
            <label>Título del Ítem</label>
            <input
              type="text"
              value={item.title}
              onChange={(e) => updateItem(item.id, "title", e.target.value)}
            />
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label>Tipo de Muestra</label>
              <select
                value={item.tipoId || ""}
                onChange={(e) => handleTipoSeleccionado("general", item.id, e.target.value)}
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
              <label>Parámetro</label>
              <input type="text" value={item.parametro || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Método</label>
              <input type="text" value={item.metodo || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Técnica</label>
              <input type="text" value={item.tecnica || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Unidad</label>
              <input type="text" value={item.unidad || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Precio</label>
              <input type="number" value={item.precio || ""} readOnly />
            </div>
            <div className="form-group">
              <label>Cantidad</label>
              <input
                type="number"
                min="1"
                value={item.cantidad}
                onChange={(e) => updateItem(item.id, "cantidad", e.target.value)}
              />
            </div>
            <div className="form-group" style={{ display: "flex", alignItems: "center" }}>
              <button
                type="button"
                className="icon-btn"
                title="Eliminar análisis"
                onClick={() => removeItem(item.id)}
              >
                <Trash2 size={20} color="#e74c3c" />
              </button>
            </div>
          </div>
        </div>
      ))}
      <button className="add-analysis-btn" onClick={addItem}>
        Agregar Ítem de Monitoreo
      </button>
    </div>
  );

  return (
    <>
      <div className="my-toast-container">
        {notifications.map((n) => (
          <div key={n.id} className={`my-toast ${n.type}`}>
            {n.type === "success" && <CheckCircle size={22} style={{ marginRight: 8 }} />}
            {n.type === "error" && <AlertCircle size={22} style={{ marginRight: 8 }} />}
            {n.type === "info" && <Info size={22} style={{ marginRight: 8 }} />}
            {n.message}
          </div>
        ))}
      </div>
      <div className="container">
        <Sidebar />
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
                  onChange={(e) => handleClientDataChange("nombre", e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Fecha *</label>
                <input
                  type="date"
                  value={clientData.fecha}
                  onChange={(e) => handleClientDataChange("fecha", e.target.value)}
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
                  onChange={(e) => handleClientDataChange("telefono", e.target.value)}
                />
              </div>
              <div className="form-group full">
                <label>Dirección</label>
                <input
                  type="text"
                  value={clientData.direccion}
                  onChange={(e) => handleClientDataChange("direccion", e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Correo Electrónico</label>
                <input
                  type="email"
                  value={clientData.correo}
                  onChange={(e) => handleClientDataChange("correo", e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Contacto</label>
                <input
                  type="text"
                  value={clientData.contacto}
                  onChange={(e) => handleClientDataChange("contacto", e.target.value)}
                />
              </div>
            </div>
          </div>

          {renderItems()}

          <div className="button-group">
            <button className="button gray" onClick={handleNew}>
              <Info size={16} style={{ marginRight: 4, marginBottom: -2 }} />
              Limpiar Cliente
            </button>
            <button className="button orange" onClick={handleClear}>
              <Trash2 size={16} style={{ marginRight: 4, marginBottom: -2 }} />
              Limpiar Todo
            </button>
            <button className="button green" onClick={handleSave}>
              <CheckCircle size={16} style={{ marginRight: 4, marginBottom: -2 }} />
              Guardar
            </button>
          </div>

          {lastProforma && lastProforma.pdf_url && (
            <div style={{ marginTop: "20px" }}>
              <a
                href={`http://localhost:8000${lastProforma.pdf_url.startsWith("/") ? lastProforma.pdf_url : "/" + lastProforma.pdf_url}`}
                target="_blank"
                rel="noopener noreferrer"
                className="button blue"
                download
              >
                <FileDown size={18} style={{ marginRight: 6, marginBottom: -2 }} />
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