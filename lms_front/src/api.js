const API_BASE_URL = 'http://localhost:8000';

const handleErrors = async (response) => {
  try {
    // Если HTTP-статус не 2xx
    if (!response.ok) {
      const errorData = await response.json().catch(() => null); // Пытаемся распарсить JSON

      // Если ошибка содержит объект (например, {"error": {...}})
      if (errorData && typeof errorData === "object") {
        if (errorData.error) {
          console.log("api", errorData.error);
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
    const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(credentials),
    });
    return handleErrors(response);
  },

  // Регистрация пользователя
  register: async (formData) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
      method: 'POST',
      body: formData,
    });
    return handleErrors(response);
  },

  aboutme: async () => {
    const response = await fetch(`${API_BASE_URL}/api/auth/about_me/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);

  },

  updateme: async (formData) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/about_me/`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(formData),
    });
    return handleErrors(response);

  },
};


export const AdminUserService = {

  getallusers: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/users/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);

  },
  get_users: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/users/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },  
  // Получение одного пользователя по ID
  getUserById: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  // Создание нового пользователя
  createUser: async (userData) => {
    console.log(JSON.stringify(userData));
    const response = await fetch(`${API_BASE_URL}/api/admin/users/`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(userData),
    });
    return handleErrors(response);
  },

  // Обновление данных пользователя
  updateUser: async (userId, userData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(userData),
    });
    return handleErrors(response);
  },

  // Удаление пользователя
  deleteUser: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },
};


export const AdminRolesService = {

  // Получение всех ролей
  getallroles: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/roles/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  // Получение роли по ID
  getRoleById: async (roleId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/roles/${roleId}/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  // Создание новой роли
  createRole: async (roleData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/roles/`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(roleData),
    });
    return handleErrors(response);
  },

  // Обновление роли
  updateRole: async (roleId, roleData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/roles/${roleId}/`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(roleData),
    });
    return handleErrors(response);
  },

  // Удаление роли
  deleteRole: async (roleId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/roles/${roleId}/`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },
};



export const AdminLevelsService = {
  // Получение всех уровней
  getalllevels: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/levels/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  // Получение уровня по ID
  getLevelById: async (levelId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/levels/${levelId}/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  // Создание нового уровня
  createLevel: async (levelData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/levels/`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(levelData),
    });
    return handleErrors(response);
  },

  // Обновление уровня по ID
  updateLevel: async (levelId, levelData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/levels/${levelId}/`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(levelData),
    });
    return handleErrors(response);
  },

  // Удаление уровня по ID
  deleteLevel: async (levelId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/levels/${levelId}/`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },
};

export const AdminCategoriesMaterialService = {
  // Получение всех категорий материалов
  getAllCategories: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/categoriesmaterial/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  // Получение категории материалов по ID
  getCategoryById: async (categoryId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/categoriesmaterial/${categoryId}/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  // Создание новой категории материалов
  createCategory: async (categoryData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/categoriesmaterial/`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(categoryData),
    });
    return handleErrors(response);
  },

  // Обновление категории материалов по ID
  updateCategory: async (categoryId, categoryData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/categoriesmaterial/${categoryId}/`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(categoryData),
    });
    return handleErrors(response);
  },

  // Удаление категории материалов по ID
  deleteCategory: async (categoryId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/categoriesmaterial/${categoryId}/`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },
};

export const AdminModulesService = {
  getAllModules: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/modules/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  getModuleById: async (moduleId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/modules/${moduleId}/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  createModule: async (moduleData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/modules/`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(moduleData),
    });
    return handleErrors(response);
  },

  updateModule: async (moduleId, moduleData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/modules/${moduleId}/`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(moduleData),
    });
    return handleErrors(response);
  },

  deleteModule: async (moduleId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/modules/${moduleId}/`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },
};

export const AdminTopicsService = {
  getAllTopics: async () => {
    const response = await fetch(`${API_BASE_URL}/api/admin/topics/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  getTopicById: async (topicId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/topics/${topicId}/`, {
      method: 'GET',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },

  createTopic: async (topicData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/topics/`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(topicData),
    });
    return handleErrors(response);
  },

  updateTopic: async (topicId, topicData) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/topics/${topicId}/`, {
      method: 'PUT',
      headers: getHeaders(true),
      body: JSON.stringify(topicData),
    });
    return handleErrors(response);
  },

  deleteTopic: async (topicId) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/topics/${topicId}/`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return handleErrors(response);
  },
};


