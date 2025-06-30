import React, { useState, useEffect } from "react";
import "../styles/Dashboard.css";
import Sidebar from "../components/Sidebar";
import axios from "axios";

const statusColors = {
  "Por hacer": "gray",
  "En progreso": "#facc15",
  "Terminado": "#22c55e",
};

const statusOptions = ["Por hacer", "En progreso", "Terminado"];

const Dashboard = () => {
  const username = localStorage.getItem("user") || "Usuario";
  const role = localStorage.getItem("role") || "user"; // 'admin' o 'user'
  const isAdmin = role === "admin";

  const [search, setSearch] = useState("");
  const [allDocs, setAllDocs] = useState([]);
  const [filteredData, setFilteredData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responses = await Promise.all([
          axios.get("http://localhost:8000/api/informes/"),
          isAdmin ? axios.get("http://localhost:8000/api/proformas/") : null,
        ]);

        const informes = responses[0].data.map((item) => ({
          id: item.id || item._id,
          type: "Informe",
          code: item.code || item.numero || "SIN-CÓDIGO",
          date: item.date || item.fecha || "Sin fecha",
          status: item.status || "Por hacer",
        }));

        let proformas = [];
        if (isAdmin && responses[1]) {
          proformas = responses[1].data.map((item) => ({
            id: item.id || item._id,
            type: "Proforma",
            code: item.code || item.numero || "SIN-CÓDIGO",
            date: item.date || item.fecha || "Sin fecha",
            status: item.status || "Por hacer",
          }));
        }

        const combined = [...proformas, ...informes];
        setAllDocs(combined);
        setFilteredData(combined);
      } catch (err) {
        console.error("Error al cargar datos:", err);
      }
    };

    fetchData();
  }, [isAdmin]);

  useEffect(() => {
    setFilteredData(
      allDocs.filter((item) =>
        item.code.toLowerCase().includes(search.toLowerCase())
      )
    );
  }, [search, allDocs]);

  const handleStatusChange = async (id, newStatus) => {
    try {
      await axios.patch(`http://localhost:8000/api/${id.includes("PRO") ? "proformas" : "informes"}/${id}/`, {
        status: newStatus,
      });
      setAllDocs((prev) =>
        prev.map((doc) =>
          doc.id === id ? { ...doc, status: newStatus } : doc
        )
      );
    } catch (err) {
      console.error("Error actualizando estado:", err);
    }
  };

  const handleDownload = async (doc) => {
    try {
      const url = `http://localhost:8000/api/${doc.type === "Informe" ? "proformas" : "proformas"}/${doc.id}/${
        doc.type === "Informe" ? "informe_pdf" : "pdf"
      }/`;
      const res = await axios.get(url, {
        responseType: "blob",
      });

      const file = new Blob([res.data], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(file);
      link.download = `${doc.code}.pdf`;
      link.click();
    } catch (err) {
      console.error("Error al descargar PDF:", err);
    }
  };

  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="main-content">
        <div className="user-info">
          <h2>Hola, <strong>{username}</strong> 👋</h2>
        </div>

        <h2 className="section-title">Historial de Documentos</h2>

        <input
          type="text"
          className="search-bar"
          placeholder="Buscar por código..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <table className="activity-table">
          <thead>
            <tr>
              <th>Tipo</th>
              <th>Código</th>
              <th>Fecha</th>
              <th>Estado</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((doc) => (
              <tr key={doc.id}>
                <td>{doc.type}</td>
                <td>{doc.code}</td>
                <td>{doc.date}</td>
                <td>
                  {isAdmin ? (
                    <select
                      value={doc.status}
                      onChange={(e) =>
                        handleStatusChange(doc.id, e.target.value)
                      }
                      className="status-dropdown"
                    >
                      {statusOptions.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <span
                      className="status-pill"
                      style={{ backgroundColor: statusColors[doc.status] || "#ccc" }}
                    >
                      {doc.status}
                    </span>
                  )}
                </td>
                <td>
                  <button className="status-badge" onClick={() => handleDownload(doc)}>
                    Descargar
                  </button>
                </td>
              </tr>
            ))}
            {filteredData.length === 0 && (
              <tr>
                <td colSpan="5" className="illustration-text">
                  No se encontraron documentos.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
