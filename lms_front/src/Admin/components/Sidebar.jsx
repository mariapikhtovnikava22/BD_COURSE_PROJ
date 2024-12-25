import React from "react";
import { Link, useLocation } from "react-router-dom";

const Sidebar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div
      style={{
        width: "250px",
        backgroundColor: "#5d4b46", // Более мягкий оттенок коричневого
        color: "#fff",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        height: "auto", // Учитываем высоту header
        borderTop: "2px solid #D2C4B3", // Разделитель сверху
      }}
    >
      <h2 style={{ fontSize: "20px", marginBottom: "20px" }}>Админ-панель</h2>
      <nav style={{ flex: "1" }}>
        <Link
          to="/admin/users"
          style={{
            display: "block",
            color: isActive("/admin/users") ? "#D2C4B3" : "#fff",
            textDecoration: "none",
            marginBottom: "10px",
            fontWeight: isActive("/admin/users") ? "bold" : "normal",
          }}
        >
          Пользователи
        </Link>
        <Link
          to="/admin/roles"
          style={{
            display: "block",
            color: isActive("/admin/roles") ? "#D2C4B3" : "#fff",
            textDecoration: "none",
            marginBottom: "10px",
            fontWeight: isActive("/admin/roles") ? "bold" : "normal",
          }}
        >
          Роли
        </Link>
        <Link
          to="/admin/levels"
          style={{
            display: "block",
            color: isActive("/admin/levels") ? "#D2C4B3" : "#fff",
            textDecoration: "none",
            marginBottom: "10px",
            fontWeight: isActive("/admin/levels") ? "bold" : "normal",
          }}
        >
          Уровни
        </Link>
        <Link
          to="/admin/categories"
          style={{
            display: "block",
            color: isActive("/admin/categories") ? "#D2C4B3" : "#fff",
            textDecoration: "none",
            marginBottom: "10px",
            fontWeight: isActive("/admin/categories") ? "bold" : "normal",
          }}
        >
          Категории материалов
        </Link>
        <Link
          to="/admin/course"
          style={{
            display: "block",
            color: isActive("/admin/course") ? "#D2C4B3" : "#fff",
            textDecoration: "none",
            marginBottom: "10px",
            fontWeight: isActive("/admin/corse") ? "bold" : "normal",
          }}
        >
          Создание курса
        </Link>
      </nav>
    </div>
  );
};

export default Sidebar;
