import React, { useState, useEffect } from "react";
import "../styles/Dashboard.css";
import Sidebar from "../components/Sidebar";
import axios from "axios";
import { FileDown, Search } from "lucide-react";

const statusColors = {
  "Por hacer": "gray",
  "En progreso": "#facc15",
  "Terminado": "#22c55e",
};

const statusOptions = ["Por hacer", "En progreso", "Terminado"];

const InformesList = () => {
  const username = localStorage.getItem("user") || "Usuario";
  const role = (localStorage.getItem("userRole") || "user").toLowerCase().trim();
  const isAdmin = role === "admin";

  const [search, setSearch] = useState("");
  const [allDocs, setAllDocs] = useState([]);
  const [filteredData, setFilteredData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const informesRes = await axios.get("http://localhost:8000/api/informes/");

        const informes = informesRes.data.map((item) => ({
          id: item.id || item._id,
          type: "Informe",
          code: item.codigo || "SIN-CÓDIGO",
          date: item.fecha_emision || "Sin fecha",
          status: item.status || "Por hacer",
          creado_por: item.created_by || item.analizado_por || "Desconocido",
          proforma: item.proforma || null,
        }));

        const sorted = informes
          .map((item) => ({
            ...item,
            rawDate: new Date(item.date),
          }))
          .filter((item) => !isNaN(item.rawDate))
          .sort((a, b) => b.rawDate - a.rawDate)
          .slice(0, 6);

        setAllDocs(sorted);
        setFilteredData(sorted);
      } catch (err) {
        console.error("Error al cargar datos:", err);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    setFilteredData(
      allDocs.filter((item) =>
        item.code.toLowerCase().includes(search.toLowerCase())
      )
    );
  }, [search, allDocs]);

  const handleStatusChange = async (id, newStatus) => {
    try {
      await axios.patch(
        `http://localhost:8000/api/informes/${id}/`,
        { status: newStatus }
      );
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
    let url = "";
    let filename = doc.code || "documento";

    if (doc.type === "Informe") {
      const proformaId = typeof doc.proforma === "object" ? doc.proforma.id : doc.proforma;
      if (!proformaId) {
        console.error("No se encontró el ID de la proforma relacionada.");
        return;
      }
      url = `http://localhost:8000/api/proformas/${proformaId}/informe_pdf/`;
    } else if (doc.type === "Proforma") {
      url = `http://localhost:8000/api/proformas/${doc.id}/pdf/`;
    }

    const res = await axios.get(url, { responseType: "blob" });

    const file = new Blob([res.data], { type: "application/pdf" });
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(file);
    link.download = `${filename}.pdf`;
    link.click();
  } catch (err) {
    console.error("Error al descargar PDF:", err.response?.data || err.message);
  }
};


  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="main-content">
        <div className="user-info">
          <h2>
            Hola, <strong>{username}</strong> 👋
          </h2>
        </div>

        <h2 className="section-title">Informes Recientes</h2>
        <div className="search-container">
          <span className="search-icon">
            <Search size={16} />
          </span>
          <input type="text" className="search-bar" placeholder="Buscar por código..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>

        <div className="ua-form-card">
          <table className="ua-table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Código</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th>Creado por</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.type}</td>
                  <td>{doc.code}</td>
                  <td>{new Date(doc.date).toLocaleDateString()}</td>
                  <td>
                    {isAdmin ? (
                      <select
                        value={doc.status}
                        onChange={(e) => handleStatusChange(doc.id, e.target.value)}
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
                        style={{
                          backgroundColor: statusColors[doc.status] || "#ccc",
                        }}
                      >
                        {doc.status}
                      </span>
                    )}
                  </td>
                  <td>{doc.creado_por}</td>
                  <td>
                    <button className="ua-button" onClick={() => handleDownload(doc)}>
                      <FileDown size={14} /> Descargar
                    </button>
                  </td>
                </tr>
              ))}
              {filteredData.length === 0 && (
                <tr>
                  <td colSpan="6" className="illustration-text">
                    No se encontraron documentos.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default InformesList;
