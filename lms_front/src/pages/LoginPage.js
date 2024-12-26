import React from "react";
import { Link } from "react-router-dom"; // Импортируем Link для навигации
import Login from "../components/Login";
import "../styles/Login.css";
import Header from "../components/Header";
import Footer from "../components/Footer";

const LoginPage = () => {
  return (
    <div
      className="d-flex flex-column min-vh-100" // Новый класс для растяжения контейнера на всю высоту экрана
      style={{ backgroundColor: "#f9f4ef" }} // Перенесли фон сюда
    >
      <Header />
      <div
        className="d-flex justify-content-center align-items-center flex-grow-1" // flex-grow-1 позволяет занять все свободное пространство
        style={{
          padding: "20px", // Отступы для мобильных экранов
        }}
      >
        <div
          className="shadow-lg p-5"
          style={{
            backgroundColor: "#fff",
            width: "1000px", // Увеличенная ширина
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
            Вход
          </h2>
          <Login />
          <div className="text-center mt-4">
            <p style={{ fontSize: "16px", color: "#5A3E36" }}>
              У вас еще нет аккаунта?{" "}
              <Link
                to="/register"
                style={{
                  textDecoration: "underline",
                  color: "#5A3E36",
                  fontWeight: "bold",
                }}
              >
                Зарегистрируйтесь!
              </Link>
            </p>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default LoginPage;