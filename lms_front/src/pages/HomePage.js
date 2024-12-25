import React from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { auth } from "../auth";

const Home = () => {
  const isAuthenticated = auth.isAuthenticated();
  const isadmin = auth.isAdmin();

  console.log("role", localStorage.getItem("role_id"));

  if (!isAuthenticated) {
    return (
      <div
        style={{
          backgroundColor: "#F7F3EF",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Header />
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
          }}
        >
          <h1 className="mb-4" style={{ color: "#5A3E36" }}>
            Добро пожаловать в EduFlex!
          </h1>
          <p className="mb-4" style={{ color: "#7A6A63" }}>
            Выберите действие, чтобы начать свое обучение.
          </p>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div
      style={{
        backgroundColor: "#F7F3EF",
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Header />
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
        }}
      >
        <h1 className="mb-4" style={{ color: "#5A3E36" }}>
          Добро пожаловать {isadmin ? ", администратор!" : " в EduFlex!"}
        </h1>
        {isadmin && (
          <p className="mb-4" style={{ color: "#7A6A63" }}>
            Управляйте платформой с помощью панели администратора.
          </p>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default Home;
