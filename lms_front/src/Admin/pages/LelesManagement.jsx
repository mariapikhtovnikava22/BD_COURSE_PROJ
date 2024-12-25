import React, { useState, useEffect } from "react";
import { AdminLevelsService } from "../../api";

const LevelsManagement = () => {
  const [levels, setLevels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingLevelId, setEditingLevelId] = useState(null); // ID редактируемого уровня (null для добавления)
  const [newLevel, setNewLevel] = useState({ name: "" });
  const [formError, setFormError] = useState("");

  useEffect(() => {
    const fetchLevels = async () => {
      try {
        const data = await AdminLevelsService.getalllevels();
        setLevels(data.sort((a, b) => a.id - b.id));
      } catch (err) {
        setError("Ошибка загрузки уровней");
      } finally {
        setLoading(false);
      }
    };

    fetchLevels();
  }, []);

  const handleEdit = (levelId) => {
    const levelToEdit = levels.find((level) => level.id === levelId);
    if (levelToEdit) {
      setEditingLevelId(levelId);
      setNewLevel({ name: levelToEdit.name });
      setShowModal(true);
    }
  };

  const handleDelete = async (levelId) => {
    if (window.confirm(`Вы уверены, что хотите удалить уровень с ID: ${levelId}?`)) {
      try {
        await AdminLevelsService.deleteLevel(levelId);
        setLevels(levels.filter((level) => level.id !== levelId));
        alert(`Уровень с ID: ${levelId} успешно удалён.`);
      } catch (err) {
        alert(`Ошибка при удалении уровня с ID: ${levelId}.`);
      }
    }
  };

  const handleAddLevel = () => {
    setFormError("");
    setEditingLevelId(null);
    setNewLevel({ name: "" });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setFormError("");
  };

  const handleSaveLevel = async () => {
    try {
      setFormError("");

      if (editingLevelId) {
        // Обновление уровня
        await AdminLevelsService.updateLevel(editingLevelId, newLevel);
        const updatedLevels = levels.map((level) =>
          level.id === editingLevelId ? { ...level, ...newLevel } : level
        );
        setLevels(updatedLevels.sort((a, b) => a.id - b.id));
      } else {
        // Добавление нового уровня
        const createdLevel = await AdminLevelsService.createLevel(newLevel);
        const updatedLevels = [...levels, createdLevel];
        setLevels(updatedLevels.sort((a, b) => a.id - b.id));
      }

      setShowModal(false);
    } catch (err) {
      setFormError(err || "Ошибка при сохранении уровня");
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h2>Управление уровнями</h2>

      <div className="table-wrapper" style={{ maxWidth: "600px", margin: "0 auto", padding: "20px" }}>
        <table className="table table-striped" style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {levels.map((level) => (
              <tr key={level.id}>
                <td>{level.id}</td>
                <td>{level.name}</td>
                <td>
                  <button
                    className="btn btn-primary me-2"
                    onClick={() => handleEdit(level.id)}
                  >
                    Изменить
                  </button>
                  <button
                    className="btn custom-btn btn-danger"
                    onClick={() => handleDelete(level.id)}
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
          onClick={handleAddLevel}
        >
          Добавить уровень
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
                handleSaveLevel();
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
              <h5>{editingLevelId ? "Редактировать уровень" : "Добавить новый уровень"}</h5>
              <div className="mb-3">
                <label htmlFor="name">Название</label>
                <input
                  type="text"
                  id="name"
                  className="form-control"
                  value={newLevel.name}
                  onChange={(e) => setNewLevel({ name: e.target.value })}
                  required
                />
                <div className="invalid-feedback">Пожалуйста, укажите название уровня.</div>
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

export default LevelsManagement;
