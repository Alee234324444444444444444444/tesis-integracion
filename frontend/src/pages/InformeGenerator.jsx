import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";
import {
  CheckCircle,
  AlertCircle,
  Info,
  FileDown,
  Search,
  RefreshCw,
  User,
  Calendar,
  ClipboardList,
  FlaskConical,
  Pencil,
  Ruler,
  HelpCircle,
  ZoomIn,
  LineChart
} from "lucide-react";
import "../styles/InformeGenerator.css";

const InformeGenerator = () => {
  const navigate = useNavigate();
  const role = localStorage.getItem("userRole");
  const [notifications, setNotifications] = useState([]);
  const [query, setQuery] = useState("");
  const [proformas, setProformas] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [selectedProforma, setSelectedProforma] = useState(null);
  const [form, setForm] = useState({ tomadoPor: "", procedimiento: "" });
  const [analisis, setAnalisis] = useState([]);
  const [informeGuardado, setInformeGuardado] = useState(false);

  const showNotification = (type, message, time = 3500) => {
    const id = Date.now() + Math.random();
    setNotifications((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, time);
  };

  useEffect(() => {
    fetch("http://localhost:8000/api/proformas/")
      .then((res) => res.json())
      .then((data) => setProformas(data));
  }, []);

  const handleSearch = () => {
    const lower = query.toLowerCase();
    const results = proformas.filter(
      (p) =>
        p.proforma_number.toLowerCase().includes(lower) ||
        p.client_name.toLowerCase().includes(lower)
    );
    if (!results.length) {
      showNotification("info", "No se encontró ninguna proforma");
    }
    setFiltered(results);
  };

  const handleSelect = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/api/proformas/${id}/informe/`);
      const data = await res.json();
      setSelectedProforma({ ...data, id });
      setForm({ tomadoPor: "", procedimiento: "" });
      const analisisMapeado = data.analysis_data.map((item) => ({
        ...item,
        resultados: "",
        incertidumbre: "",
        limite: "",
      }));
      setAnalisis(analisisMapeado);
      setInformeGuardado(false);
    } catch (err) {
      showNotification("error", "Error al cargar la proforma");
    }
  };

  const updateField = (index, field, value) => {
    setAnalisis((prev) => {
      const copy = [...prev];
      copy[index][field] = value;
      return copy;
    });
  };

  const camposClienteIncompletos = () => {
    return !form.tomadoPor.trim() || !form.procedimiento.trim();
  };

  const analisisIncompleto = () => {
    return analisis.some(
      (a) =>
        !a.resultados.trim() ||
        !a.limite.trim() ||
        !a.incertidumbre.trim()
    );
  };

  const handleGuardar = async () => {
    if (!selectedProforma) return showNotification("error", "Seleccione una proforma primero");

    if (camposClienteIncompletos() || analisisIncompleto()) {
      showNotification("error", "Faltan campos obligatorios del cliente o del análisis");
      return;
    }

    try {
      await fetch("http://localhost:8000/api/csrf/", { credentials: "include" });
      const csrfToken = Cookies.get("csrftoken");
      if (!csrfToken) {
        showNotification("error", "No se pudo obtener el token CSRF");
        return;
      }

      const payload = {
        proforma: selectedProforma.id,
        fecha_emision: selectedProforma.date.slice(0, 10),
        analizado_por: selectedProforma.created_by,
        tomado_por: form.tomadoPor,
        procedimiento: form.procedimiento,
        resultados: analisis.map((a) => ({
          parameter: a.parameter,
          unit: a.unit,
          method: a.method,
          resultados: a.resultados,
          limite: a.limite,
          incertidumbre: a.incertidumbre,
        })),
      };

      const res = await fetch("http://localhost:8000/api/informes/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      await res.json();
      if (res.ok) {
        showNotification("success", "Informe guardado correctamente");
        setInformeGuardado(true);
      } else {
        showNotification("error", "Error al guardar el informe");
        setInformeGuardado(false);
      }
    } catch (err) {
      showNotification("error", "Error guardando informe");
      setInformeGuardado(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login");
  };

  const renderInputWithIcon = (Icon, props) => (
    <div className="input-icon-container">
      <Icon size={16} className="input-icon" />
      <input {...props} />
    </div>
  );

  return (
    <>
      <div className="my-toast-container">
        {notifications.map((n) => (
          <div key={n.id} className={`my-toast ${n.type}`}>
            {n.type === "success" && <CheckCircle size={20} style={{ marginRight: 8 }} />}
            {n.type === "error" && <AlertCircle size={20} style={{ marginRight: 8 }} />}
            {n.type === "info" && <Info size={20} style={{ marginRight: 8 }} />}
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
            <button className="menu-item" onClick={() => navigate("/dashboard")}>Inicio</button>
            <button className="menu-item" onClick={() => navigate("/proformas")}>Proformas</button>
            <button className="menu-item active">Informes</button>
            
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
          <button className="logout-btn" onClick={handleLogout}>Cerrar Sesión</button>
        </div>

        <div className="main">
          <h1 className="title">Generar Informes</h1>

          <div className="form-card">
            <h2>Buscar Proforma</h2>
            <div className="form-grid">
              <div className="form-group full">
                <label>Buscar por N° o cliente</label>
                <div className="search-row">
                  {renderInputWithIcon(Search, {
                    type: "text",
                    value: query,
                    onChange: (e) => setQuery(e.target.value),
                    placeholder: "Ej: PRF-0023 o Juan",
                  })}
                  <button className="search-button" onClick={handleSearch}><Search size={18} /></button>
                </div>
              </div>
            </div>

            {filtered.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <label><strong>Resultados:</strong></label>
                <ul style={{ listStyle: "none", paddingLeft: 0 }}>
                  {filtered.map((p) => (
                    <li key={p.id}>
                      <button
                        className="button gray"
                        style={{ marginTop: 8 }}
                        onClick={() => handleSelect(p.id)}
                      >
                        {p.proforma_number} - {p.client_name}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {selectedProforma && (
            <>
              <div className="form-card">
                <h2>Datos del Cliente</h2>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Cliente</label>
                    {renderInputWithIcon(User, { type: "text", value: selectedProforma.client_name, readOnly: true })}
                  </div>
                  <div className="form-group">
                    <label>Fecha de Emisión</label>
                    {renderInputWithIcon(Calendar, { type: "date", value: selectedProforma.date.slice(0, 10), readOnly: true })}
                  </div>
                  <div className="form-group">
                    <label>Muestra tomada por</label>
                    {renderInputWithIcon(Pencil, {
                      type: "text",
                      value: form.tomadoPor,
                      onChange: (e) => setForm({ ...form, tomadoPor: e.target.value }),
                    })}
                  </div>
                  <div className="form-group">
                    <label>Procedimiento</label>
                    {renderInputWithIcon(ClipboardList, {
                      type: "text",
                      value: form.procedimiento,
                      onChange: (e) => setForm({ ...form, procedimiento: e.target.value }),
                    })}
                  </div>
                  <div className="form-group">
                    <label>Analizado por</label>
                    {renderInputWithIcon(FlaskConical, { type: "text", value: selectedProforma.created_by, readOnly: true })}
                  </div>
                </div>
              </div>

              <div className="form-card">
                <h2>Resultados del Análisis</h2>
                {analisis.map((a, index) => (
                  <div key={index} className="analysis-entry">
                    <div className="form-grid">
                      <div className="form-group">
                        <label>Parámetro</label>
                        {renderInputWithIcon(HelpCircle, { type: "text", value: a.parameter, readOnly: true })}
                      </div>
                      <div className="form-group">
                        <label>Unidad</label>
                        {renderInputWithIcon(Ruler, { type: "text", value: a.unit, readOnly: true })}
                      </div>
                      <div className="form-group">
                        <label>Método</label>
                        {renderInputWithIcon(ZoomIn, { type: "text", value: a.method, readOnly: true })}
                      </div>
                      <div className="form-group">
                        <label>Resultado</label>
                        {renderInputWithIcon(LineChart, {
                          type: "text",
                          value: a.resultados,
                          onChange: (e) => updateField(index, "resultados", e.target.value),
                        })}
                      </div>
                      <div className="form-group">
                        <label>Límite</label>
                        {renderInputWithIcon(Ruler, {
                          type: "text",
                          value: a.limite,
                          onChange: (e) => updateField(index, "limite", e.target.value),
                        })}
                      </div>
                      <div className="form-group">
                        <label>Incertidumbre</label>
                        {renderInputWithIcon(Info, {
                          type: "text",
                          value: a.incertidumbre,
                          onChange: (e) => updateField(index, "incertidumbre", e.target.value),
                        })}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="button-group">
                <button className="button green" onClick={handleGuardar}>
                  <CheckCircle size={16} style={{ marginRight: 4, marginBottom: -2 }} />
                  Guardar Informe
                </button>

                {informeGuardado && (
                  <a
                    href={`http://localhost:8000/api/proformas/${selectedProforma.id}/informe_pdf/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="button blue"
                  >
                    <FileDown size={18} style={{ marginRight: 6, marginBottom: -2 }} />
                    Descargar PDF
                  </a>
                )}

                <button
                  className="button gray"
                  onClick={() => {
                    setSelectedProforma(null);
                    setQuery("");
                    setFiltered([]);
                    setAnalisis([]);
                    setForm({ tomadoPor: "", procedimiento: "" });
                    setInformeGuardado(false);
                    showNotification("info", "Campos limpiados");
                  }}
                >
                  <RefreshCw size={16} style={{ marginRight: 4, marginBottom: -2 }} />
                  Limpiar Todo
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
};

export default InformeGenerator;
