import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Dashboard from "./pages/Dashboard";
import ProtectedRoute from "./components/ProtectedRoute";
import ForgotPassword from "./components/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import ProformaGenerator from "./pages/ProformaGenerator";
import AdminMuestras from "./pages/AdminMuestras";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/proformas"
          element={
            <ProtectedRoute>
              <ProformaGenerator />
            </ProtectedRoute>
          }
        />

        {/* ✅ Ruta corregida */}
        <Route
          path="/admin/tipos-muestra"
          element={
            <ProtectedRoute onlyAdmin={true}>
              <AdminMuestras />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Login />} />
      </Routes>
    </Router>
  );
}

export default App;
