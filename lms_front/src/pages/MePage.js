import React, { useEffect, useState } from "react";
import { userService } from "../api";
import Header from "../components/Header";
import Footer from "../components/Footer";

const UserInfo = () => {

  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false); // Для управления модальным окном
  const [formData, setFormData] = useState({
    fio: "",
    email: "",
    old_password: "",
    new_password: "",
  });
  const [success, setSuccess] = useState("");
  const [formError, setFormError] = useState("");

  // Получение данных о пользователе
  useEffect(() => {
    setError("");
    const fetchUserInfo = async () => {
      try {
        const data = await userService.aboutme(); // API-запрос на получение данных
        setUserData(data);
        setFormData({
          fio: data.fio || "",
          email: data.email || "",
          old_password: "",
          new_password: "",
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  // Обработка изменений в форме
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Проверка валидности email
  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Фильтрация данных для отправки
  const filterFormData = () => {
    const filteredData = {};
    Object.keys(formData).forEach((key) => {
      if (formData[key]) {
        filteredData[key] = formData[key];
      }
    });
    return filteredData;
  };

  // Сохранение изменений
  const handleSave = async () => {
    setFormError(""); // Сброс ошибки
    // Валидация полей

    if (formData.email && !isValidEmail(formData.email)) {
      setFormError("Введите корректный email.");
      return;
    }

    const filteredData = filterFormData();

    // Валидация: если введен только старый или только новый пароль
    if ((formData.old_password && !formData.new_password) || (!formData.old_password && formData.new_password)) {
      setFormError("Для изменения пароля необходимо ввести текущий и новый пароли.");
      return;}

    // Если нет изменений, не отправляем запрос
    if (Object.keys(filteredData).length === 0) {
      setFormError("Нет данных для обновления.");
      return;
    }

    try {
      await userService.updateme(filteredData); // API-запрос для обновления данных
      setUserData((prev) => ({
        ...prev,
        ...filteredData,
      }));
      setSuccess("Данные успешно обновились");
      setTimeout(() => {
        setShowModal(false);
        setSuccess("");
      }, 1000);
    } catch (err) {
      console.log("er", err);
      setFormError(err || "Не удалось обновить данные.");
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>Ошибка: {error}</div>;

  const handleCloseModal = () => {
    setShowModal(false); // Закрытие окна
    setFormError("");    // Сброс ошибки
  };

    return (
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
          backgroundColor: "#F7F3EF",
          flex: "1",
        }}
      >
        <Header />
        <h1 style={{padding: "20px"}}>Ваша личная информация</h1>
          
        <div
    style={{
      padding: "0 50px", // Отступы по 50px слева и справа
      boxSizing: "border-box", 
      flex: "1",// Учитывает отступы в ширине
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
      onClick={() => setShowModal(true)} // Открытие модального окна
    >
      Редактировать данные
    </button>
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
            <h5 style={{ marginBottom: "20px", textAlign:"center" }}>Редактировать данные</h5>
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
                onClick={handleCloseModal}// Закрытие окна
              >
                Отмена
              </button>
              <button
                className="btn-modal-first"
                style={{ width: "45%" }}
                onClick={handleSave} // Сохранение данных
              >
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
