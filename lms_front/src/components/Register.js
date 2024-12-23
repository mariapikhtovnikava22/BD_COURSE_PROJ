import React, { useState } from "react";
import { userService } from "../api";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ fio: "", email: "", password: "", image: null });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleFileChange = (e) => {
    setFormData({ ...formData, image: e.target.files[0] });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    const formDataToSend = new FormData();
    formDataToSend.append("fio", formData.fio);
    formDataToSend.append("email", formData.email);
    formDataToSend.append("password", formData.password);

    try {
      const response = await userService.register(formDataToSend);

      if (response.detail) {
        setError(response.detail);
        return;
      }

      localStorage.setItem('Token', response.access_token);

      setSuccess("Вы успешно зарегистрировались!");
      setTimeout(() => {
        navigate('/');
      }, 1000);
    } catch (error) {
      setError(error.response?.data?.detail || error.response?.data?.email || "Ошибка регистрации. Проверьте данные и попробуйте снова.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">ФИО:</label>
                  <input
                    type="text"
                    className="form-control"
                    style={{ borderRadius: "5px", border: "1px solid #D2C4B3" }}
                    name="fio"
                    value={formData.fio}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Почта:</label>
                  <input
                    type="email"
                    className="form-control"
                    style={{ borderRadius: "5px", border: "1px solid #D2C4B3" }}
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Пароль:</label>
                  <input
                    type="password"
                    className="form-control"
                    style={{ borderRadius: "5px", border: "1px solid #D2C4B3" }}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="btn w-100"
                  style={{ backgroundColor: "#5A3E36", color: "#fff", borderRadius: "5px", border: "none" }}
                  disabled={isLoading}
                >
                  {isLoading ? "Загрузка..." : "Зарегистрироваться"}
                </button>
              </form>
              {error && <div className="alert alert-danger mt-3">{error}</div>}
              {success && <div className="alert alert-success mt-3">{success}</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;