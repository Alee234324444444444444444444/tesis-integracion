// src/components/Sidebar.js
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  FaHome,
  FaFileInvoice,
  FaChartBar,
  FaFlask,
  FaUsersCog,
  FaSignOutAlt,
  FaFileAlt,
} from "react-icons/fa";

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [activePath, setActivePath] = useState(location.pathname);
  const role = localStorage.getItem("userRole");

  useEffect(() => {
    setActivePath(location.pathname);
  }, [location.pathname]);

  const handleNavigate = (path) => {
    navigate(path);
  };

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    localStorage.removeItem("userRole");
    navigate("/login");
  };

  return (
    <div className="sidebar">
      <div className="logo-section">
        <div className="logo">
          <img src="/logo-white.png" alt="Logo" className="logo-white" />
          ENVIRONOVALAB
        </div>
      </div>

      <div className="menu">
        <button
          className={`menu-item ${activePath === "/dashboard" ? "active" : ""}`}
          onClick={() => handleNavigate("/dashboard")}
        >
        <FaHome className="icon" />  Inicio
        </button>

        {role === "admin" && (
          <>
          <button
            className={`menu-item ${activePath === "/proformas" ? "active" : ""}`}
            onClick={() => handleNavigate("/proformas")}
          >
          <FaFileInvoice className="icon" />  Proformas
          </button>

          <button
            className={`menu-item ${activePath === "/proformaslist" ? "active" : ""}`}
            onClick={() => handleNavigate("/proformaslist")}
          >
          <FaFileAlt className="icon" />  Lista de Proformas
          </button>
          </>
        )}
        

        <button
          className={`menu-item ${activePath === "/informes" ? "active" : ""}`}
          onClick={() => handleNavigate("/informes")}
        >
        <FaChartBar className="icon" />  Informes
        </button>

        <button
          className={`menu-item ${activePath === "/informeslist" ? "active" : ""}`}
          onClick={() => handleNavigate("/informeslist")}
        >
        <FaChartBar className="icon" />  Lista de Informes
        </button>

        {role === "admin" && (
          <>
            <button
              className={`menu-item ${activePath === "/admin/tipos-muestra" ? "active" : ""}`}
              onClick={() => handleNavigate("/admin/tipos-muestra")}
            >
            <FaFlask className="icon" />  Tipos de Muestra
            </button>

            <button
              className={`menu-item ${activePath === "/admin/usuarios" ? "active" : ""}`}
              onClick={() => handleNavigate("/admin/usuarios")}
            >
            <FaUsersCog className="icon" />  Usuarios
            </button>
          </>
        )}
      </div>

      <button onClick={handleLogout} className="logout-btn">
      <FaSignOutAlt className="icon" />  Cerrar Sesión
      </button>
    </div>
  );
};

export default Sidebar;
