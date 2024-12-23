const API_BASE_URL = 'http://localhost:8000';

const handleErrors = async (response) => {
  try {
    // Если HTTP-статус не 2xx
    if (!response.ok) {
      const errorData = await response.json().catch(() => null); // Пытаемся распарсить JSON

      // Если ошибка содержит объект (например, {"error": {...}})
      if (errorData && typeof errorData === "object") {
        if (errorData.error) {
          console.log(errorData.error);
          throw errorData.error; // Бросаем вложенный объект ошибки
        }
        if (errorData.detail) {
          throw { detail: errorData.detail }; // Если есть detail
        }
        throw errorData; // Бросаем весь объект ошибки
      }

      // Если это строка или другой формат (например, plain text)
      const errorMessage = await response.text().catch(() => "Ошибка сервера");
      throw { detail: errorMessage || "Ошибка сервера" }; // Упаковываем текст в объект
    }

    // Если всё ок, возвращаем данные
    return await response.json();
  } catch (error) {
    // Если при обработке произошла ошибка, выбрасываем
    throw error;
  }
};

// Генерация заголовков
const getHeaders = (isJSON = true) => {
  const headers = {};
  console.log(localStorage.getItem("Token"));
  const token = localStorage.getItem("Token"); // Токен из localStorage
  if (token) {
    headers["Authorization"] = `Token ${token}`; // Используем формат Token
  }
  if (isJSON) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
};

export const userService = {

  // Авторизация пользователя
  login: async (credentials) => {
    const response = await fetch(`${API_BASE_URL}/api/users/login/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(credentials),
    });
    return handleErrors(response);
  },

  // Регистрация пользователя
  register: async (formData) => {
    const response = await fetch(`${API_BASE_URL}/api/users/register/`, {
      method: 'POST',
      body: formData,
    });
    return handleErrors(response);
  },

  aboutme: async () => {
    const response = await fetch(`${API_BASE_URL}/api/users/about_me`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

//   updatepassword: async (formData) => {
//     const response = await fetch(`${API_BASE_URL}/api/auth/update_password`, {
//       method: 'PUT',
//       headers: getHeaders(true),
//       body: JSON.stringify(formData),
//     });
//     return handleErrors(response);
//   },
};