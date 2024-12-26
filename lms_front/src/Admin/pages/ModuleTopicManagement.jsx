import React, { useState, useEffect } from "react";
import {
  AdminModulesService,
  AdminTopicsService,
  AdminLevelsService,
  AdminMaterialsService,
  AdminCategoriesMaterialService,
  
} from "../../api";
import BASE_BACKEND_URL from "../../config";

const ModuleTopicManagement = () => {
  // Состояния для модулей, тем, уровней и категорий
  const [modules, setModules] = useState([]);
  const [topics, setTopics] = useState([]);
  const [levels, setLevels] = useState([]);
  const [categories, setCategories] = useState([]);

  // Состояния для материалов
  const [materialsByTopic, setMaterialsByTopic] = useState({});
  const [expandedModuleId, setExpandedModuleId] = useState(null);
  const [expandedTopicIds, setExpandedTopicIds] = useState([]);

  // Состояния для загрузки и ошибок
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formError, setFormError] = useState("");
  const [success, setSuccess] = useState("");

  // Состояния для модальных окон
  const [showTopicModal, setShowTopicModal] = useState(false);
  const [showModuleModal, setShowModuleModal] = useState(false);
  const [showMaterialModal, setShowMaterialModal] = useState(false);

  // Данные для модальных окон
  const [newTopic, setNewTopic] = useState({ name: "", description: "" });
  const [currentModuleId, setCurrentModuleId] = useState(null);
  const [currentTopicId, setCurrentTopicId] = useState(null);
  const [newModule, setNewModule] = useState({ name: "", description: "", level_id: "" });
  const [currentModuleEditId, setCurrentModuleEditId] = useState(null);

  // Данные для модального окна материалов
  const [currentMaterial, setCurrentMaterial] = useState(null); // объект материала для редактирования
  const [newMaterial, setNewMaterial] = useState({
    topic_id: "",
    categorymaterials_id: "",
    content: "",
    file: null,
  });

  // Состояние для фильтра по уровню
  const [selectedLevelId, setSelectedLevelId] = useState("");

  // Загрузка данных при монтировании компонента
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [modulesData, topicsData, levelsData, categoriesData] = await Promise.all([
          AdminModulesService.getAllModules(),
          AdminTopicsService.getAllTopics(),
          AdminLevelsService.getalllevels(),
          AdminCategoriesMaterialService.getAllCategories(),
        ]);

        setModules(modulesData);
        setTopics(topicsData);
        setLevels(levelsData);
        setCategories(categoriesData);
      } catch (err) {
        console.error("Ошибка загрузки данных:", err);
        setError("Ошибка загрузки данных");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Фильтрация тем по названию модуля
  const getTopicsByModuleName = (moduleName) =>
    topics.filter((topic) => topic.module_name === moduleName);

  // Переключение раскрытия модуля
  const toggleModule = (moduleId) => {
    setExpandedModuleId((prev) => (prev === moduleId ? null : moduleId));
  };

  // Переключение раскрытия материалов темы
  const toggleTopicMaterials = async (topicId) => {
    if (expandedTopicIds.includes(topicId)) {
      setExpandedTopicIds((prev) => prev.filter((id) => id !== topicId));
      return;
    }

    setExpandedTopicIds((prev) => [...prev, topicId]);

    if (!materialsByTopic[topicId]) {
      try {
        const materials = await AdminMaterialsService.getAllMaterials();
        const topicMaterials = materials.filter((mat) => mat.topic_id === topicId);
        setMaterialsByTopic((prev) => ({
          ...prev,
          [topicId]: topicMaterials,
        }));
      } catch (err) {
        console.error("Ошибка при загрузке материалов:", err);
        setFormError("Не удалось загрузить материалы.");
      }
    }
  };

  // Добавление новой темы
  const handleAddTopic = (moduleId) => {
    setCurrentModuleId(moduleId);
    setCurrentTopicId(null);
    setNewTopic({ name: "", description: "" });
    setFormError("");
    setSuccess("");
    setShowTopicModal(true);
  };

  // Редактирование существующей темы
  const handleEditTopic = (topic) => {
    setCurrentModuleId(topic.module_id);
    setCurrentTopicId(topic.id);
    setNewTopic({ name: topic.name, description: topic.description });
    setFormError("");
    setSuccess("");
    setShowTopicModal(true);
  };

  // Удаление темы
  const handleDeleteTopic = async (topicId) => {
    if (window.confirm("Вы уверены, что хотите удалить тему?")) {
      try {
        await AdminTopicsService.deleteTopic(topicId);
        setTopics((prevTopics) => prevTopics.filter((t) => t.id !== topicId));
        setMaterialsByTopic((prev) => {
          const newMaterials = { ...prev };
          delete newMaterials[topicId];
          return newMaterials;
        });
      } catch (error) {
        console.error("Ошибка при удалении темы:", error);
        setFormError("Не удалось удалить тему.");
      }
    }
  };

  // Добавление или редактирование модуля
  const handleEditModule = (module) => {
    setCurrentModuleEditId(module.id);
    setNewModule({
      name: module.name,
      description: module.description,
      level_id: module.level_id || "",
    });
    setFormError("");
    setSuccess("");
    setShowModuleModal(true);
  };

  // Удаление модуля
  const handleDeleteModule = async (moduleId) => {
    if (window.confirm("Вы уверены, что хотите удалить модуль?")) {
      try {
        await AdminModulesService.deleteModule(moduleId);
        setModules((prev) => prev.filter((m) => m.id !== moduleId));

        // Удаление тем и материалов, связанных с модулем
        const moduleTopics = topics.filter((t) => t.module_id === moduleId);
        const moduleTopicIds = moduleTopics.map((t) => t.id);
        setTopics((prev) => prev.filter((t) => t.module_id !== moduleId));
        setMaterialsByTopic((prev) => {
          const newMaterials = { ...prev };
          moduleTopicIds.forEach((id) => {
            delete newMaterials[id];
          });
          return newMaterials;
        });
      } catch (error) {
        console.error("Ошибка при удалении модуля:", error);
        setFormError("Не удалось удалить модуль.");
      }
    }
  };

  // Изменение фильтра по уровню
  const handleLevelFilterChange = (e) => {
    setSelectedLevelId(e.target.value);
  };

  // Сохранение модуля (добавление или редактирование)
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
        setModules((prev) =>
          prev.map((mod) => (mod.id === currentModuleEditId ? updatedModule : mod))
        );
      } else {
        // Создание нового модуля
        const createdModule = await AdminModulesService.createModule(newModule);
        setModules((prev) => [...prev, createdModule]);
      }
      setSuccess("Модуль успешно сохранен!");
      setTimeout(() => {
        setShowModuleModal(false);
        setSuccess("");
      }, 1000);
    } catch (error) {
      console.error("Ошибка при сохранении модуля:", error);
      setFormError(error.message || "Не удалось сохранить модуль");
    }
  };

  // Сохранение темы (добавление или редактирование)
  const saveTopic = async () => {
    if (!newTopic.name.trim()) {
      setFormError("Название темы обязательно");
      return;
    }
    try {
      let updatedTopic;
      if (currentTopicId) {
        // Редактирование темы
        updatedTopic = await AdminTopicsService.updateTopic(currentTopicId, {
          ...newTopic,
          module_id: currentModuleId,
        });
        updatedTopic = {
          ...updatedTopic,
          module_name: modules.find((m) => m.id === updatedTopic.module_id)?.name || "",
        };
        setTopics((prevTopics) =>
          prevTopics.map((t) => (t.id === currentTopicId ? updatedTopic : t))
        );
      } else {
        // Создание новой темы
        const createdTopic = await AdminTopicsService.createTopic({
          ...newTopic,
          module_id: currentModuleId,
        });
        updatedTopic = {
          ...createdTopic,
          module_name: modules.find((m) => m.id === createdTopic.module_id)?.name || "",
        };
        setTopics((prevTopics) => [...prevTopics, updatedTopic]);
      }
      setSuccess("Тема успешно сохранена!");
      setTimeout(() => {
        setShowTopicModal(false);
        setSuccess("");
      }, 1000);
    } catch (error) {
      console.error("Ошибка при сохранении темы:", error);
      setFormError(error.message || "Не удалось сохранить тему");
    }
  };

  // Добавление нового материала
  const handleAddMaterial = (topicId) => {
    setCurrentMaterial(null); // не редактируемый материал
    setNewMaterial({ topic_id: topicId, categorymaterials_id: "", content: "", file: null });
    setFormError("");
    setSuccess("");
    setShowMaterialModal(true);
  };

  // Редактирование существующего материала
  const handleEditMaterial = (material) => {
    setCurrentMaterial(material);
    setNewMaterial({
      topic_id: material.topic_id,
      categorymaterials_id: material.categorymaterials_id,
      content: material.content,
      file: null, // Файл необходимо перезагрузить при редактировании
    });
    setFormError("");
    setSuccess("");
    setShowMaterialModal(true);
  };

  // Сохранение материала (добавление или редактирование)
  const saveMaterial = async () => {
    if (!newMaterial.content || !newMaterial.categorymaterials_id) {
      setFormError("Укажите категорию и описание материала.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("topic_id", newMaterial.topic_id);
      formData.append("categorymaterials_id", newMaterial.categorymaterials_id);
      formData.append("content", newMaterial.content);
      if (newMaterial.file) {
        formData.append("file", newMaterial.file);
      }

      // Логирование данных для отладки
      console.log("Saving material:", {
        topic_id: newMaterial.topic_id,
        categorymaterials_id: newMaterial.categorymaterials_id,
        content: newMaterial.content,
        file: newMaterial.file,
      });

      for (let pair of formData.entries()) {
        console.log(`${pair[0]}: ${pair[1]}`);
      }

      let responseMaterial;
      if (currentMaterial) {
        // Редактирование существующего материала
        responseMaterial = await AdminMaterialsService.updateMaterial(currentMaterial.id, formData);
        setMaterialsByTopic((prev) => ({
          ...prev,
          [newMaterial.topic_id]: prev[newMaterial.topic_id].map((mat) =>
            mat.id === currentMaterial.id ? responseMaterial : mat
          ),
        }));
      } else {
        // Создание нового материала
        responseMaterial = await AdminMaterialsService.createMaterial(formData);
        setMaterialsByTopic((prev) => ({
          ...prev,
          [newMaterial.topic_id]: [...(prev[newMaterial.topic_id] || []), responseMaterial],
        }));
      }

      setSuccess("Материал успешно сохранён!");
      setShowMaterialModal(false);
    } catch (err) {
      console.error("Ошибка при сохранении материала:", err);
      setFormError(err.message || "Не удалось сохранить материал.");
    }
  };

  // Удаление материала
  const handleDeleteMaterial = async (topicId, materialId) => {
    if (!window.confirm("Удалить материал?")) return;

    try {
      await AdminMaterialsService.deleteMaterial(materialId);
      setMaterialsByTopic((prev) => ({
        ...prev,
        [topicId]: prev[topicId].filter((mat) => mat.id !== materialId),
      }));
      setSuccess("Материал успешно удалён!");
    } catch (err) {
      console.error("Ошибка при удалении материала:", err);
      setFormError("Не удалось удалить материал.");
    }
  };

  // Фильтрация модулей по уровню
  const filteredModules = selectedLevelId
    ? modules.filter((m) => m.level_id === parseInt(selectedLevelId))
    : modules;

  // Проверка заполненности обязательных полей для кнопки сохранить
  const isMaterialFormValid = newMaterial.topic_id && newMaterial.categorymaterials_id && newMaterial.content;

  // Отображение индикатора загрузки и ошибок
  if (loading) return <p>Загрузка...</p>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div>
      <h2 className="my-4">Программа курса</h2>

      {/* Фильтр по уровню */}
      <div className="mb-4">
        <label htmlFor="levelFilter">Фильтр по уровням: </label>
        <select
          id="levelFilter"
          className="form-control"
          value={selectedLevelId}
          onChange={handleLevelFilterChange}
        >
          <option value="">Все уровни</option>
          {levels.map((lvl) => (
            <option key={lvl.id} value={lvl.id}>
              {lvl.name}
            </option>
          ))}
        </select>
      </div>

      {/* Список модулей */}
      {filteredModules.map((module) => (
        <div key={module.id} className="module mb-4">
          <div className="d-flex justify-content-between align-items-center p-3 bg-light rounded">
            <div>
              <h5 className="mb-0">{module.name}</h5>
              {module.description && <small className="text-muted">{module.description}</small>}
              <small className="text-muted d-block">
                Уровень: {levels.find((l) => l.id === module.level_id)?.name || "Не указан"}
              </small>
            </div>
            <div>
              <button
                className="btn btn-sm me-2"
                onClick={() => handleEditModule(module)}
                style={{ border: "none", background: "transparent", fontSize: "1rem" }}
                title="Редактировать модуль"
              >
                ✏️
              </button>
              <button
                className="btn btn-sm me-2"
                onClick={() => handleDeleteModule(module.id)}
                style={{ border: "none", background: "transparent", fontSize: "1rem" }}
                title="Удалить модуль"
              >
                🗑️
              </button>
              <button
                className="btn btn-sm"
                onClick={() => toggleModule(module.id)}
                style={{ border: "none", background: "transparent", fontSize: "1rem" }}
                title={expandedModuleId === module.id ? "Свернуть темы" : "Развернуть темы"}
              >
                {expandedModuleId === module.id ? "🔼" : "🔽"}
              </button>
            </div>
          </div>

          {/* Если модуль раскрыт — показываем темы */}
          {expandedModuleId === module.id && (
            <div className="topics mt-3 ps-4">
              <h5>Темы:</h5>
              <ul className="list-group">
                {getTopicsByModuleName(module.name).map((topic) => (
                  <li key={topic.id} className="list-group-item d-flex flex-column" style={{ marginBottom: "8px" }}>
                    <div className="d-flex justify-content-between align-items-center">
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
                    </div>

                    {/* Кнопки для раскрытия материалов и добавления нового материала */}
                    <div className="mt-2">
                      <button
                        className="btn btn-sm btn-outline-info me-3"
                        onClick={() => toggleTopicMaterials(topic.id)}
                      >
                        {expandedTopicIds.includes(topic.id) ? "Скрыть материалы" : "Показать материалы"}
                      </button>
                      <button
                        className="btn btn-sm btn-success"
                        onClick={() => handleAddMaterial(topic.id)}
                      >
                        Добавить материал
                      </button>
                    </div>

                    {/* Список материалов */}
                    {expandedTopicIds.includes(topic.id) && (
                      <div className="mt-2 ms-3">
                        {materialsByTopic[topic.id]?.length ? (
                          materialsByTopic[topic.id].map((material) => (
                            <div key={material.id} className="d-flex justify-content-between align-items-center border p-2 mb-1 rounded">
                              <div>
                                <p className="mb-1">
                                  <strong>Контент:</strong> {material.content}
                                </p>
                                <div className="file-container" style={{ wordBreak: "break-word" }}>
                                {material.file_url ? (
      <a
        href={`${BASE_BACKEND_URL}${material.file_url}`}
        target="_blank"
        rel="noreferrer"
        style={{
          textOverflow: "ellipsis",
          overflow: "hidden",
          display: "inline-block",
          maxWidth: "100%",
        }}
        title={material.file_url} // Полный путь при наведении
      >
        {decodeURIComponent(material.file_url.split("/").pop())}
      </a>
    ) : (
      <span className="text-muted">Файл отсутствует</span>
    )}
</div>
                                
                              </div>
                              <div>
                                <button
                                  className="btn btn-sm btn-primary me-2"
                                  onClick={() => handleEditMaterial(material)}
                                >
                                  Ред.
                                </button>
                                <button
                                  className="btn btn-sm btn-danger"
                                  onClick={() => handleDeleteMaterial(topic.id, material.id)}
                                >
                                  Уд.
                                </button>
                              </div>
                            </div>
                          ))
                        ) : (
                          <p className="text-muted">Нет материалов</p>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
              {getTopicsByModuleName(module.name).length === 0 && (
                <p className="text-muted">Темы отсутствуют</p>
              )}
              <button className="btn btn-success mt-3" onClick={() => handleAddTopic(module.id)}>
                Добавить тему
              </button>
            </div>
          )}
        </div>
      ))}

      {/* Кнопка добавления модуля */}
      <button
        className="btn btn-success mt-4"
        onClick={() => {
          setNewModule({
            name: "",
            description: "",
            level_id: selectedLevelId || "",
          });
          setCurrentModuleEditId(null);
          setFormError("");
          setSuccess("");
          setShowModuleModal(true);
        }}
      >
        Добавить новый модуль
      </button>

      {/* Модальное окно для добавления/редактирования темы */}
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
            className="needs-validation bg-white p-4 rounded"
            style={{ width: "400px" }}
            onSubmit={(e) => e.preventDefault()}
          >
            <h5>{currentTopicId ? "Редактировать тему" : "Добавить тему"}</h5>
            <div className="mb-3">
              <label htmlFor="topicName" className="form-label">
                Название темы
              </label>
              <input
                type="text"
                id="topicName"
                className="form-control"
                value={newTopic.name}
                onChange={(e) => setNewTopic({ ...newTopic, name: e.target.value })}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="topicDescription" className="form-label">
                Описание
              </label>
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
                type="button"
              >
                Отмена
              </button>
              <button className="btn btn-primary" onClick={saveTopic} type="button">
                Сохранить
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Модальное окно для добавления/редактирования модуля */}
      {showModuleModal && (
        <div
          className="modal"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <form
            className="needs-validation bg-white p-4 rounded"
            style={{ width: "400px" }}
            onSubmit={(e) => e.preventDefault()}
          >
            <h5>{currentModuleEditId ? "Редактировать модуль" : "Добавить модуль"}</h5>
            <div className="mb-3">
              <label htmlFor="moduleName" className="form-label">
                Название модуля
              </label>
              <input
                type="text"
                id="moduleName"
                className="form-control"
                value={newModule.name}
                onChange={(e) => setNewModule({ ...newModule, name: e.target.value })}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="moduleDescription" className="form-label">
                Описание
              </label>
              <textarea
                id="moduleDescription"
                className="form-control"
                value={newModule.description}
                onChange={(e) => setNewModule({ ...newModule, description: e.target.value })}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="moduleLevel" className="form-label">
                Уровень
              </label>
              <select
                id="moduleLevel"
                className="form-control"
                value={newModule.level_id || ""}
                onChange={(e) => setNewModule({ ...newModule, level_id: e.target.value })}
              >
                <option value="">Выберите уровень</option>
                {levels.map((lvl) => (
                  <option key={lvl.id} value={lvl.id}>
                    {lvl.name}
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
                type="button"
              >
                Отмена
              </button>
              <button className="btn btn-primary" onClick={saveModule} type="button">
                Сохранить
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Модальное окно для добавления/редактирования материала */}
      {showMaterialModal && (
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
            className="needs-validation bg-white p-4 rounded"
            style={{ width: "400px" }}
            onSubmit={(e) => e.preventDefault()}
          >
            <h5>{currentMaterial ? "Редактировать материал" : "Добавить материал"}</h5>
            <div className="mb-3">
              <label htmlFor="topic_id" className="form-label">
                Тема
              </label>
              <select
                id="topic_id"
                name="topic_id"
                className="form-select"
                value={newMaterial.topic_id}
                onChange={(e) => setNewMaterial({ ...newMaterial, topic_id: e.target.value })}
                disabled={!!currentMaterial} // Отключаем изменение темы при редактировании
              >
                <option value="">Выберите тему</option>
                {topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-3">
              <label htmlFor="categorymaterials_id" className="form-label">
                Категория
              </label>
              <select
                id="categorymaterials_id"
                name="categorymaterials_id"
                className="form-select"
                value={newMaterial.categorymaterials_id}
                onChange={(e) => setNewMaterial({ ...newMaterial, categorymaterials_id: e.target.value })}
              >
                <option value="">Выберите категорию</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-3">
              <label htmlFor="content" className="form-label">
                Описание
              </label>
              <textarea
                id="content"
                name="content"
                className="form-control"
                value={newMaterial.content}
                onChange={(e) => setNewMaterial({ ...newMaterial, content: e.target.value })}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="file" className="form-label">
                Файл
              </label>
              <input
                type="file"
                id="file"
                name="file"
                className="form-control"
                onChange={(e) => setNewMaterial({ ...newMaterial, file: e.target.files[0] })}
              />
            </div>
            {formError && <div className="alert alert-danger">{formError}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <div className="text-end">
              <button
                className="btn btn-secondary me-2"
                onClick={() => setShowMaterialModal(false)}
                type="button"
              >
                Отмена
              </button>
              <button
                className="btn btn-primary"
                onClick={saveMaterial}
                type="button"
                disabled={!isMaterialFormValid}
              >
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
