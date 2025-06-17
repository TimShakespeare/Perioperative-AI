import React, { useState } from 'react';
import './index.css';

const commonQuestions = [
  "术前饮食注意事项有哪些？",
  "术后多久可以下床活动？",
  "麻醉前要做哪些准备？",
  "术后多久可以正常进食？",
  "复查需要注意什么？"
];

function App() {
  const [chatHistory, setChatHistory] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (message) => {
    setChatHistory([...chatHistory, { sender: "user", text: message }]);
    setLoading(true);
    const res = await fetch('http://你的天翼云后端API地址/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message})
    });
    const data = await res.json();
    setChatHistory(prev => [...prev, { sender: "ai", text: data.reply }]);
    setLoading(false);
  };

  const handleClickQuestion = (q) => handleSend(q);

  const handleSubmit = () => {
    if (!userInput.trim()) return;
    handleSend(userInput);
    setUserInput('');
  };

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      <h1 className="text-3xl font-bold">围术期管理 AI</h1>
      <div className="grid grid-cols-2 gap-2">
        {commonQuestions.map((q, idx) => (
          <button key={idx} className="bg-blue-500 text-white p-2 rounded" onClick={() => handleClickQuestion(q)}>{q}</button>
        ))}
      </div>

      <div className="h-80 overflow-y-scroll border p-2">
        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`my-2 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
            <span>{msg.sender === "user" ? "🧑" : "🤖"} {msg.text}</span>
          </div>
        ))}
        {loading && <div>AI 正在思考...</div>}
      </div>

      <div className="flex gap-2">
        <input className="border p-2 flex-1" value={userInput} onChange={e => setUserInput(e.target.value)} placeholder="请输入您的问题" />
        <button className="bg-green-500 text-white p-2 rounded" onClick={handleSubmit}>发送</button>
      </div>
    </div>
  );
}

export default App;
