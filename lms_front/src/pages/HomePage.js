import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { auth } from "../auth";

const Home = () => {
  const isAuthenticated = auth.isAuthenticated();

  if (!isAuthenticated) {
    return (
      <div style={{ backgroundColor: "#F7F3EF", minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <Header />
        <div className="container flex-grow-1 d-flex flex-column align-items-center justify-content-center text-center">
          <h1 className="mb-4" style={{ color: "#5A3E36" }}>Добро пожаловать в EduFlex!</h1>
          <p className="mb-4" style={{ color: "#7A6A63" }}>
            Выберите действие, чтобы начать свое обучение.
          </p>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: "#F7F3EF", minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Header />
      <div className="container flex-grow-1 py-5">
        <h1 className="mb-4" style={{ color: "#5A3E36" }}>Добро пожаловать в EduFlex!</h1>
      </div>
      <Footer />
    </div>
  );
};

export default Home;