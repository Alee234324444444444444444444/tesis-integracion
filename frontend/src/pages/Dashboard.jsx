import React from "react";
import "../styles/Dashboard.css";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login"); // ✅ redirigir sin confirmación ni notificación
  };

  const username = localStorage.getItem("user") || "Usuario";

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo-section">
          <div className="logo">
            <img src="/logo-white.png" alt="Logo" className="logo-white" />
            ENVIRONOVALAB
          </div>
        </div>

        <div className="menu">
          <button
            className="menu-item"
            onClick={() => console.log("Ir a Inicio")}
          >
            Inicio
          </button>
          <button className="menu-item" onClick={() => navigate("/proformas")}>
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

      {/* Main Content */}
      <div className="main-content">
        <div className="user-info">
          <h2>
            Hola, <strong>{username}</strong> 👋
          </h2>
        </div>

        <h2 className="section-title">Actividad Reciente</h2>

        <table className="activity-table">
          <thead>
            <tr>
              <th>Documento</th>
              <th>Fecha</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>PRO-00001</td>
              <td>18/05/2025</td>
              <td>
                <span className="status-badge">VER</span>
              </td>
            </tr>
            <tr>
              <td>INF-00001</td>
              <td>18/05/2025</td>
              <td>
                <span className="status-badge">VER</span>
              </td>
            </tr>
          </tbody>
        </table>

        
      </div>
    </div>
  );
};

export default Dashboard;
