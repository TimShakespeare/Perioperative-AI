import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import axios from 'axios';

const app = express();
app.use(cors());
app.use(bodyParser.json());

const PORT = 3001;

app.post('/chat', async (req, res) => {
  const { message } = req.body;

  const apiKey = "key";

  try {
    const response = await axios.post('https://api.openai.com/v1/chat/completions', {
      model: "ft:gpt-4o-2024-08-06:personal:liver:BjRU8n0t",  // <-- your fine-tuned model name
      messages: [
        { role: "system", content: "你是一个专业的围术期管理AI助手，专门解答患者在术前、术中、术后的常见问题，请用简单清晰的语言帮助患者。" },
        { role: "user", content: message }
      ],
      temperature: 0.5,
    }, {
      headers: { Authorization: `Bearer ${apiKey}` }
    });

    res.json({ reply: response.data.choices[0].message.content });
  } catch (error) {
    console.error(error.response ? error.response.data : error.message);
    res.status(500).json({ reply: "AI 暂时无法回答，请联系医生。" });
  }
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
