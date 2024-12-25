import React from "react";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import Sidebar from "./Sidebar";
import AdminContent from "./AdminContent";

const AdminDashboardPage = () => {
  return (
        <div
    style={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: "#F7F3EF",
    }}
    >
    <Header />
    <div style={{ display: "flex", flex: "1", overflow: "hidden" }}>
        <Sidebar />
        <div style={{ flex: "10", padding: "20px", overflowY: "auto" }}>
        <AdminContent />
        </div>
    </div>
    <Footer />
    </div>
    );
};

export default AdminDashboardPage;
