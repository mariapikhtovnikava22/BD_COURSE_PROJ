// TopicItem.jsx

import React, { useState } from "react";

function TopicItem({ topic }) {
  const [expanded, setExpanded] = useState(false);

  const handleToggle = () => setExpanded((prev) => !prev);

  return (
    <div className="card mb-3" style={{ border: "1px solid #ddd", borderRadius: "10px" }}>
      <div
        className="card-header d-flex justify-content-between align-items-center"
        style={{ cursor: "pointer", backgroundColor: "#f8f9fa" }}
        onClick={handleToggle}
      >
        <strong>{topic.name}</strong>
        <span>{expanded ? "▲" : "▼"}</span>
      </div>
      {expanded && (
        <div className="card-body">
          <p>{topic.description}</p>
        </div>
      )}
    </div>
  );
}

export default TopicItem;
