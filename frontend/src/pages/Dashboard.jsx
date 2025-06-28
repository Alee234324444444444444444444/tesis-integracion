import React from "react";
import "../styles/Dashboard.css";
import Sidebar from "../components/Sidebar";

const Dashboard = () => {

  const username = localStorage.getItem("user") || "Usuario";

  return (
    <div className="dashboard-container">
      <Sidebar />
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