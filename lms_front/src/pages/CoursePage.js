// src/User/pages/UserTestPage.jsx
import React, { useState, useEffect } from "react";
import { userService } from "../api";

const UserTestPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [test, setTest] = useState([]);
  const [modules, setModules] = useState([]);
  const [answers, setAnswers] = useState({});
  const [testCompleted, setTestCompleted] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await userService.getEntranceTestOrModules();
        setStatus(response.status);
        if (response.status === "test") {
          setTest(response.test);
        } else if (response.status === "modules") {
          setModules(response.modules);
        }
      } catch (err) {
        setError("Ошибка загрузки данных");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAnswerChange = (questionId, optionId) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionId,
    }));
  };

  const handleSubmitTest = async () => {
    try {
      // Преобразуем объект ответов в массив
      const formattedAnswers = Object.entries(answers).map(([questionId, optionId]) => ({
        question_id: parseInt(questionId, 10),
        selected_option_id: optionId,
      }));
  
      console.log("Отправляем ответы:", formattedAnswers);
  
      const response = await userService.submitEntranceTest({ answers: formattedAnswers });
      setTestCompleted(true);
      alert(`Ваш результат: ${response.score}%`);
    } catch (err) {
      console.error("Ошибка отправки теста:", err);
      setError(err || "Не удалось отправить тест.");
    }
  };

  if (loading) return <p>Загрузка...</p>;
  if (error) return <div className="alert alert-danger">{error}</div>;

  return (
    <div className="container my-4">
      <h2>Добро пожаловать!</h2>

      {status === "test" && !testCompleted && (
        <div>
          <h3>Вступительный тест</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmitTest();
            }}
          >
            {test.map((question) => (
              <div key={question.question_id} className="mb-4">
                <h5>{question.question_name}</h5>
                <ul className="list-group">
                  {question.options.map((option) => (
                    <li
                      key={option.option_id}
                      className="list-group-item d-flex align-items-center"
                    >
                      <input
                        type="radio"
                        name={`question-${question.question_id}`}
                        value={option.option_id}
                        checked={answers[question.question_id] === option.option_id}
                        onChange={() =>
                          handleAnswerChange(question.question_id, option.option_id)
                        }
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
        </div>
      )}

      {status === "modules" && (
        <div>
          <h3>Доступные модули</h3>
          <ul className="list-group">
            {modules.map((module) => (
              <li key={module.id} className="list-group-item">
                <h5>{module.name}</h5>
                <p>{module.description}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {testCompleted && (
        <div className="alert alert-success mt-4">
          Тест завершён! Вы можете начать изучение курсов.
        </div>
      )}
    </div>
  );
};

export default UserTestPage;
