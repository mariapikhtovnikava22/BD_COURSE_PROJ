import React, { useState, useEffect } from "react";
import { AdminUserService, AdminRolesService, AdminLevelsService } from "../../api";

const UsersManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [roles, setRoles] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingUserId, setEditingUserId] = useState(null); // ID редактируемого пользователя (null для добавления)
  const [newUser, setNewUser] = useState({
    fio: "",
    email: "",
    password: "",
    role_id: "",
    is_active: true, // Добавлено поле is_active
  });

  const [levels, setLevels] = useState([]); // Если есть уровни
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRole, setSelectedRole] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("");
  const [filteredUsers, setFilteredUsers] = useState([]);

  const [formError, setFormError] = useState("");

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await AdminUserService.getallusers();
        const rolesData = await AdminRolesService.getallroles();
        const levelsData = await AdminLevelsService.getalllevels();

        setUsers(data);
        setRoles(rolesData);
        setFilteredUsers(data.sort((a, b) => a.id - b.id));
        setLevels(levelsData);

        setUsers(data);
        setRoles(rolesData);
      } catch (err) {
        setError(err || "Ошибка загрузки пользователей");
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleEdit = (userId) => {
    const userToEdit = users.find((user) => user.id === userId);
    if (userToEdit) {
      setEditingUserId(userId);
      setNewUser({
        fio: userToEdit.fio,
        email: userToEdit.email,
        password: "", // Пароль оставляем пустым
        role_id: userToEdit.role_id,
        is_active: userToEdit.is_active, // Устанавливаем is_active из данных пользователя
      });
      setShowModal(true);
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm(`Вы уверены, что хотите удалить пользователя с ID: ${userId}?`)) {
      try {
        await AdminUserService.deleteUser(userId);
        setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));
        setFilteredUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));
        alert(`Пользователь с ID: ${userId} успешно удалён.`);
      } catch (err) {
        alert(`Ошибка при удалении пользователя с ID: ${userId}.`);
      }
    }
  };

  const handleAddUser = () => {
    setFormError("");
    setEditingUserId(null);

    setNewUser({
      fio: "",
      email: "",
      password: "",
      role_id: roles.find((role) => role.id === 2)?.id || null,
      is_active: true, // По умолчанию пользователь активен
    });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setFormError("");
  };

  const handleSaveUser = async () => {
    try {
      setFormError("");
  
      if (editingUserId) {
        // Обновление пользователя
        await AdminUserService.updateUser(editingUserId, newUser);
        const updatedUsers = users.map((user) =>
          user.id === editingUserId
            ? {
                ...user,
                ...newUser,
                role_id: newUser.role_id,
              }
            : user
        );
        setUsers(updatedUsers);
        setFilteredUsers(updatedUsers);
      } else {
        // Добавление нового пользователя
        const createdUser = await AdminUserService.createUser(newUser);
        setUsers((prevUsers) => [...prevUsers, createdUser]);
        setFilteredUsers((prevUsers) => [...prevUsers, createdUser]);
      }
  
      setSuccess(editingUserId ? "Пользователь успешно обновлён" : "Пользователь успешно добавлен");
      setTimeout(() => {
        setShowModal(false);
        setSuccess("");
      }, 1000);
    } catch (err) {
      setFormError("Ошибка при сохранении пользователя.");
    }
  };
  
  

  const handleSearch = (query) => {
    setSearchQuery(query);
    filterUsers(query, selectedRole, selectedLevel);
  };

  const handleRoleFilter = (roleId) => {
    setSelectedRole(roleId);
    filterUsers(searchQuery, parseInt(roleId), selectedLevel);
  };

  const handleLevelFilter = (levelId) => {
    setSelectedLevel(levelId);
    filterUsers(searchQuery, selectedRole, parseInt(levelId));
  };

  const filterUsers = (query, roleId, levelId) => {
    let filtered = users;

    if (query) {
      filtered = filtered.filter((user) =>
        user.fio.toLowerCase().includes(query.toLowerCase())
      );
    }


    if (roleId) {
      filtered = filtered.filter((user) => parseInt(user.role_id) === parseInt(roleId));
    }
    

    if (levelId) {
      filtered = filtered.filter((user) => user.level_id === levelId);
    }

    setFilteredUsers(filtered.sort((a, b) => a.id - b.id)); // Сортировка по ID
  };



  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h2>Управление пользователями</h2>
      
      {/* Панель фильтров и поиска */}
      <div className="filter-panel mb-3">
        <div className="row">
          <div className="col-md-4">
            <input
              type="text"
              className="form-control"
              placeholder="Поиск по имени"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>
          <div className="col-md-4">
            <select
              className="form-control"
              value={selectedRole}
              onChange={(e) => handleRoleFilter(e.target.value)}
            >
              <option value="">Фильтр по роли</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-4">
              <select
              className="form-control"
              value={selectedLevel}
              onChange={(e) => handleLevelFilter(e.target.value)}
            >
              <option value="">Фильтр по уровню</option>
              {levels.map((level) => (
                <option key={level.id} value={level.id}>
                  {level.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>



      <div className="table-wrapper">
        <table className="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>ФИО</th>
              <th>Email</th>
              <th>Роль</th>
              <th>Активен</th>
              <th>Уровень</th>
              <th>Вступительный тест</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
          {filteredUsers.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.fio}</td>
                <td>{user.email}</td>
                <td>{roles.find((role) => role.id === user.role_id)?.name || "Не указана"}</td>
                <td>{user.is_active ? "Да" : "Нет"}</td>
                <td>{levels.find((level) => level.id == user.level_id)?.name || "Уровень не определен"}</td>
                <td>{user.entrance_test ? "Пройден" : "Не пройден"}</td>
                <td>
                  <button
                    className="btn btn-primary me-2"
                    onClick={() => handleEdit(user.id)}
                  >
                    Изменить
                  </button>
                  <button
                    className="btn custom-btn btn-danger"
                    onClick={() => handleDelete(user.id)}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <button
          className="btn add-btn"
          onClick={handleAddUser}
          style={{
            backgroundColor: "#28a745",
            color: "#fff",
            border: "none",
            padding: "10px 20px",
            borderRadius: "5px",
            fontSize: "16px",
          }}
        >
          Добавить пользователя
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
                handleSaveUser();
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
              <h5>{editingUserId ? "Редактировать пользователя" : "Добавить нового пользователя"}</h5>
              <div className="mb-3">
                <label htmlFor="fio">ФИО</label>
                <input
                  type="text"
                  id="fio"
                  className="form-control"
                  value={newUser.fio}
                  onChange={(e) => setNewUser({ ...newUser, fio: e.target.value })}
                  required
                />
                <div className="invalid-feedback">Пожалуйста, укажите ФИО.</div>
              </div>
              <div className="mb-3">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  className="form-control"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  required
                  pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
                />
                <div className="invalid-feedback">Пожалуйста, укажите email.</div>
              </div>
              {!editingUserId && (
                <div className="mb-3">
                  <label htmlFor="password">Пароль</label>
                  <input
                    type="password"
                    id="password"
                    className="form-control"
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    required
                  />
                  <div className="invalid-feedback">Пожалуйста, укажите пароль.</div>
                </div>
              )}
              <div className="mb-3">
                <label htmlFor="role">Роль</label>
                <select
                  id="role"
                  className="form-control"
                  value={newUser.role_id}
                  onChange={(e) => setNewUser({ ...newUser, role_id: parseInt(e.target.value) })}
                  required
                >
                  <option value="">Выберите роль</option>
                  {roles.map((role) => (
                    <option key={role.id} value={role.id}>
                      {role.name}
                    </option>
                  ))}
                </select>
                <div className="invalid-feedback">Пожалуйста, выберите роль.</div>
              </div>
              <div className="mb-3">
                <label htmlFor="is_active">Активен</label>
                <select
                  id="is_active"
                  className="form-control"
                  value={newUser.is_active ? "true" : "false"}
                  onChange={(e) =>
                    setNewUser({
                      ...newUser,
                      is_active: e.target.value === "true",
                    })
                  }
                >
                  <option value="true">Да</option>
                  <option value="false">Нет</option>
                </select>
                <div className="invalid-feedback">Пожалуйста, выберите активность.</div>
              </div>
              {formError && <div className="alert alert-danger mt-3">{formError}</div>}
              {success && <div className="alert alert-success mt-3">{success}</div>}
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

export default UsersManagement;
