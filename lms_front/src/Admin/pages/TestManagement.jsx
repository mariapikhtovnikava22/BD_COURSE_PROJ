// src/Admin/pages/TestManagement.jsx

import React, { useState, useEffect, useCallback } from "react";
import {
  AdminModulesService,
  AdminTestService,
  AdminTestQuestionService,
  AdminTopicsService,
  AdminOptionService,
  AdminQuestionOptionService,
  AdminQuestionService,
} from "../../api";

const TestManagement = () => {
  // Состояния для модулей, тестов, тем и вопросов
  const [modules, setModules] = useState([]);
  const [tests, setTests] = useState([]);
  const [topics, setTopics] = useState([]);

  // Состояния для управления раскрытием тестов и хранения вопросов
  const [expandedTestIds, setExpandedTestIds] = useState([]);
  const [questionsByTest, setQuestionsByTest] = useState({});

  // Состояния для тестового модального окна
  const [showTestModal, setShowTestModal] = useState(false);
  const [newTest, setNewTest] = useState({ name: "", description: "", module_id: "" });
  const [currentTestId, setCurrentTestId] = useState(null);

  // Состояния для вопросного модального окна
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [currentTestForQuestion, setCurrentTestForQuestion] = useState(null);
  const [newQuestion, setNewQuestion] = useState({ question_text: "", topic_id: "" });
  const [options, setOptions] = useState([]);
  const [currentOption, setCurrentOption] = useState({ option_text: "", is_correct: false });
  const [correctAnswerId, setCorrectAnswerId] = useState(null);

  // Дополнительные состояния для редактирования вопроса
  const [isEditingQuestion, setIsEditingQuestion] = useState(false);
  const [editingQuestionId, setEditingQuestionId] = useState(null);

  // Состояния для загрузки и ошибок
  const [loading, setLoading] = useState(true);
  const [loadingQuestions, setLoadingQuestions] = useState({});
  const [error, setError] = useState("");

  // Состояния для ошибок/успехов форм
  const [formError, setFormError] = useState("");
  const [success, setSuccess] = useState("");

  // Загружаем модули, тесты и темы при монтировании
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [modulesData, testsData, topicsData] = await Promise.all([
          AdminModulesService.getAllModules(),
          AdminTestService.getAllTests(),
          AdminTopicsService.getAllTopics(),
        ]);
        setModules(modulesData);
        setTests(testsData);
        setTopics(topicsData);
      } catch (err) {
        setError("Ошибка загрузки данных");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Открытие формы редактирования теста
  const handleEditTest = useCallback((test) => {
    setCurrentTestId(test.id);
    setNewTest({
      name: test.name,
      description: test.description,
      module_id: test.module_id,
    });
    setFormError("");
    setSuccess("");
    setShowTestModal(true);
  }, []);

  // Удаление теста
  const handleDeleteTest = useCallback(async (testId) => {
    if (window.confirm("Вы уверены, что хотите удалить тест?")) {
      try {
        await AdminTestService.deleteTest(testId);
        setTests((prevTests) => prevTests.filter((t) => t.id !== testId));
        setSuccess("Тест успешно удален!");
        setTimeout(() => setSuccess(""), 2000);
      } catch (error) {
        console.error("Ошибка при удалении теста:", error);
        setFormError("Не удалось удалить тест");
      }
    }
  }, []);

  // Раскрытие/сворачивание списка вопросов
  const handleToggleExpandTest = useCallback(
    (testId) => {
      setExpandedTestIds((prev) =>
        prev.includes(testId)
          ? prev.filter((id) => id !== testId)
          : [...prev, testId]
      );
      if (!questionsByTest[testId]) {
        fetchQuestionsForTest(testId);
      }
    },
    [questionsByTest]
  );

  // Загрузка вопросов для теста
  const fetchQuestionsForTest = useCallback(async (testId) => {
    setLoadingQuestions((prev) => ({ ...prev, [testId]: true }));
    try {
      const data = await AdminTestQuestionService.getAllTestQuestions(testId);
      const questionsArray = Array.isArray(data) ? data : [data];
      setQuestionsByTest((prev) => ({
        ...prev,
        [testId]: questionsArray,
      }));
    } catch (err) {
      console.error("Ошибка загрузки вопросов:", err);
      setFormError("Ошибка загрузки вопросов");
    } finally {
      setLoadingQuestions((prev) => ({ ...prev, [testId]: false }));
    }
  }, []);

  // Открыть форму добавления нового вопроса (или редактирования)
  const handleAddQuestion = useCallback((testId) => {
    // Для "создания" вопроса:
    setIsEditingQuestion(false);
    setEditingQuestionId(null);

    setCurrentTestForQuestion(testId);
    setNewQuestion({ question_text: "", topic_id: "" });
    setOptions([]);
    setCorrectAnswerId(null);
    setFormError("");
    setSuccess("");
    setShowQuestionModal(true);
  }, []);

  // Открыть форму редактирования уже существующего вопроса
  const handleEditQuestion = useCallback(
    (testId, question) => {
      setIsEditingQuestion(true);
      setEditingQuestionId(question.id);

      setCurrentTestForQuestion(testId);
      setNewQuestion({
        question_text: question.name || "",
        topic_id: question.topic_id || "",
      });
      setOptions(question.options || []);
      // Найдём, какой вариант правильный
      const correctOpt = question.options.find((opt) => opt.is_correct);
      setCorrectAnswerId(correctOpt ? correctOpt.id : null);

      setFormError("");
      setSuccess("");
      setShowQuestionModal(true);
    },
    []
  );

  // Добавление нового варианта ответа
  const handleAddOption = useCallback(async () => {
    if (!currentOption.option_text.trim()) {
      setFormError("Текст варианта ответа обязателен.");
      return;
    }
    if (options.length >= 5) {
      setFormError("Нельзя добавить больше 5 вариантов.");
      return;
    }
    if (currentOption.is_correct && options.some((opt) => opt.is_correct)) {
      setFormError("Правильный ответ уже выбран.");
      return;
    }
    if (!currentTestForQuestion) {
      setFormError("Не выбран тест для добавления вопроса.");
      return;
    }

    try {
      // Создаём вариант в БД
      const savedOption = await AdminOptionService.createOption({
        value: currentOption.option_text,
      });

      let newOptions = [
        ...options,
        { ...savedOption, is_correct: currentOption.is_correct },
      ];

      if (currentOption.is_correct) {
        // Сбрасываем правильность остальных
        newOptions = newOptions.map((opt) => ({
          ...opt,
          is_correct: opt.id === savedOption.id,
        }));
        setCorrectAnswerId(savedOption.id);
      }

      setOptions(newOptions);
      setCurrentOption({ option_text: "", is_correct: false });
      setFormError("");
    } catch (error) {
      console.error("Ошибка при сохранении варианта ответа:", error);
      setFormError("Не удалось сохранить вариант ответа.");
    }
  }, [currentOption, options, currentTestForQuestion]);

  const handleDeleteOption = useCallback(
    async (index) => {
      const toDelete = options[index];
      if (!toDelete) return;
  
      // Если удаляемый вариант был правильным, сбрасываем correctAnswerId
      if (toDelete.is_correct) {
        setCorrectAnswerId(null);
      }
  
      try {
        // 1. Удаляем связь вопрос-опция в QuestionOptions (если нужна).
        //    Предположим, у вас AdminQuestionOptionService.deleteQuestionOptionByOptionId(...)
        //    или как-то иначе.


        const allLinks = await AdminQuestionOptionService.getAllQuestionOptions();
        const link = allLinks.find(
          (l) => l.option_id === toDelete.id && l.question_id === editingQuestionId
        );
        if (link) {
          await AdminQuestionOptionService.deleteQuestionOption(link.id);
        }
  
        // 2. Удаляем сам вариант ответа из Optionss
        await AdminOptionService.deleteOption(toDelete.id);
  
        // 3. Убираем вариант из локального массива
        const updated = options.filter((_, i) => i !== index);
        setOptions(updated);
        setFormError("");
        console.log(`Вариант ответа ID ${toDelete.id} удалён из БД и локального состояния.`);
      } catch (error) {
        console.error("Ошибка при удалении варианта ответа из БД:", error);
        setFormError("Не удалось удалить вариант ответа из базы.");
      }
    },
    [options, editingQuestionId]
  );

  // Логика сохранения вопроса (создание или редактирование)
  const saveQuestion = useCallback(async () => {
    if (!newQuestion.question_text.trim() || !newQuestion.topic_id) {
      setFormError("Текст вопроса и тема обязательны");
      return;
    }
    if (options.length === 0) {
      setFormError("Добавьте хотя бы один вариант ответа");
      return;
    }
    const correct = options.filter((o) => o.is_correct);
    if (correct.length !== 1) {
      setFormError("Должен быть выбран ровно один правильный вариант ответа.");
      return;
    }

    try {
      if (!isEditingQuestion) {
        // СОЗДАНИЕ вопроса
        const createdQuestion = await AdminQuestionService.createQuestion({
          name: newQuestion.question_text,
          correct_answer_id: correctAnswerId,
          topic_id: newQuestion.topic_id,
        });

        // Связываем вопрос с тестом
        await AdminTestQuestionService.linkTestToQuestion({
          test_id: currentTestForQuestion,
          question_id: createdQuestion.id,
        });

        // Связываем варианты ответа
        await Promise.all(
          options.map((option) =>
            AdminQuestionOptionService.linkQuestionToOption({
              question_id: createdQuestion.id,
              option_id: option.id,
            })
          )
        );

        // Обновляем стейт
        setQuestionsByTest((prev) => ({
          ...prev,
          [currentTestForQuestion]: [
            ...(prev[currentTestForQuestion] || []),
            { ...createdQuestion, options },
          ],
        }));
        setSuccess("Вопрос успешно добавлен!");
      } else {
        // РЕДАКТИРОВАНИЕ вопроса
        // 1. Обновляем сам вопрос
        const updatedQuestion = await AdminQuestionService.updateQuestion(editingQuestionId, {
          name: newQuestion.question_text,
          correct_answer_id: correctAnswerId,
          topic_id: newQuestion.topic_id,
        });

        console.log("Ответ сервера при update:", updatedQuestion);

        // 2. Варианты уже «есть» в БД — но мы могли поменять is_correct
        //    Нужно заново отразить логику is_correct в БД, если оно там хранится.
        //    Однако, в текущей архитектуре "правильный" ответ хранится
        //    в поле correct_answer_id вопроса, а не в Options.
        //    Так что обновлять Options не нужно, если текст остался тем же.

        // 3. Обновляем состояние локально
 

          
          // Обновляем состояние локально
          setQuestionsByTest((prev) => {
            const updatedQuestions = (prev[currentTestForQuestion] || []).map((q) => {
              if (q.id === editingQuestionId) {
                console.log('Обновляем вопрос с ID:', editingQuestionId);
                return {
                  ...q,
                  ...updatedQuestion, // Используем объект, возвращённый сервером
                  options: options, // Но оставляем локальные варианты ответа
                };
              }
              return q;
            });
          
            return {
              ...prev,
              [currentTestForQuestion]: updatedQuestions,
            };
          });
        setSuccess("Вопрос успешно обновлён!");
      }

      // Сброс формы
      setNewQuestion({ question_text: "", topic_id: "" });
      setOptions([]);
      setCorrectAnswerId(null);
      setIsEditingQuestion(false);
      setEditingQuestionId(null);
      setCurrentTestForQuestion(null);
      setShowQuestionModal(false);
      setFormError("");
      setTimeout(() => setSuccess(""), 2000);
    } catch (error) {
      console.error("Ошибка при сохранении вопроса:", error);
      setFormError("Не удалось сохранить вопрос");
    }
  }, [
    newQuestion,
    options,
    correctAnswerId,
    isEditingQuestion,
    editingQuestionId,
    currentTestForQuestion,
  ]);

  // Удаление вопроса
  const handleDeleteQuestion = useCallback(async (testId, questionId, questionName) => {
    if (window.confirm("Вы уверены, что хотите удалить вопрос?")) {
      try {
        console.log(testId, questionId, questionName);
  
        // 1. Получаем все связи вопроса с вариантами
        const allLinks = await AdminQuestionOptionService.getAllQuestionOptions();
        console.log("Линки получил", allLinks);
  
        // Фильтруем линки, где `question_name` совпадает с переданным именем
        const questionLinks = allLinks.filter((l) => l.question_name === questionName);
        console.log("Связанные линки для вопроса:", questionLinks);

        // Удаляем все найденные связи
        await Promise.all(
          questionLinks.map((link) => AdminQuestionOptionService.deleteQuestionOption(link.id))
        );
  
        // 2. Удаляем связь тест-вопрос
        const testQuestionLinks = await AdminTestQuestionService.getAllTestQuestions(testId);
        console.log("Связи тест-вопрос получены", testQuestionLinks);
  
        // Фильтруем связь по `testId` и `questionName`
        const link = testQuestionLinks.find(
          (l) => l.name === questionName
        );
        if (link) {
            console.log(link.link_id);
          await AdminTestQuestionService.deleteTestQuestion(link.link_id);
        }
  
        // 3. Удаляем сам вопрос (по имени вместо ID)
        const allQuestions = await AdminQuestionService.getAllQuestions(); // Предполагается, что есть такой метод
        const question = allQuestions.find((q) => q.name === questionName);
        if (question) {
          await AdminQuestionService.deleteQuestion(question.id);
        } else {
          console.error("Вопрос не найден в базе");
          alert("Вопрос не найден в базе.");
          return;
        }
  
        // 4. Обновляем локальный стейт
        setQuestionsByTest((prev) => ({
          ...prev,
          [testId]: prev[testId].filter((q) => q.id !== question.id),
        }));
  
        alert("Вопрос успешно удален!");
      } catch (error) {
        console.error("Ошибка при удалении вопроса:", error);
        alert("Не удалось удалить вопрос");
      }
    }
  }, []);
  

  // Сохранение теста (создание/редактирование)
  const saveTest = useCallback(async () => {
    if (!newTest.name.trim() || !newTest.module_id) {
      setFormError("Название теста и модуль обязательны");
      return;
    }
    try {
      if (currentTestId) {
        // Редактирование
        const updated = await AdminTestService.updateTest(currentTestId, newTest);
        setTests((prev) =>
          prev.map((t) => (t.id === currentTestId ? updated : t))
        );
        setSuccess("Тест успешно обновлен!");
      } else {
        // Создание
        const created = await AdminTestService.createTest(newTest);
        setTests((prev) => [...prev, created]);
        setSuccess("Тест успешно создан!");
      }
      setTimeout(() => {
        setShowTestModal(false);
        setSuccess("");
      }, 2000);
    } catch (err) {
      console.error(err);
      setFormError(err || "Не удалось сохранить тест");
    }
  }, [newTest, currentTestId]);


  const filteredTopics = React.useMemo(() => {
    if (!currentTestForQuestion) return [];
  
    // Находим сам тест
    const testObj = tests.find((t) => t.id === currentTestForQuestion);
    if (!testObj) return [];
  
    // Находим модуль, которому принадлежит этот тест
    const moduleObj = modules.find((m) => m.id === testObj.module_id);
  
    // Если название модуля "вступительный" или модуль не найден, выводим все темы
    if (moduleObj.name.toLowerCase() === "вступительный") {
      return topics; // Возвращаем все темы
    }
  
    // Фильтруем темы, относящиеся к модулю
    return topics.filter((topic) => topic.module_name === moduleObj.name);
  }, [currentTestForQuestion, tests, topics, modules]);

  return (
    <>
      <h2 className="my-4">Управление тестами</h2>

      {loading && <p>Загрузка...</p>}
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div>
        {tests.map((test) => {
          // Найдём название модуля (опционально, если нужно отобразить в самом тесте)
          const moduleName =
            modules.find((m) => m.id === test.module_id)?.name || "Неизвестно";

          return (
            <div key={test.id} className="test mb-4">
              <div className="d-flex justify-content-between align-items-center p-3 bg-light rounded">
                <div>
                  <h5 className="mb-0">{test.name}</h5>
                  {test.description && (
                    <small className="text-muted d-block">{test.description}</small>
                  )}
                  {/* Выводим модуль теста, если нужно */}
                  <small className="text-muted d-block">Модуль: {moduleName}</small>
                </div>
                <div>
                  <button
                    className="btn btn-sm me-2"
                    onClick={() => handleEditTest(test)}
                    title="Редактировать"
                  >
                    ✏️
                  </button>
                  <button
                    className="btn btn-sm me-2"
                    onClick={() => handleDeleteTest(test.id)}
                    title="Удалить"
                  >
                    🗑️
                  </button>
                  <button
                    className="btn btn-sm"
                    onClick={() => handleToggleExpandTest(test.id)}
                    title={expandedTestIds.includes(test.id) ? "Свернуть" : "Развернуть"}
                  >
                    {expandedTestIds.includes(test.id) ? "🔼" : "🔽"}
                  </button>
                </div>
              </div>

              {expandedTestIds.includes(test.id) && (
                <div className="mt-3">
                  <h5>Вопросы:</h5>
                  {loadingQuestions[test.id] ? (
                    <p>Загрузка вопросов...</p>
                  ) : questionsByTest[test.id] && questionsByTest[test.id].length > 0 ? (
                    <>
                      {questionsByTest[test.id].map((question) => (
                        <div
                          key={question.id}
                          style={{
                            backgroundColor: "#fff",
                            border: "1px solid #eee",
                            marginBottom: "0.5rem",
                            padding: "0.75rem",
                            borderRadius: "5px",
                          }}
                        >
                          <div className="d-flex justify-content-between">
                            <div>
                              <strong>{question.name}</strong>
                              <br />
                              <small>
                                Тема:{" "}
                                {topics.find((t) => t.id === question.topic_id)?.name ||
                                  "Неизвестно"}
                              </small>
                            </div>
                            <div>
                              <button
                                className="btn btn-sm me-2"
                                style={{ border: "none", background: "transparent" }}
                                title="Редактировать вопрос"
                                onClick={() => handleEditQuestion(test.id, question)}
                              >
                                ✏️
                              </button>
                              <button
                                className="btn btn-sm"
                                style={{ border: "none", background: "transparent" }}
                                title="Удалить вопрос"
                                onClick={() => handleDeleteQuestion(test.id, question.id, question.name)}
                              >
                                🗑️
                              </button>
                            </div>
                          </div>

                          <ul className="list-group mt-1">
                            {question.options.map((option, index) => (
                              <li
                                key={option.id}
                                className="list-group-item d-flex justify-content-between align-items-center"
                              >
                                <span>
                                  {index + 1}. {option.value}
                                </span>
                                {option.is_correct && (
                                  <span className="badge bg-success">Правильный</span>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </>
                  ) : (
                    <div>В этом тесте пока нет вопросов</div>
                  )}
                  <button
                    className="btn btn-success mt-3"
                    onClick={() => handleAddQuestion(test.id)}
                  >
                    Добавить вопрос
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <button
        className="btn btn-success mt-4"
        onClick={() => {
          setNewTest({ name: "", description: "", module_id: "" });
          setCurrentTestId(null);
          setFormError("");
          setSuccess("");
          setShowTestModal(true);
        }}
      >
        Добавить новый тест
      </button>

      {/* Модалка для добавления/редактирования теста */}
      {showTestModal && (
        <div
          className="modal show"
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
          <div
            className="modal-dialog"
            style={{ maxWidth: "500px", width: "100%" }}
          >
            <div className="modal-content">
              <form className="needs-validation" onSubmit={(e) => e.preventDefault()}>
                <div className="modal-header">
                  <h5 className="modal-title">
                    {currentTestId ? "Редактировать тест" : "Добавить тест"}
                  </h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setShowTestModal(false)}
                  ></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label htmlFor="testName" className="form-label">
                      Название теста
                    </label>
                    <input
                      type="text"
                      id="testName"
                      className="form-control"
                      value={newTest.name}
                      onChange={(e) => setNewTest({ ...newTest, name: e.target.value })}
                    />
                  </div>
                  <div className="mb-3">
                    <label htmlFor="testDescription" className="form-label">
                      Описание
                    </label>
                    <textarea
                      id="testDescription"
                      className="form-control"
                      value={newTest.description}
                      onChange={(e) => setNewTest({ ...newTest, description: e.target.value })}
                    />
                  </div>
                  <div className="mb-3">
                    <label htmlFor="testModule" className="form-label">
                      Модуль
                    </label>
                    <select
                      id="testModule"
                      className="form-select"
                      value={newTest.module_id}
                      onChange={(e) => setNewTest({ ...newTest, module_id: e.target.value })}
                    >
                      <option value="">Выберите модуль</option>
                      {modules.map((module) => (
                        <option key={module.id} value={module.id}>
                          {module.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {formError && <div className="alert alert-danger">{formError}</div>}
                  {success && <div className="alert alert-success">{success}</div>}
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowTestModal(false)}
                  >
                    Отмена
                  </button>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={saveTest}
                  >
                    Сохранить
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Модалка для добавления/редактирования вопроса */}
      {showQuestionModal && (
        <div
          className="modal show"
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
          <div
            className="modal-dialog"
            style={{ maxWidth: "600px", width: "100%" }}
          >
            <div className="modal-content">
              <form className="needs-validation" onSubmit={(e) => e.preventDefault()}>
                <div className="modal-header">
                  <h5 className="modal-title">
                    {isEditingQuestion ? "Редактировать вопрос" : "Добавить новый вопрос"}
                  </h5>
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => {
                      setShowQuestionModal(false);
                      setCurrentTestForQuestion(null);
                      setIsEditingQuestion(false);
                      setEditingQuestionId(null);
                      setFormError("");
                      setSuccess("");
                      setNewQuestion({ question_text: "", topic_id: "" });
                      setOptions([]);
                      setCorrectAnswerId(null);
                    }}
                  ></button>
                </div>
                <div className="modal-body">
                  <div className="mb-3">
                    <label htmlFor="questionText" className="form-label">
                      Текст вопроса
                    </label>
                    <input
                      type="text"
                      id="questionText"
                      className="form-control"
                      value={newQuestion.question_text}
                      onChange={(e) =>
                        setNewQuestion({ ...newQuestion, question_text: e.target.value })
                      }
                    />
                  </div>

                  <div className="mb-3">
                    <label htmlFor="topic" className="form-label">
                      Тема (только из модуля теста)
                    </label>
                    <select
                      id="topic"
                      className="form-select"
                      value={newQuestion.topic_id}
                      onChange={(e) =>
                        setNewQuestion({ ...newQuestion, topic_id: e.target.value })
                      }
                    >
                      <option value="">Выберите тему</option>
                      {/** Показываем только те темы, которые относятся к модулю теста */}
                      {filteredTopics.map((topic) => (
                        <option key={topic.id} value={topic.id}>
                          {topic.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="mb-3">
                    <h6>Варианты ответа:</h6>
                    {options.map((option, index) => (
                      <div key={option.id} className="d-flex align-items-center mb-2">
                        <input
                          type="text"
                          className="form-control me-2"
                          placeholder="Текст варианта"
                          value={option.value}
                          onChange={(e) => {
                            const updatedOptions = [...options];
                            updatedOptions[index].value = e.target.value;
                            setOptions(updatedOptions);
                          }}
                        />
                        <div className="form-check me-2">
                          <input
                            type="radio"
                            name="correctOption"
                            className="form-check-input"
                            checked={option.is_correct}
                            onChange={() => {
                              const updatedOptions = options.map((opt) => ({
                                ...opt,
                                is_correct: opt.id === option.id,
                              }));
                              setOptions(updatedOptions);
                              setCorrectAnswerId(option.id);
                            }}
                          />
                          <label className="form-check-label">Правильный</label>
                        </div>
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDeleteOption(index)}
                        >
                          &times;
                        </button>
                      </div>
                    ))}

                    {/* Добавление нового варианта ответа */}
                    <div className="d-flex align-items-center mb-2">
                      <input
                        type="text"
                        className="form-control me-2"
                        placeholder="Текст варианта"
                        value={currentOption.option_text}
                        onChange={(e) =>
                          setCurrentOption({
                            ...currentOption,
                            option_text: e.target.value,
                          })
                        }
                      />
                      <div className="form-check me-2">
                        <input
                          type="radio"
                          name="correctOptionNew"
                          className="form-check-input"
                          checked={currentOption.is_correct}
                          onChange={() =>
                            setCurrentOption({ ...currentOption, is_correct: true })
                          }
                        />
                        <label className="form-check-label">Правильный</label>
                      </div>
                      <button
                        type="button"
                        className="btn btn-primary btn-sm"
                        onClick={handleAddOption}
                        disabled={options.length >= 5}
                      >
                        Добавить вариант
                      </button>
                    </div>
                    {options.length >= 5 && (
                      <small className="text-muted">Максимум 5 вариантов.</small>
                    )}
                  </div>

                  {formError && <div className="alert alert-danger">{formError}</div>}
                  {success && <div className="alert alert-success">{success}</div>}
                </div>
                <div className="modal-footer">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setShowQuestionModal(false);
                      setCurrentTestForQuestion(null);
                      setIsEditingQuestion(false);
                      setEditingQuestionId(null);
                      setFormError("");
                      setSuccess("");
                      setNewQuestion({ question_text: "", topic_id: "" });
                      setOptions([]);
                      setCorrectAnswerId(null);
                    }}
                  >
                    Отмена
                  </button>
                  <button type="button" className="btn btn-primary" onClick={saveQuestion}>
                    {isEditingQuestion ? "Сохранить изменения" : "Сохранить вопрос"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TestManagement;
