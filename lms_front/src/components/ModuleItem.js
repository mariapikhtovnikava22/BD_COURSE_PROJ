// ModuleItem.jsx

import React, { useState } from "react";
import TopicItem from "./TopicItem"; // Импортируем компонент для темы

function ModuleItem({ module }) {
  const [expanded, setExpanded] = useState(false);

  const handleToggle = () => setExpanded((prev) => !prev);

  return (
    <div className="card mb-4" style={{ border: "1px solid #ccc", borderRadius: "10px" }}>
      <div
        className="card-header d-flex justify-content-between align-items-center"
        style={{ cursor: "pointer", backgroundColor: "#fff" }}
        onClick={handleToggle}
      >
        <h5 className="mb-0">{module.name}</h5>
        <span>{expanded ? "▲" : "▼"}</span>
      </div>
      {expanded && (
        <div className="card-body">
          <p>{module.description}</p>

          {/* Темы модуля */}
          {module.topics && module.topics.length > 0 ? (
            <div>
              <h6>Темы:</h6>
              {module.topics.map((topic) => (
                <TopicItem key={topic.id} topic={topic} />
              ))}
            </div>
          ) : (
            <p>Темы для этого модуля отсутствуют.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default ModuleItem;
