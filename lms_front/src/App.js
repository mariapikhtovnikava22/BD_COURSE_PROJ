import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import MePage from "./pages/MePage";
import UserTestPage from "./pages/CoursePage";
import "./styles/App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import { auth } from './auth'; 
import AdminDashboardPage from "./Admin/components/AdminDashboardPage";


console.log("app");
const PrivateRoute = ({ children }) => {
  const isAuthenticated = auth.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};


const AdminRoute = ({ children }) => {

  if (!auth.isAuthenticated()) {
      // Если пользователь не авторизован, перенаправляем на страницу входа
      return <Navigate to="/login" replace />;
  }

  if (!auth.isAdmin()) {
      // Если пользователь не администратор, перенаправляем на главную страницу
      return <Navigate to="/" replace />;
  }

  // Если всё ок, отображаем компонент
  return children;
};




const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/userprofile" element={ 
          <PrivateRoute>
              <MePage />
          </PrivateRoute>} />
          <Route path="/courses" element={ 
          <PrivateRoute>
              <UserTestPage />
          </PrivateRoute>} />
        <Route path="/admin/*" element = {
          <AdminRoute> 
            <AdminDashboardPage /> 
          </AdminRoute>}/>
      </Routes>
    </Router>
  );
};

export default App;
