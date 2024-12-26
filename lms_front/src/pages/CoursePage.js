// src/User/pages/UserTestPage.jsx

import React, { useState, useEffect } from "react";
import { userService } from "../api"; 
import Header from "../components/Header";
import Footer from "../components/Footer";

const UserTestPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState("");
  const [formError, setFormError] = useState("");
  const [success, setSuccess] = useState("");

  // Отображаем либо "test" (вступительный тест), либо "modules" (список модулей)
  const [status, setStatus] = useState("");

  // ===== Вступительный тест =====
  const [test, setTest] = useState([]);         // Список вопросов
  const [answers, setAnswers] = useState({});   // { [questionId]: optionId }
  const [testCompleted, setTestCompleted] = useState(false);
  const [level, setLevel] = useState(null);     // Для отображения названия уровня (если нужно)

  // ===== Модули =====
  const [modules, setModules] = useState([]);   // [{id, name, description, topics: [...], moduleTest: {...}?}, ...]
  const [expandedModuleIds, setExpandedModuleIds] = useState([]); 
  // Ответы на тесты конкретных модулей:
  // В формате { [moduleId]: { [questionId]: selectedOptionId }, ... }
  const [moduleAnswers, setModuleAnswers] = useState({});

  // --------------------------------------------------------------------
  // 1) Загрузка первоначальных данных при монтировании
  // --------------------------------------------------------------------
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Узнаём у сервера, нужно ли пройти вступительный тест (status="test"),
        // или уже можно загрузить список модулей (status="modules")
        const response = await userService.getEntranceTestOrModules();
        setStatus(response.status);

        if (response.status === "test") {
          // Нужно пройти вступительный тест
          setTest(response.test);
        } else if (response.status === "modules") {
          // Вступительный тест уже пройден => подгружаем модули
          const userModulesResponse = await userService.getUserModules();
          setModules(userModulesResponse.modules || []);
        }
      } catch (err) {
        console.error("Ошибка загрузки данных:", err);
        setError("Ошибка загрузки данных. Попробуйте позже.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // --------------------------------------------------------------------
  // 2) Логика вступительного теста
  // --------------------------------------------------------------------
  // Изменение ответа в "answers"
  const handleAnswerChange = (questionId, optionId) => {
    setAnswers((prev) => ({ ...prev, [questionId]: optionId }));
  };

  // Отправка вступительного теста
  const handleSubmitTest = async () => {
    setFormError("");
    setSuccess("");

    try {
      // Преобразуем объект answers => массив { question_id, selected_option_id }
      const formattedAnswers = Object.entries(answers).map(([qId, optId]) => ({
        question_id: parseInt(qId, 10),
        selected_option_id: optId,
      }));

      if (formattedAnswers.length === 0) {
        setFormError("Вы должны ответить хотя бы на один вопрос перед отправкой.");
        return;
      }

      // Отправляем результат
      const response = await userService.submitEntranceTest({ answers: formattedAnswers });
      setTestCompleted(true);
      setLevel(response.level || null);
      setSuccess("Вступительный тест успешно завершён!");

      // Подгружаем модули (после успешной отправки)
      const userModulesResponse = await userService.getUserModules();
      setModules(userModulesResponse.modules || []);

      // Через 2 секунды переключаемся на status="modules"
      setTimeout(() => {
        setStatus("modules");
      }, 2000);
    } catch (err) {
      console.error("Ошибка отправки вступительного теста:", err);
      setFormError(err.message || "Не удалось отправить тест. Попробуйте снова.");
    }
  };

  // --------------------------------------------------------------------
  // 3) Логика раскрытия модулей + загрузка/прохождение теста модуля
  // --------------------------------------------------------------------
  // Раскрытие / свёртывание модуля
  const handleToggleExpandModule = (moduleId) => {
    setExpandedModuleIds((prev) =>
      prev.includes(moduleId)
        ? prev.filter((id) => id !== moduleId)
        : [...prev, moduleId]
    );
  };

  // Загрузка теста для модуля
  const handleLoadModuleTest = async (moduleId) => {
    try {
      const moduleTestData = await userService.getModuleTest(moduleId);
      // Добавляем test в объект нужного модуля
      setModules((prevModules) =>
        prevModules.map((mod) =>
          mod.id === moduleId ? { ...mod, moduleTest: moduleTestData } : mod
        )
      );
    } catch (err) {
      console.error("Ошибка при загрузке теста модуля:", err);
      setError("Не удалось загрузить тест модуля. Попробуйте позже.");
    }
  };

  // Выбор ответа в тесте модуля
  const handleModuleTestAnswerChange = (moduleId, questionId, optionId) => {
    setModuleAnswers((prev) => ({
      ...prev,
      [moduleId]: {
        ...(prev[moduleId] || {}),
        [questionId]: optionId,
      },
    }));
  };

  // Отправка теста модуля
  const handleSubmitModuleTest = async (moduleId) => {
    setFormError("");
    setSuccess("");

    const currentModuleAnswers = moduleAnswers[moduleId] || {};
    const formatted = Object.entries(currentModuleAnswers).map(([qId, optId]) => ({
      question_id: parseInt(qId, 10),
      selected_option_id: optId,
    }));

    if (formatted.length === 0) {
      setFormError("Вы должны ответить хотя бы на один вопрос теста модуля.");
      return;
    }

    try {
      console.log(formatted)
      // Отправляем результаты теста модуля
      const response = await userService.SubmitTest(moduleId, { answers: formatted });
      setSuccess(`Тест модуля #${moduleId} успешно завершён!`);

      // При желании удаляем moduleTest, чтобы больше не показывать вопросы
      setModules((prevModules) =>
        prevModules.map((mod) =>
          mod.id === moduleId
            ? { ...mod, moduleTest: null }
            : mod
        )
      );
    } catch (err) {
      console.error("Ошибка при отправке теста модуля:", err);
      setFormError(err.message || "Не удалось отправить тест модуля. Попробуйте снова.");
    }
  };

  // --------------------------------------------------------------------
  // Рендер
  // --------------------------------------------------------------------
  if (loading) return <p>Загрузка...</p>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div className="d-flex flex-column min-vh-100" style={{ backgroundColor: "#F7F3EF" }}>
      <Header />
      <main className="flex-grow-1 p-5">
        {/* Вступительный тест (если нужен) */}
        {status === "test" && !testCompleted && (
          <div>
            <h2 className="mb-4">Пройдите тест для определения уровня знаний!</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSubmitTest();
              }}
            >
              {test.map((question) => (
                <div key={question.question_id} className="card mb-3">
                  <div className="card-header">
                    <h5>{question.question_name}</h5>
                  </div>
                  <ul className="list-group list-group-flush">
                    {question.options.map((option) => (
                      <li key={option.option_id} className="list-group-item">
                        <input
                          type="radio"
                          name={`question-${question.question_id}`}
                          value={option.option_id}
                          checked={answers[question.question_id] === option.option_id}
                          onChange={() => handleAnswerChange(question.question_id, option.option_id)}
                          className="form-check-input me-2"
                        />
                        {option.option_text}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
              <button type="submit" className="btn btn-primary">
                Завершить тест
              </button>
            </form>
            {/* Ошибки / успех для вступительного теста */}
            {formError && <div className="alert alert-danger mt-3">{formError}</div>}
            {success && <div className="alert alert-success mt-3">{success}</div>}
          </div>
        )}

        {/* Если тест завершён, показываем уведомление */}
        {testCompleted && (
          <div className="alert alert-success mt-4">
            <h4>Вступительный тест завершён!</h4>
            <p>Ваш уровень: {level ?? "Неизвестно"}</p>
          </div>
        )}

        {/* Список модулей (status === "modules") */}
        {status === "modules" && (
          <div>
            <h2 className="mb-4">Ваши доступные модули</h2>
            {modules.map((module) => {
              const isExpanded = expandedModuleIds.includes(module.id);
              const moduleTestData = module.moduleTest; // Тест модуля, если мы его загрузили
              const currentModuleAnswers = moduleAnswers[module.id] || {};

              return (
                <div key={module.id} className="card mb-4">
                  <div className="card-header d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">{module.name}</h5>
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => handleToggleExpandModule(module.id)}
                    >
                      {isExpanded ? "Свернуть" : "Развернуть"}
                    </button>
                  </div>

                  <div className="card-body">
                    <p>{module.description}</p>

                    {/* Если модуль "раскрыт" */}
                    {isExpanded && (
                      <div>
                        <h6>Темы:</h6>
                        {module.topics && module.topics.length > 0 ? (
                          module.topics.map((topic) => (
                            <div key={topic.id} className="card mb-3">
                              <div className="card-body">
                                <strong>{topic.name}</strong>
                                <p>{topic.description}</p>
                                {/* Тут можно делать дополнительные вложенные раскрытия, если нужно */}
                              </div>
                            </div>
                          ))
                        ) : (
                          <p>Темы отсутствуют.</p>
                        )}

                        {/* Если тест модуля уже подгружен */}
                        {moduleTestData ? (
                          <div className="mt-3">
                            <h4>{moduleTestData.name}</h4>
                            {moduleTestData.questions.map((q) => (
                              <div key={q.id} className="card mb-3">
                                <div className="card-header">
                                  <strong>{q.name}</strong>
                                  {/* Если нужно, можно вывести q.topic_name */}
                                </div>
                                <ul className="list-group list-group-flush">
                                  {q.options.map((opt) => (
                                    <li key={opt.id} className="list-group-item">
                                      <input
                                        type="radio"
                                        name={`module-${module.id}-question-${q.id}`}
                                        value={opt.id}
                                        checked={currentModuleAnswers[q.id] === opt.id}
                                        onChange={() =>
                                          handleModuleTestAnswerChange(module.id, q.id, opt.id)
                                        }
                                        className="form-check-input me-2"
                                      />
                                      {opt.text}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            ))}

                            <button
                              className="btn btn-success"
                              onClick={() => handleSubmitModuleTest(module.id)}
                            >
                              Завершить тест модуля
                            </button>

                            {/* Ошибки / успех при отправке теста модуля */}
                            {formError && <div className="alert alert-danger mt-3">{formError}</div>}
                            {success && <div className="alert alert-success mt-3">{success}</div>}
                          </div>
                        ) : (
                          <button
                            className="btn btn-primary"
                            onClick={() => handleLoadModuleTest(module.id)}
                          >
                            Загрузить тест модуля
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
};

export default UserTestPage;
