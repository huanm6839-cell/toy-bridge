import express from 'express';
import { WebSocketServer } from 'ws';

const app = express();
app.use(express.json());

const SECRET = process.env.BRIDGE_SECRET || '';
const queue = [];
const clients = new Set();

// 内存队列：AI 发指令 → 存这里
app.post('/toy', (req, res) => {
  if (SECRET && req.headers['x-bridge-secret'] !== SECRET) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const cmd = req.body;
  if (cmd && typeof cmd === 'object') {
    queue.push(cmd);
    // 通知所有等待的轮询客户端
    for (const ws of clients) {
      if (ws.readyState === 1) ws.send(JSON.stringify(cmd));
    }
  }
  res.json({ ok: true, queued: queue.length });
});

// 蓝牙中继轮询接口
app.get('/toy-next', (req, res) => {
  if (SECRET && req.headers['x-bridge-secret'] !== SECRET) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const cmd = queue.shift() || { type: 'hello' };
  res.json(cmd);
});

// MCP SSE 端点（Claude 用）
app.get('/mcp', (req, res) => {
  if (SECRET && req.query.secret !== SECRET) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();
  
  const send = (data) => res.write(`data: ${JSON.stringify(data)}\n\n`);
  send({ type: 'hello', tools: [
    { name: 'toy_set_speed', description: '设置强度 0-100%', parameters: { speed: 'number', sec: 'number?' } },
    { name: 'toy_set_pattern', description: '设置振动花样 1-8', parameters: { pattern: 'number', level: 'number?' } },
    { name: 'toy_stop', description: '立即停止', parameters: {} },
    { name: 'toy_status', description: '查询状态', parameters: {} }
  ]});
  
  clients.add(res);
  req.on('close', () => clients.delete(res));
});

// MCP 工具调用
app.post('/mcp/call', express.json(), (req, res) => {
  if (SECRET && req.headers['x-bridge-secret'] !== SECRET) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const { name, params } = req.body;
  let cmd = {};
  if (name === 'toy_set_speed') cmd = { speed: params.speed, sec: params.sec };
  else if (name === 'toy_set_pattern') cmd = { pattern: params.pattern, level: params.level || 0.6 };
  else if (name === 'toy_stop') cmd = { stop: true };
  else if (name === 'toy_status') {
    return res.json({ status: 'online', queue: queue.length });
  }
  queue.push(cmd);
  res.json({ ok: true, cmd });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Bridge on port ${PORT}`));
