import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import ForgotPassword from "./components/ForgotPassword";
import ProtectedRoute from "./components/ProtectedRoute";

import Dashboard from "./pages/Dashboard";
import ProformaGenerator from "./pages/ProformaGenerator";
import InformeGenerator from "./pages/InformeGenerator";
import AdminMuestras from "./pages/AdminMuestras";
import UserAdmin from "./pages/UserAdmin";
import ResetPassword from "./pages/ResetPassword";
import InformesList from "./pages/InfromesList";
import ProformasList from "./pages/ProformasList";

function App() {
  return (
    <Router>
      <Routes>
        {/* Ruta por defecto */}
        <Route path="/" element={<Login />} />

        {/* Rutas públicas */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />

        {/* Rutas protegidas */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/informeslist"
          element={
            <ProtectedRoute>
              <InformesList />
            </ProtectedRoute>
          }
        />

        <Route
          path="/informes"
          element={
            <ProtectedRoute>
              <InformeGenerator />
            </ProtectedRoute>
          }
        />

        {/* Rutas solo para administradores */}
        <Route
          path="/proformas"
          element={
            <ProtectedRoute onlyAdmin={true}>
              <ProformaGenerator />
            </ProtectedRoute>
          }
        />

        <Route
          path="/proformaslist"
          element={
            <ProtectedRoute onlyAdmin={true}>
              <ProformasList/>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/tipos-muestra"
          element={
            <ProtectedRoute onlyAdmin={true}>
              <AdminMuestras />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/usuarios"
          element={
            <ProtectedRoute onlyAdmin={true}>
              <UserAdmin />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
