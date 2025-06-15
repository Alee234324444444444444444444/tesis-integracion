import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children, onlyAdmin = false }) {
  const isAuthenticated = localStorage.getItem("auth") === "true";
  const isAdmin = localStorage.getItem("userRole") === "admin";

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (onlyAdmin && !isAdmin) {
    return <Navigate to="/dashboard" />; // Si no es admin, redirige
  }

  return children;
}
