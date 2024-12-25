import React, { useState, useEffect } from "react";
import { AdminCategoriesMaterialService } from "../../api";

const CategoryMaterialManagement = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingCategoryId, setEditingCategoryId] = useState(null); // ID редактируемой категории (null для добавления)
  const [newCategory, setNewCategory] = useState({ name: "" });
  const [formError, setFormError] = useState("");

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await AdminCategoriesMaterialService.getAllCategories();
        setCategories(data.sort((a, b) => a.id - b.id));
      } catch (err) {
        setError("Ошибка загрузки категорий материалов");
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  const handleEdit = (categoryId) => {
    const categoryToEdit = categories.find((category) => category.id === categoryId);
    if (categoryToEdit) {
      setEditingCategoryId(categoryId);
      setNewCategory({ name: categoryToEdit.name });
      setShowModal(true);
    }
  };

  const handleDelete = async (categoryId) => {
    if (window.confirm(`Вы уверены, что хотите удалить категорию с ID: ${categoryId}?`)) {
      try {
        await AdminCategoriesMaterialService.deleteCategory(categoryId);
        setCategories(categories.filter((category) => category.id !== categoryId));
        alert(`Категория с ID: ${categoryId} успешно удалена.`);
      } catch (err) {
        alert(`Ошибка при удалении категории с ID: ${categoryId}.`);
      }
    }
  };

  const handleAddCategory = () => {
    setFormError("");
    setEditingCategoryId(null);
    setNewCategory({ name: "" });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setFormError("");
  };

  const handleSaveCategory = async () => {
    try {
      setFormError("");

      if (editingCategoryId) {
        // Обновление категории
        await AdminCategoriesMaterialService.updateCategory(editingCategoryId, newCategory);
        const updatedCategories = categories.map((category) =>
          category.id === editingCategoryId ? { ...category, ...newCategory } : category
        );
        setCategories(updatedCategories.sort((a, b) => a.id - b.id));
      } else {
        // Добавление новой категории
        const createdCategory = await AdminCategoriesMaterialService.createCategory(newCategory);
        const updatedCategories = [...categories, createdCategory];
        setCategories(updatedCategories.sort((a, b) => a.id - b.id));
      }

      setShowModal(false);
    } catch (err) {
      setFormError(err.detail || "Ошибка при сохранении категории");
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h2>Управление категориями материалов</h2>

      <div className="table-wrapper" style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
        <table className="table table-striped" style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((category) => (
              <tr key={category.id}>
                <td>{category.id}</td>
                <td>{category.name}</td>
                <td>
                  <button
                    className="btn btn-primary me-2"
                    onClick={() => handleEdit(category.id)}
                  >
                    Изменить
                  </button>
                  <button
                    className="btn custom-btn btn-danger"
                    onClick={() => handleDelete(category.id)}
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
          onClick={handleAddCategory}
        >
          Добавить категорию
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
                handleSaveCategory();
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
              <h5>{editingCategoryId ? "Редактировать категорию" : "Добавить новую категорию"}</h5>
              <div className="mb-3">
                <label htmlFor="name">Название</label>
                <input
                  type="text"
                  id="name"
                  className="form-control"
                  value={newCategory.name}
                  onChange={(e) => setNewCategory({ name: e.target.value })}
                  required
                />
                <div className="invalid-feedback">Пожалуйста, укажите название категории.</div>
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

export default CategoryMaterialManagement;
