import React, { useState, useEffect } from "react";
import { AdminModulesService, AdminTopicsService, AdminLevelsService } from "../../api";

const ModuleTopicManagement = () => {
  const [modules, setModules] = useState([]);
  const [topics, setTopics] = useState([]);
  const [levels, setLevels] = useState([]); // Уровни для выпадающего списка
  const [expandedModuleId, setExpandedModuleId] = useState(null); // ID раскрытого модуля
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showTopicModal, setShowTopicModal] = useState(false);
  const [showModuleModal, setShowModuleModal] = useState(false);
  const [newTopic, setNewTopic] = useState({ name: "", description: "" });
  const [newModule, setNewModule] = useState({ name: "", description: "", level_id: "" });
  const [currentModuleId, setCurrentModuleId] = useState(null); // ID модуля для добавления или редактирования темы
  const [currentModuleEditId, setCurrentModuleEditId] = useState(null); // ID модуля для редактирования
  const [currentTopicId, setCurrentTopicId] = useState(null); // ID темы для редактирования
  const [formError, setFormError] = useState(""); // Ошибка формы
  const [success, setSuccess] = useState(""); // Успех

  const fetchData = async () => {
    try {
      const [modulesData, topicsData, levelsData] = await Promise.all([
        AdminModulesService.getAllModules(),
        AdminTopicsService.getAllTopics(),
        AdminLevelsService.getalllevels(),
      ]);

      setModules(modulesData);
      setTopics(topicsData);
      setLevels(levelsData);
    } catch (err) {
      setError("Ошибка загрузки данных");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getTopicsByModuleName = (moduleName) => {
    console.log(moduleName);
    return topics.filter((topic) => topic.module_name === moduleName);
  };

  const toggleModule = (moduleId) => {
    setExpandedModuleId(expandedModuleId === moduleId ? null : moduleId);
  };

  const handleAddTopic = (moduleId) => {
    setCurrentModuleId(moduleId);
    setCurrentTopicId(null);
    setNewTopic({ name: "", description: "" });
    setFormError("");
    setSuccess("");
    setShowTopicModal(true);
  };

  const handleEditTopic = (topic) => {
    setCurrentModuleId(topic.module_id);
    setCurrentTopicId(topic.id);
    setNewTopic({ name: topic.name, description: topic.description });
    setFormError("");
    setSuccess("");
    setShowTopicModal(true);
  };

  const handleDeleteTopic = async (topicId) => {
    if (window.confirm("Вы уверены, что хотите удалить тему?")) {
      try {
        await AdminTopicsService.deleteTopic(topicId);
        setTopics((prevTopics) => prevTopics.filter((topic) => topic.id !== topicId));
      } catch (error) {
        console.error("Ошибка при удалении темы:", error);
      }
    }
  };

  const handleEditModule = (module) => {
    console.log("Редактируемый модуль:", module);
  
    // Находим level_id по level_name
    const matchedLevel = levels.find((level) => level.name === module.level_name);
  
    setCurrentModuleEditId(module.id); // Сохраняем ID модуля
    setNewModule({
      name: module.name,
      description: module.description,
      level_id: matchedLevel ? matchedLevel.id : "", // Устанавливаем level_id или пустое значение
    });
    setFormError("");
    setSuccess("");
    setShowModuleModal(true);
  };
  
  const handleDeleteModule = async (moduleId) => {
    if (window.confirm("Вы уверены, что хотите удалить модуль?")) {
      try {
        await AdminModulesService.deleteModule(moduleId);
        setModules((prevModules) => prevModules.filter((module) => module.id !== moduleId));
      } catch (error) {
        console.error("Ошибка при удалении модуля:", error);
      }
    }
  };

  const saveModule = async () => {
    if (!newModule.name.trim() || !newModule.level_id) {
      setFormError("Название модуля и уровень обязательны");
      return;
    }
  
    try {
      let updatedModule;
      if (currentModuleEditId) {
        // Редактирование модуля
        updatedModule = await AdminModulesService.updateModule(currentModuleEditId, newModule);
        setModules((prevModules) =>
          prevModules.map((module) => (module.id === currentModuleEditId ? updatedModule : module))
        );
  
        // Обновление module_name у связанных тем
        setTopics((prevTopics) =>
          prevTopics.map((topic) =>
            topic.module_name === modules.find((m) => m.id === currentModuleEditId)?.name
              ? { ...topic, module_name: updatedModule.name }
              : topic
          )
        );
      } else {
        // Добавление нового модуля
        const createdModule = await AdminModulesService.createModule(newModule);
        setModules((prevModules) => [...prevModules, createdModule]);
      }
  
      setSuccess("Модуль успешно сохранен!");
      setTimeout(() => {
        setShowModuleModal(false);
        setSuccess("");
      }, 1000);
    } catch (error) {
      console.error("Ошибка при сохранении модуля:", error);
      setFormError(error || "Не удалось сохранить модуль");
    }
  };
  

  const saveTopic = async () => {
    if (!newTopic.name.trim()) {
      setFormError("Название темы обязательно");
      return;
    }

    try {
      if (currentTopicId) {
        // Редактирование темы
        const updatedTopic = await AdminTopicsService.updateTopic(currentTopicId, {
          ...newTopic,
          module_id: currentModuleId,
        });

        setTopics((prevTopics) =>
          prevTopics.map((topic) =>
            topic.id === currentTopicId ? { ...updatedTopic, module_name: updatedTopic.module_name } : topic
          )
        );
      } else {
        // Добавление новой темы
        const createdTopic = await AdminTopicsService.createTopic({
          ...newTopic,
          module_id: currentModuleId,
        });

        setTopics((prevTopics) => [
          ...prevTopics,
          { ...createdTopic, module_name: modules.find((m) => m.id === currentModuleId)?.name },
        ]);
      }

      setSuccess("Тема успешно сохранена!");
      setTimeout(() => {
        setShowTopicModal(false);
        setSuccess("");
      }, 1000);
    } catch (error) {
      console.error("Ошибка при сохранении темы:", error);
      setFormError(error || "Не удалось сохранить тему");
    }
  };

  return (
  <div>
    <h2 className="my-4">Программа курса</h2>
    <div>
      {modules.map((module) => (
        <div key={module.id} className="module mb-4">
          <div className="d-flex justify-content-between align-items-center p-3 bg-light rounded">
            <div>
              <h5 className="mb-0">{module.name}</h5>
              {module.description && <small className="text-muted">{module.description}</small>}
            </div>
            <div>
            <button
                className="btn btn-sm me-2"
                onClick={() => handleEditModule(module)}
                title="Редактировать"
                style={{ border: "none", background: "transparent", fontSize: "1rem" }}
            >
                ✏️
            </button>
            <button
                className="btn btn-sm me-2"
                onClick={() => handleDeleteModule(module.id)}
                title="Удалить"
                style={{ border: "none", background: "transparent", fontSize: "1rem" }}
            >
                🗑️
            </button>
            <button
                className="btn  btn-sm"
                onClick={() => toggleModule(module.id)}
                title={expandedModuleId === module.id ? "Свернуть" : "Развернуть"}
                style={{ border: "none", background: "transparent", fontSize: "1rem" }}
            >
                {expandedModuleId === module.id ? "🔼" : "🔽"}
            </button>
            </div>

          </div>

          {expandedModuleId === module.id && (
            <div className="topics mt-3 ps-4">
              <h6>Темы:</h6>
              <ul className="list-group">
                {getTopicsByModuleName(module.name).map((topic) => (
                  <li key={topic.id} className="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{topic.name}</strong>
                      {topic.description && <small className="text-muted d-block">{topic.description}</small>}
                    </div>
                    <div>
                      <button
                        className="btn btn-primary btn-sm me-2"
                        onClick={() => handleEditTopic(topic)}
                      >
                        Редактировать
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDeleteTopic(topic.id)}
                      >
                        Удалить
                      </button>
                    </div>
                  </li>
                ))}
                {getTopicsByModuleName(module.name).length === 0 && (
                  <p className="text-muted">Темы отсутствуют</p>
                )}
              </ul>
              <button
                className="btn btn-success mt-3"
                onClick={() => handleAddTopic(module.id)}
              >
                Добавить тему
              </button>
            </div>
          )}
        </div>
      ))}
    </div>

    <button className="btn btn-success mt-4" onClick={() => setShowModuleModal(true)}>
      Добавить новый модуль
    </button>

    {/* Модальное окно для тем */}
    {showTopicModal && (
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
          onSubmit={(e) => e.preventDefault()}
          style={{
            backgroundColor: "#fff",
            borderRadius: "10px",
            padding: "20px",
            width: "400px",
          }}
        >
          <h5>{currentTopicId ? "Редактировать тему" : "Добавить тему"}</h5>
          <div className="mb-3">
            <label htmlFor="topicName">Название темы</label>
            <input
              type="text"
              id="topicName"
              className="form-control"
              value={newTopic.name}
              onChange={(e) => setNewTopic({ ...newTopic, name: e.target.value })}
            />
          </div>
          <div className="mb-3">
            <label htmlFor="topicDescription">Описание</label>
            <textarea
              id="topicDescription"
              className="form-control"
              value={newTopic.description}
              onChange={(e) => setNewTopic({ ...newTopic, description: e.target.value })}
            />
          </div>

          {formError && <div className="alert alert-danger">{formError}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <div className="text-end">
            <button
              className="btn btn-secondary me-2"
              onClick={() => setShowTopicModal(false)}
            >
              Отмена
            </button>
            <button className="btn btn-primary" onClick={saveTopic}>
              Сохранить
            </button>
          </div>
        </form>
      </div>
    )}

    {/* Модальное окно для модулей */}
    {showModuleModal && (
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
          onSubmit={(e) => e.preventDefault()}
          style={{
            backgroundColor: "#fff",
            borderRadius: "10px",
            padding: "20px",
            width: "400px",
          }}
        >
          <h5>{currentModuleEditId ? "Редактировать модуль" : "Добавить модуль"}</h5>
          <div className="mb-3">
            <label htmlFor="moduleName">Название модуля</label>
            <input
              type="text"
              id="moduleName"
              className="form-control"
              value={newModule.name}
              onChange={(e) => setNewModule({ ...newModule, name: e.target.value })}
            />
          </div>
          <div className="mb-3">
            <label htmlFor="moduleDescription">Описание</label>
            <textarea
              id="moduleDescription"
              className="form-control"
              value={newModule.description}
              onChange={(e) => setNewModule({ ...newModule, description: e.target.value })}
            />
          </div>
          <div className="mb-3">
            <label htmlFor="moduleLevel">Уровень</label>
            <select
              id="moduleLevel"
              className="form-control"
              value={newModule.level_id || ""}
              onChange={(e) => setNewModule({ ...newModule, level_name: e.target.value })}
            >
              <option value="">Выберите уровень</option>
              {levels.map((level) => (
                <option key={level.id} value={level.id}>
                  {level.name}
                </option>
              ))}
            </select>
          </div>

          {formError && <div className="alert alert-danger">{formError}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <div className="text-end">
            <button
              className="btn btn-secondary me-2"
              onClick={() => setShowModuleModal(false)}
            >
              Отмена
            </button>
            <button className="btn btn-primary" onClick={saveModule}>
              Сохранить
            </button>
          </div>
        </form>
      </div>
    )}
  </div>
);
};

export default ModuleTopicManagement;
