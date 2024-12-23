import React from "react";
import { Link } from "react-router-dom"; // Импортируем Link для навигации
import Register from "../components/Register"; // Предполагаем, что компонент Register существует
import "../styles/Register.css"; // Если у вас есть отдельный CSS файл для регистрации
import Header from "../components/Header";
import Footer from "../components/Footer";

const RegisterPage = () => {
  return (
    <>
      <Header />
    <div
      className="d-flex justify-content-center align-items-center"
      style={{
        minHeight: "81vh", // Высота на весь экран
        backgroundColor: "#f9f4ef",
        padding: "20px", // Отступы для мобильных экранов
      }}
    >
      <div
        className="shadow-lg p-5"
        style={{
          backgroundColor: "#fff",
          width: "1200px", // Увеличенная ширина
          maxWidth: "100%", // Для адаптивности
          borderRadius: "10px",
        }}
      >
        <h2
          className="text-center mb-4"
          style={{
            fontFamily: "Georgia, serif",
            fontSize: "28px",
            color: "#5A3E36",
          }}
        >
          Регистрация
        </h2>
        <Register /> 
        <div className="text-center mt-4">
            <p style={{ fontSize: "16px", color: "#5A3E36" }}>
              У вас есть аккаунт?{" "}
              <Link
                to="/login"
                style={{
                  textDecoration: "underline",
                  color: "#5A3E36",
                  fontWeight: "bold",
                }}
              >
                Войдите!
              </Link>
            </p>
          </div>
      </div>
    </div>
    <Footer />
    </>
  );
};

export default RegisterPage;