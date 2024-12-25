import React, { useState, useEffect } from "react";
import { AdminRolesService } from "../../api";

const RolesManagement = () => {
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingRoleId, setEditingRoleId] = useState(null); // ID редактируемой роли (null для добавления)
  const [newRole, setNewRole] = useState({ name: "" });
  const [formError, setFormError] = useState("");

  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const data = await AdminRolesService.getallroles();
        setRoles(data.sort((a, b) => a.id - b.id));
      } catch (err) {
        setError("Ошибка загрузки ролей");
      } finally {
        setLoading(false);
      }
    };

    fetchRoles();
  }, []);

  const handleEdit = (roleId) => {
    const roleToEdit = roles.find((role) => role.id === roleId);
    if (roleToEdit) {
      setEditingRoleId(roleId);
      setNewRole({ name: roleToEdit.name });
      setShowModal(true);
    }
  };

  const handleDelete = async (roleId) => {
    if (window.confirm(`Вы уверены, что хотите удалить роль с ID: ${roleId}?`)) {
      try {
        await AdminRolesService.deleteRole(roleId);
        setRoles(roles.filter((role) => role.id !== roleId));
        alert(`Роль с ID: ${roleId} успешно удалена.`);
      } catch (err) {
        alert(`Ошибка при удалении роли с ID: ${roleId}.`);
      }
    }
  };

  const handleAddRole = () => {
    setFormError("");
    setEditingRoleId(null);
    setNewRole({ name: "" });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setFormError("");
  };

  const handleSaveRole = async () => {
    try {
      setFormError("");

      if (editingRoleId) {
        // Обновление роли
        await AdminRolesService.updateRole(editingRoleId, newRole);
        const updatedRoles = roles.map((role) =>
          role.id === editingRoleId ? { ...role, ...newRole } : role
        );
        setRoles(updatedRoles.sort((a, b) => a.id - b.id));
      } else {
        // Добавление новой роли
        const createdRole = await AdminRolesService.createRole(newRole);
        const updatedRoles = [...roles, createdRole];
        setRoles(updatedRoles.sort((a, b) => a.id - b.id));
      }

      setShowModal(false);
    } catch (err) {
      setFormError(err || "Ошибка при сохранении роли");
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h2>Управление ролями</h2>

      <div className="table-wrapper" style={{ maxWidth: "600px", margin: "0 auto", padding:"20px" }}>
  <table className="table table-striped" style={{ width: "100%" }}>
    <thead>
      <tr>
        <th>ID</th>
        <th>Название</th>
        <th>Действия</th>
      </tr>
    </thead>
    <tbody>
      {roles.map((role) => (
        <tr key={role.id}>
          <td>{role.id}</td>
          <td>{role.name}</td>
          <td>
            <button
              className="btn btn-primary me-2"
              onClick={() => handleEdit(role.id)}
            >
              Изменить
            </button>
            <button
              className="btn custom-btn btn-danger"
              onClick={() => handleDelete(role.id)}
            >
              Удалить
            </button>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
</div>

      <div style={{ textAlign: "center" }}>
        <button
          className="btn add-btn"
          style={{
            backgroundColor: "#28a745",
            color: "#fff",
            border: "none",
            padding: "10px 20px",
            borderRadius: "5px",
            fontSize: "16px",
          }}
          onClick={handleAddRole}
        >
          Добавить роль
        </button>
      </div>

      {showModal && (
        <div
          className="modal"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <form
            className="needs-validation"
            onSubmit={(e) => {
              e.preventDefault();
              const form = e.target;
              if (form.checkValidity()) {
                handleSaveRole();
              } else {
                form.classList.add("was-validated");
              }
            }}
            noValidate
          >
            <div
              className="modal-content"
              style={{
                backgroundColor: "#fff",
                borderRadius: "10px",
                padding: "20px",
                width: "400px",
              }}
            >
              <h5>{editingRoleId ? "Редактировать роль" : "Добавить новую роль"}</h5>
              <div className="mb-3">
                <label htmlFor="name">Название</label>
                <input
                  type="text"
                  id="name"
                  className="form-control"
                  value={newRole.name}
                  onChange={(e) => setNewRole({ name: e.target.value })}
                  required
                />
                <div className="invalid-feedback">Пожалуйста, укажите название роли.</div>
              </div>
              {formError && <div className="alert alert-danger mt-3">{formError}</div>}
              <div style={{ textAlign: "right" }}>
                <button
                  type="button"
                  className="btn btn-secondary me-2"
                  onClick={handleCloseModal}
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  Сохранить
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default RolesManagement;
