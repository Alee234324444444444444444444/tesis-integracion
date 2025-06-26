import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  CheckCircle,
  AlertCircle,
  Info,
  Shield,
  ToggleLeft,
  ToggleRight,
} from "lucide-react";
import "../styles/UserAdmin.css";

const UserAdmin = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [notifications, setNotifications] = useState([]);

  let authUser = null;
  try {
    const raw = localStorage.getItem("user");
    authUser = JSON.parse(raw);
  } catch {
    const raw = localStorage.getItem("user");
    authUser = raw ? { username: raw } : null;
  }

  const showNotification = (type, message, time = 3000) => {
    const id = Date.now() + Math.random();
    setNotifications((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    }, time);
  };

  const fetchUsers = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/api/auth/admin/users/");
      const data = await res.json();
      setUsers(data);
    } catch {
      showNotification("error", "Error al obtener usuarios");
    }
  }, []);

  const toggleAdmin = async (id, is_admin) => {
    try {
      await fetch(`http://localhost:8000/api/auth/admin/users/${id}/update_role/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_admin: !is_admin }),
      });
      showNotification("success", "Rol actualizado");
      fetchUsers();
    } catch {
      showNotification("error", "No se pudo actualizar rol");
    }
  };

  const toggleActivo = async (id) => {
    try {
      await fetch(`http://localhost:8000/api/auth/admin/users/${id}/toggle_active/`, {
        method: "POST",
      });
      showNotification("success", "Estado actualizado");
      fetchUsers();
    } catch {
      showNotification("error", "No se pudo actualizar estado");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("auth");
    localStorage.removeItem("user");
    navigate("/login");
  };

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return (
    <>
      <div className="ua-toast-container">
        {notifications.map((n) => (
          <div key={n.id} className={`ua-toast ${n.type}`}>
            {n.type === "success" && <CheckCircle size={20} />}
            {n.type === "error" && <AlertCircle size={20} />}
            {n.type === "info" && <Info size={20} />}
            {n.message}
          </div>
        ))}
      </div>

      <div className="ua-container">
        <div className="ua-sidebar">
          <div className="ua-logo-section">
            <div className="ua-logo">
              <img src="/logo-white.png" alt="Logo" className="ua-logo-white" />
              ENVIRONOVALAB
            </div>
          </div>
          <div className="ua-menu">
            <button className="ua-menu-item" onClick={() => navigate("/dashboard")}>Inicio</button>
            <button className="ua-menu-item" onClick={() => navigate("/proformas")}>Proformas</button>
            <button className="ua-menu-item" onClick={() => navigate("/informes")}>Informes</button>
            <button className="ua-menu-item" onClick={() => navigate("/admin/tipos-muestra")}>Tipos de Muestra</button>
            <button className="ua-menu-item active" onClick={() => navigate("/admin/usuarios")}>Usuarios</button>
          </div>
          <button className="ua-logout-btn" onClick={handleLogout}>Cerrar Sesión</button>
        </div>

        <div className="ua-main">
          <h1 className="ua-title">Administrar Usuarios</h1>
          <div className="ua-form-card">
            <table className="ua-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u, i) => {
                  const isSelf = authUser && u.username === authUser.username;
                  const isLast = i === users.length - 1;
                  return (
                    <tr key={u.id} className={`${isSelf ? "ua-self-row" : ""} ${isLast ? "ua-last-row" : ""}`}>
                      <td>{u.username}</td>
                      <td>{u.email}</td>
                      <td>
                        <button
                          className={`ua-button ${u.is_admin ? "blue" : "gray"}`}
                          onClick={() => toggleAdmin(u.id, u.is_admin)}
                          disabled={isSelf}
                          title={isSelf ? "No puedes cambiar tu propio rol" : ""}
                        >
                          <Shield size={16} className="ua-icon" />
                          {u.is_admin ? "Admin" : "Usuario"}
                        </button>
                      </td>
                      <td>
                        <button
                          className={`ua-button ${u.activo ? "green" : "red"}`}
                          onClick={() => toggleActivo(u.id)}
                          disabled={isSelf}
                          title={isSelf ? "No puedes cambiar tu propio estado" : ""}
                        >
                          {u.activo ? (
                            <>
                              <ToggleLeft size={14} className="ua-icon" />
                              <span className="ua-bold">Activo</span>
                            </>
                          ) : (
                            <>
                              <ToggleRight size={14} className="ua-icon" />
                              <span className="ua-bold">Inactivo</span>
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
};

export default UserAdmin;
