import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import Cookies from "js-cookie";
import {
  CheckCircle,
  AlertCircle,
  Info,
  Shield,
  ToggleLeft,
  ToggleRight,
  UserPlus,
  XCircle,
  Save,
  Mail,
  Lock,
  User
} from "lucide-react";
import "../styles/UserAdmin.css";
import Sidebar from "../components/Sidebar";

const UserAdmin = () => {
  const [users, setUsers] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    is_admin: false,
  });

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

  const refreshCsrf = async () => {
    try {
      await axios.get("http://localhost:8000/api/csrf/", { withCredentials: true });
    } catch (err) {
      console.error("❌ No se pudo obtener CSRF token:", err);
    }
  };

  const fetchUsers = useCallback(async () => {
    try {
      await axios.get("http://localhost:8000/api/csrf/", { withCredentials: true });
      const res = await axios.get("http://localhost:8000/api/auth/admin/users/", {
        withCredentials: true,
        headers: { "X-CSRFToken": Cookies.get("csrftoken") },
      });
      setUsers(res.data);
    } catch {
      showNotification("error", "Error al obtener usuarios");
    }
  }, []);

  const toggleAdmin = async (id, is_admin) => {
    try {
      await refreshCsrf();
      await axios.post(
        `http://localhost:8000/api/auth/admin/users/${id}/update_role/`,
        { is_admin: !is_admin },
        {
          withCredentials: true,
          headers: { "X-CSRFToken": Cookies.get("csrftoken") },
        }
      );
      showNotification("success", "Rol actualizado");
      fetchUsers();
    } catch {
      showNotification("error", "No se pudo actualizar rol");
    }
  };

  const toggleActivo = async (id) => {
    try {
      await refreshCsrf();
      await axios.post(
        `http://localhost:8000/api/auth/admin/users/${id}/toggle_active/`,
        {},
        {
          withCredentials: true,
          headers: { "X-CSRFToken": Cookies.get("csrftoken") },
        }
      );
      showNotification("success", "Estado actualizado");
      fetchUsers();
    } catch {
      showNotification("error", "No se pudo actualizar estado");
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleUserCreate = async () => {
    const { username, email, password, is_admin } = formData;
    if (!username || !email || !password) {
      showNotification("error", "Todos los campos son obligatorios");
      return;
    }

    try {
      await refreshCsrf();
      await axios.post(
        "http://localhost:8000/api/auth/admin/users/",
        { username, email, password, is_admin },
        {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken"),
          },
        }
      );

      showNotification("success", "Usuario creado");
      setFormData({ username: "", email: "", password: "", is_admin: false });
      setShowModal(false);
      fetchUsers();
    } catch (err) {
      console.error("Error al crear usuario:", err);
      showNotification("error", "Error al crear usuario");
    }
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
        <Sidebar />

        <div className="ua-main">
          <div className="ua-title-button-bar">
            <h1 className="ua-title">Administrar Usuarios</h1>
            <div className="ua-button-bar">
              <button className="ua-create-btn" onClick={() => setShowModal(true)}>
                <UserPlus size={18} />
                Añadir Usuario
              </button>
            </div>
          </div>

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

      {showModal && (
        <div className="ua-modal-overlay">
          <div className="ua-modal">
            <h3>Nuevo Usuario</h3>
            <div className="ua-input-wrapper">
              <User className="ua-input-icon" size={18} />
              <input
                name="username"
                type="text"
                placeholder="Nombre de usuario"
                value={formData.username}
                onChange={handleInputChange}
              />
            </div>
            <div className="ua-input-wrapper">
              <Mail className="ua-input-icon" size={18} />
              <input
                name="email"
                type="email"
                placeholder="Correo"
                value={formData.email}
                onChange={handleInputChange}
              />
            </div>
            <div className="ua-input-wrapper">
              <Lock className="ua-input-icon" size={18} />
              <input
                name="password"
                type="password"
                placeholder="Contraseña"
                value={formData.password}
                onChange={handleInputChange}
              />
            </div>
            <label>
              <input
                name="is_admin"
                type="checkbox"
                checked={formData.is_admin}
                onChange={handleInputChange}
              />
              ¿Es administrador?
            </label>
            <div className="ua-modal-actions">
              <button className="ua-button red" onClick={() => setShowModal(false)}>
                <XCircle size={14} /> Cancelar
              </button>
              <button className="ua-button green" onClick={handleUserCreate}>
                <Save size={14} /> Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default UserAdmin;
