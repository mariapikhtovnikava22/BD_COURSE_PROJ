import React, { useEffect, useState } from "react";
import { userService } from "../api";
import Header from "../components/Header";
import Footer from "../components/Footer";

const UserInfo = () => {
  const [userData, setUserData] = useState(null);
  const [progressData, setProgressData] = useState(null); // Данные о прогрессе
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formError, setFormError] = useState("");
  const [success, setSuccess] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    fio: "",
    email: "",
    old_password: "",
    new_password: "",
  });

  // Получение данных о пользователе и прогрессе
  useEffect(() => {
    const fetchData = async () => {
      try {
        const userInfo = await userService.aboutme();
        const progressInfo = await userService.UserProgress();
        setUserData(userInfo);
        setProgressData(progressInfo);
        setFormData({
          fio: userInfo.fio || "",
          email: userInfo.email || "",
          old_password: "",
          new_password: "",
        });
      } catch (err) {
        setError(err.message || "Ошибка загрузки данных.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Обработка изменений в форме
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Валидация email
  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Сохранение изменений
  const handleSave = async () => {
    setFormError("");
    try {
      if (formData.email && !isValidEmail(formData.email)) {
        setFormError("Введите корректный email.");
        return;
      }
      if (
        (formData.old_password && !formData.new_password) ||
        (!formData.old_password && formData.new_password)
      ) {
        setFormError("Для изменения пароля необходимо указать старый и новый пароли.");
        return;
      }
      const filteredData = Object.fromEntries(
        Object.entries(formData).filter(([_, value]) => value)
      );
      await userService.updateme(filteredData);
      setUserData((prev) => ({ ...prev, ...filteredData }));
      setSuccess("Данные успешно обновлены.");
      setTimeout(() => {
        setShowModal(false);
        setSuccess("");
      }, 1500);
    } catch (err) {
      setFormError(err.message || "Не удалось обновить данные.");
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>Ошибка: {error}</div>;

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
      <h1 style={{ padding: "20px" }}>Ваша личная информация</h1>
      <div
        style={{
          padding: "0 50px",
          boxSizing: "border-box",
        }}
      >
        <div className="card mt-3 p-3">
          <p>
            <strong>ФИО:</strong> {userData.fio}
          </p>
          <p>
            <strong>Email:</strong> {userData.email}
          </p>
          <p>
            <strong>Активен:</strong> {userData.is_active ? "Да" : "Нет"}
          </p>
          <p>
            <strong>Уровень:</strong> {userData.level || "Не указан"}
          </p>
          <p>
            <strong>Вступительный тест:</strong>{" "}
            {userData.entrance_test ? "Пройден" : "Не пройден"}
          </p>
        </div>
        <button
          className="custom-btn mt-3"
          onClick={() => setShowModal(true)}
        >
          Редактировать данные
        </button>

        {/* Контейнер для прогресса */}
        {progressData && (
          <div className="card mt-4 p-3">
            <h3>Прогресс по курсу</h3>
            <p>
              <strong>Завершён:</strong>{" "}
              {progressData.course_progress?.is_complite_course ? "Да" : "Нет"}
            </p>
            <p>
              <strong>Процент завершения:</strong>{" "}
              {progressData.course_progress?.completion_percentage ?? 0}%
            </p>
            <p>
              <strong>Завершённые модули:</strong>{" "}
              {progressData.course_progress?.modules_complite ?? 0}
            </p>
            <h3 className="mt-4">Прогресс по тестам</h3>
            {progressData.tests_progress && progressData.tests_progress.length > 0 ? (
              <ul>
                {progressData.tests_progress.map((test) => (
                  <li key={test.test_id}>
                    <strong>Тест #{test.test_id}:</strong>{" "}
                    {test.is_passed ? "Пройден" : "Не пройден"} | Попытки: {test.attempts} |{" "}
                    Правильных ответов: {test.correct_answers}
                  </li>
                ))}
              </ul>
            ) : (
              <p>Нет данных о прогрессе по тестам.</p>
            )}
          </div>
        )}
      </div>

      {/* Модальное окно */}
      {showModal && (
        <div
          className="modal d-flex justify-content-center align-items-center"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            textAlign: "center",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            zIndex: 1050,
          }}
        >
          <div
            className="modal-content p-4"
            style={{
              backgroundColor: "#fff",
              borderRadius: "10px",
              width: "400px",
              textAlign: "left",
            }}
          >
            <h5 style={{ marginBottom: "20px", textAlign: "center" }}>
              Редактировать данные
            </h5>
            <form>
              <div className="mb-3">
                <label className="form-label">ФИО:</label>
                <input
                  type="text"
                  className="form-control"
                  name="fio"
                  value={formData.fio}
                  onChange={handleChange}
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Email:</label>
                <input
                  type="email"
                  className="form-control"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Текущий пароль:</label>
                <input
                  type="password"
                  className="form-control"
                  name="old_password"
                  value={formData.old_password}
                  onChange={handleChange}
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Новый пароль:</label>
                <input
                  type="password"
                  className="form-control"
                  name="new_password"
                  value={formData.new_password}
                  onChange={handleChange}
                />
              </div>
            </form>
            {formError && <div className="alert alert-danger mt-3">{formError}</div>}
            {success && <div className="alert alert-success mt-3">{success}</div>}
            <div className="d-flex justify-content-between mt-4">
              <button
                className="btn-modal-secondary"
                onClick={() => {
                  setShowModal(false);
                  setFormError("");
                }}
              >
                Отмена
              </button>
              <button className="btn-modal-first" onClick={handleSave}>
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
};

export default UserInfo;
