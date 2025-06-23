import React, { useState, useEffect } from "react";
import "../styles/ProformaGenerator.css";
import { useNavigate } from "react-router-dom";

const InformeGenerator = () => {
  const navigate = useNavigate();

  const [proformasDisponibles, setProformasDisponibles] = useState([]);
  const [proformaSeleccionada, setProformaSeleccionada] = useState("");
  const [datosCliente, setDatosCliente] = useState({
    fecha: "",
    tomadoPor: "",
    procedimiento: "",
    analizadoPor: "",
  });

  const [analisis, setAnalisis] = useState([]);

  useEffect(() => {
    const cargarProformas = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/proformas/");
        const data = await res.json();
        setProformasDisponibles(data);
      } catch (error) {
        console.error("Error al cargar proformas:", error);
      }
    };
    cargarProformas();
  }, []);

  const buscarProforma = async () => {
    if (!proformaSeleccionada) return alert("Seleccione una proforma primero");
    try {
      const res = await fetch(
        `http://localhost:8000/api/proformas/${proformaSeleccionada}/informe/`
      );
      if (!res.ok) return alert("Proforma no encontrada");
      const data = await res.json();

      setDatosCliente((prev) => ({
        ...prev,
        fecha: data.date.slice(0, 10),
        analizadoPor: data.created_by,
      }));

      const analisisMapeado = data.analysis_data.map((item) => ({
        ...item,
        resultados: "",
        incertidumbre: "",
        limite: "",
      }));

      setAnalisis(analisisMapeado);
    } catch (error) {
      alert("Error al buscar proforma");
      console.error(error);
    }
  };

  const actualizarAnalisis = (index, field, value) => {
    setAnalisis((prev) => {
      const copia = [...prev];
      copia[index][field] = value;
      return copia;
    });
  };

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
          <button className="menu-item" onClick={() => navigate("/proformas")}>
            Proformas
          </button>
          <button className="menu-item active">Informes</button>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Cerrar Sesión
        </button>
      </div>

      <div className="main">
        <h1 className="title">Generar informes</h1>

        <div className="form-card">
          <h2>Datos Cliente</h2>
          <div className="form-grid">
            <div className="form-group full">
              <label>Seleccionar Proforma</label>
              <select
                value={proformaSeleccionada}
                onChange={(e) => setProformaSeleccionada(e.target.value)}
              >
                <option value="">-- Seleccione una proforma --</option>
                {proformasDisponibles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.proforma_number} - {p.client_name}
                  </option>
                ))}
              </select>
              <button
                className="button green"
                style={{ marginTop: "1rem" }}
                onClick={buscarProforma}
              >
                Buscar
              </button>
            </div>

            <div className="form-group">
              <label>Fecha de Emisión</label>
              <input type="date" value={datosCliente.fecha} readOnly />
            </div>
            <div className="form-group">
              <label>Muestra tomada por</label>
              <input
                type="text"
                value={datosCliente.tomadoPor}
                onChange={(e) =>
                  setDatosCliente({
                    ...datosCliente,
                    tomadoPor: e.target.value,
                  })
                }
              />
            </div>
            <div className="form-group">
              <label>Procedimiento de toma de muestra</label>
              <input
                type="text"
                value={datosCliente.procedimiento}
                onChange={(e) =>
                  setDatosCliente({
                    ...datosCliente,
                    procedimiento: e.target.value,
                  })
                }
              />
            </div>
            <div className="form-group">
              <label>Analizado por</label>
              <input type="text" value={datosCliente.analizadoPor} readOnly />
            </div>
          </div>
        </div>

        <div className="form-card">
          <h2>Monitoreo de Agua</h2>
          {analisis.map((a, index) => (
            <div key={index} className="analysis-entry">
              <div className="form-grid">
                <div className="form-group">
                  <label>Parámetro</label>
                  <input type="text" value={a.parameter} readOnly />
                </div>
                <div className="form-group">
                  <label>Unidad</label>
                  <input type="text" value={a.unit} readOnly />
                </div>
                <div className="form-group">
                  <label>Método/Referencia</label>
                  <input type="text" value={a.method} readOnly />
                </div>
                <div className="form-group">
                  <label>Resultados</label>
                  <input
                    type="text"
                    value={a.resultados}
                    onChange={(e) =>
                      actualizarAnalisis(index, "resultados", e.target.value)
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Límite</label>
                  <input
                    type="text"
                    value={a.limite}
                    onChange={(e) =>
                      actualizarAnalisis(index, "limite", e.target.value)
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Incertidumbre</label>
                  <input
                    type="text"
                    value={a.incertidumbre}
                    onChange={(e) =>
                      actualizarAnalisis(index, "incertidumbre", e.target.value)
                    }
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="button-group">
          <button
            className="button green"
            onClick={() => alert("Guardar informe (a implementar)")}
          >
            Guardar
          </button>
          <button
            className="button blue"
            onClick={() => alert("Previsualizar informe (a implementar)")}
          >
            Previsualizar
          </button>
        </div>
      </div>
    </div>
  );
};

export default InformeGenerator;
