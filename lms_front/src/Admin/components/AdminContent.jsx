import React from "react";
import { Routes, Route } from "react-router-dom";
import UsersManagement from "../pages/UsersManagement";
import RolesManagement from "../pages/RolesManagement";
import LevelsManagement from "../pages/LelesManagement";
import CategoryMaterialManagement from "../pages/CategoryMaterialManagement";
import ModuleTopicManagement from "../pages/ModuleTopicManagement"
// import CategoriesManagement from "../pages/admin/CategoriesManagement";

const AdminContent = () => {
  return (
    <div style={{ flex: "1", padding: "20px" }}>
      <Routes>
        <Route path="/users/" element={<UsersManagement />} />
        <Route path="/roles/" element={<RolesManagement />} />
        <Route path="/levels/" element={<LevelsManagement />} />
        <Route path="/categories/" element={<CategoryMaterialManagement />} />
        <Route path="/course/" element={<ModuleTopicManagement />} />
        {/* <Route path="/admin/roles" element={<RolesManagement />} />
        <Route path="/admin/levels" element={<LevelsManagement />} />
        <Route path="/admin/categories" element={<CategoriesManagement />} /> */}
      </Routes>
    </div>
  );
};

export default AdminContent;
