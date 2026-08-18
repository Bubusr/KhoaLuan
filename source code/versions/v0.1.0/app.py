import os
from dotenv import load_dotenv
load_dotenv() # Nạp biến môi trường từ .env

# Đồng bộ LANGFUSE_HOST từ LANGFUSE_BASE_URL nếu có
if os.getenv("LANGFUSE_BASE_URL") and not os.getenv("LANGFUSE_HOST"):
    os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_BASE_URL")

import uuid
from flask import Flask, request, jsonify, render_template_string
from langfuse import propagate_attributes
from src.retrieval.hybrid import HybridRetriever

from src.parser.clinical_parser import ClinicalParser
from src.reranking.ontology_reranker import OntologyReranker
from src.generation.clinical_generator import ClinicalGenerator
from src.pipeline import ClinicalRAGPipeline

app = Flask(__name__)

# Khởi tạo pipeline modular
retriever = HybridRetriever()
retriever.load_corpus("data/corpus/corpus.json")
retriever.build_index()

parser = ClinicalParser()
reranker = OntologyReranker("data/ontology/ontology.json")
generator = ClinicalGenerator()

pipeline = ClinicalRAGPipeline(retriever, parser, reranker, generator)

# Bộ nhớ lưu trữ lịch sử chat phía Backend trong phiên chạy (in-memory)
CHAT_SESSIONS = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ontology-Guided RAG Clinical Sandbox</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0c10;
            --bg-card: rgba(22, 28, 38, 0.6);
            --border-glow: rgba(0, 242, 254, 0.15);
            --accent-cyan: #00f2fe;
            --accent-purple: #4facfe;
            --accent-orange: #ff9f43;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --danger: #ef4444;
            --success: #10b981;
            --warning: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background: radial-gradient(circle at 50% 50%, #111827 0%, #030712 100%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            padding: 20px 40px;
            background: rgba(10, 12, 16, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }

        header h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .badge {
            padding: 4px 12px;
            border-radius: 20px;
            background: rgba(0, 242, 254, 0.1);
            border: 1px solid rgba(0, 242, 254, 0.2);
            color: var(--accent-cyan);
            font-size: 0.8rem;
            font-weight: 600;
        }

        .decision-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
        }

        .decision-badge.answer {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--success);
            color: var(--success);
        }

        .decision-badge.abstain {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid var(--warning);
            color: var(--warning);
        }

        .decision-badge.escalate {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid var(--danger);
            color: var(--danger);
        }

        .sandbox-container {
            display: flex;
            flex-direction: column;
            padding: 30px;
            gap: 30px;
            max-width: 1700px;
            width: 100%;
            margin: 0 auto;
        }

        @media (min-width: 1024px) {
            .sandbox-container {
                flex-direction: row;
            }
        }

        /* Sidebar for Multiple Chats */
        .sidebar {
            flex: 0.3;
            background: rgba(15, 22, 33, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            height: calc(100vh - 160px);
        }

        .new-chat-btn {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border: none;
            border-radius: 12px;
            padding: 12px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s ease;
        }

        .new-chat-btn:hover {
            opacity: 0.9;
            transform: scale(1.02);
        }

        .session-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            overflow-y: auto;
            flex: 1;
        }

        .session-item {
            padding: 12px 15px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            cursor: pointer;
            font-size: 0.9rem;
            color: var(--text-muted);
            transition: all 0.2s ease;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .session-item:hover, .session-item.active {
            background: rgba(0, 242, 254, 0.05);
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
        }

        /* Left side: Chat & Input */
        .chat-panel {
            flex: 1.2;
            display: flex;
            flex-direction: column;
            background: var(--bg-card);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            height: calc(100vh - 160px);
        }

        .chat-history {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .welcome-card {
            text-align: center;
            padding: 40px 20px;
            max-width: 500px;
            margin: auto;
        }

        .welcome-card h2 {
            font-size: 1.8rem;
            margin-bottom: 12px;
            color: var(--text-main);
        }

        .welcome-card p {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 24px;
            line-height: 1.5;
        }

        .suggestions {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .suggestion-btn {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 12px 16px;
            color: var(--text-main);
            text-align: left;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.9rem;
        }

        .suggestion-btn:hover {
            background: rgba(0, 242, 254, 0.05);
            border-color: rgba(0, 242, 254, 0.3);
            transform: translateX(4px);
        }

        .chat-bubble {
            max-width: 85%;
            padding: 16px 20px;
            border-radius: 16px;
            line-height: 1.6;
            font-size: 0.95rem;
        }

        .chat-bubble.user {
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.15), rgba(0, 242, 254, 0.15));
            border: 1px solid rgba(0, 242, 254, 0.2);
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .mode-selector {
            display: flex;
            gap: 8px;
            padding: 10px 20px 0;
            align-items: center;
        }

        .mode-selector-label {
            font-size: 0.78rem;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }

        .mode-btn {
            padding: 5px 14px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.03);
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .mode-btn:hover {
            border-color: rgba(0, 242, 254, 0.4);
            color: var(--accent-cyan);
        }

        .mode-btn.active-l0 {
            background: rgba(156, 163, 175, 0.15);
            border-color: var(--text-muted);
            color: #fff;
        }

        .mode-btn.active-l1 {
            background: rgba(255, 159, 67, 0.15);
            border-color: var(--accent-orange);
            color: var(--accent-orange);
        }

        .mode-btn.active-l2 {
            background: rgba(0, 242, 254, 0.1);
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
        }

        .chat-input-area {
            padding: 12px 20px 20px;
            background: rgba(10, 12, 16, 0.6);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .chat-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 16px 20px;
            color: var(--text-main);
            font-family: inherit;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }

        .chat-input:focus {
            border-color: var(--accent-cyan);
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
        }

        .send-btn {
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border: none;
            border-radius: 16px;
            padding: 16px 24px;
            color: #000;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .send-btn:hover {
            opacity: 0.9;
            transform: scale(1.02);
        }

        /* Right side: Comparators & Ontology Inspector */
        .inspector-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
            height: calc(100vh - 160px);
            overflow-y: auto;
        }

        .card {
            background: var(--bg-card);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(20px);
        }

        .card-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 8px;
        }

        .comparison-grid {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .compare-box {
            border-radius: 12px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .compare-box.level0 {
            border-left: 4px solid var(--text-muted);
        }

        .compare-box.level1 {
            border-left: 4px solid var(--accent-orange);
            background: rgba(255, 159, 67, 0.02);
        }

        .compare-box.level2 {
            border-left: 4px solid var(--accent-cyan);
            background: rgba(0, 242, 254, 0.02);
        }

        .compare-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.85rem;
            font-weight: bold;
            align-items: center;
        }

        .compare-text {
            font-size: 0.9rem;
            line-height: 1.5;
            color: #d1d5db;
        }

        .json-viewer {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 12px;
            font-family: monospace;
            font-size: 0.8rem;
            color: #38bdf8;
            overflow-x: auto;
            white-space: pre-wrap;
        }

        .tag-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 5px;
        }

        .d-tag {
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>

    <header>
        <div>
            <h1>Ontology-Guided RAG</h1>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">Clinical Decision Support Sandbox</div>
        </div>
        <span class="badge" id="session-badge">Session: Initializing...</span>
    </header>

    <div class="sandbox-container">
        <!-- Sidebar: Chat List -->
        <div class="sidebar">
            <button class="new-chat-btn" onclick="startNewChat()">+ New Chat Thread</button>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 10px; font-weight: bold;">CHAT SESSIONS (In-memory)</div>
            <div class="session-list" id="session-list"></div>
        </div>

        <!-- Left: Chat Sandbox -->
        <div class="chat-panel">
            <div class="chat-history" id="chat-history">
                <!-- Welcome card will be injected by JS after load -->
            </div>

            <div class="mode-selector">
                <span class="mode-selector-label">Chat Mode:</span>
                <button class="mode-btn active-l0" id="mode-l0" onclick="setMode('l0')">L0 — Vanilla</button>
                <button class="mode-btn" id="mode-l1" onclick="setMode('l1')">L1 — Concept Filter</button>
                <button class="mode-btn" id="mode-l2" onclick="setMode('l2')">L2 — Ontology</button>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="query-input" placeholder="Type custom medical queries..." onkeypress="handleKey(event)">
                <button class="send-btn" onclick="submitQuery()">Send Query</button>
            </div>
        </div>

        <!-- Right: Diagnostic comparison -->
        <div class="inspector-panel" id="inspector-panel" style="display: none;">
            <!-- Comparison -->
            <div class="card">
                <div class="card-title">Retrieval Comparison (L0 vs L1 vs L2)</div>
                <div class="comparison-grid">
                    <!-- Level 0 -->
                    <div class="compare-box level0">
                        <div class="compare-header">
                            <span>LEVEL 0 — VANILLA HYBRID RAG (Dense + BM25)</span>
                            <span id="l0-decision" class="decision-badge"></span>
                        </div>
                        <div class="compare-text" style="font-weight: 600; color: #fff; margin-bottom: 4px;" id="l0-retrieved"></div>
                        <div class="compare-text" id="l0-answer"></div>
                    </div>

                    <!-- Level 1 -->
                    <div class="compare-box level1">
                        <div class="compare-header">
                            <span>LEVEL 1 — CONCEPT-FILTERED RAG (Entity Boost)</span>
                            <span id="l1-decision" class="decision-badge"></span>
                        </div>
                        <div class="compare-text" style="font-weight: 600; color: #fff; margin-bottom: 4px;" id="l1-retrieved"></div>
                        <div class="compare-text" id="l1-answer"></div>
                    </div>

                    <!-- Level 2 -->
                    <div class="compare-box level2">
                        <div class="compare-header">
                            <span>LEVEL 2 — ONTOLOGY-GUIDED RAG (Rerank + Restrict)</span>
                            <span id="l2-decision" class="decision-badge"></span>
                        </div>
                        <div class="compare-text" style="font-weight: 600; color: #fff; margin-bottom: 4px;" id="l2-retrieved"></div>
                        <div class="compare-text" id="l2-answer"></div>
                    </div>
                </div>
            </div>

            <!-- Parsed Metadata -->
            <div class="card">
                <div class="card-title">Clinical Context Extracted (Used by L1 & L2)</div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 10px;">
                    * Level 1 uses disease & anatomy concepts.<br>
                    * Level 2 uses the full structured profile (state, intents, anatomy).<br>
                    * <em>Context Link: Nếu bạn đặt câu hỏi tiếp theo cùng một Thread, bối cảnh y khoa cũ sẽ được tự động kế thừa.</em>
                </div>
                <div class="json-viewer" id="json-metadata"></div>
            </div>

            <!-- Ontology Scoring details -->
            <div class="card">
                <div class="card-title">Level 2 Ontology Reranking Diagnostics</div>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 10px;">
                    💡 <em>Xếp hạng lại (Reranking) diễn ra trong quá trình tìm kiếm (Retrieval), không phải fine-tuning mô hình.</em>
                </div>
                <div id="diagnostics-list"></div>
            </div>
        </div>
    </div>

    <script>
        const samples = {
            1: "I have osteoporosis. What exercises should I perform to stay active?",
            2: "I have osteoporosis and had a vertebral fracture 2 weeks ago. What exercises should I perform to stay active?",
            3: "I have osteoporosis. What medications are recommended to improve my condition?"
        };

        let currentSessionId = "";
        let chatSessions = {};
        let activeMode = "l0"; // Default chat mode: l0, l1, l2

        const modeLabelMap = {
            "l0": "Vanilla RAG (Level 0)",
            "l1": "Concept-Filtered RAG (Level 1)",
            "l2": "Ontology-Guided RAG (Level 2)"
        };

        const modeColorMap = {
            "l0": "var(--text-muted)",
            "l1": "var(--accent-orange)",
            "l2": "var(--accent-cyan)"
        };

        function setMode(mode) {
            activeMode = mode;
            ["l0", "l1", "l2"].forEach(m => {
                const btn = document.getElementById("mode-" + m);
                btn.className = "mode-btn";
                if (m === mode) btn.classList.add("active-" + m);
            });
        }

        function buildWelcomeCard() {
            const welcome = document.createElement("div");
            welcome.className = "welcome-card";
            welcome.id = "welcome-card";

            const h2 = document.createElement("h2");
            h2.textContent = "Select a clinical query below to test 3 levels of RAG:";
            welcome.appendChild(h2);

            const p = document.createElement("p");
            p.textContent = "Compare how Level 0 (Vanilla), Level 1 (Concept Filters), and Level 2 (Ontology) handle patient profiles and safety constraints.";
            welcome.appendChild(p);

            const suggestions = document.createElement("div");
            suggestions.className = "suggestions";

            const tcSamples = [
                { id: 1, label: "TC001 (General Osteoporosis)", text: '"I have osteoporosis. What exercises should I perform to stay active?"' },
                { id: 2, label: "TC002 (Acute Vertebral Fracture)", text: '"I have osteoporosis and had a vertebral fracture 2 weeks ago. What exercises should I perform to stay active?"' },
                { id: 3, label: "TC003 (Medication Intent)", text: '"I have osteoporosis. What medications are recommended to improve my condition?"' }
            ];

            tcSamples.forEach(tc => {
                const btn = document.createElement("button");
                btn.className = "suggestion-btn";
                btn.innerHTML = `<strong>${tc.label}:</strong> ${tc.text}`;
                btn.addEventListener("click", () => sendSample(tc.id));
                suggestions.appendChild(btn);
            });

            welcome.appendChild(suggestions);
            return welcome;
        }

        function sendSample(id) {
            document.getElementById("query-input").value = samples[id];
            submitQuery();
        }

        function handleKey(e) {
            if (e.key === "Enter") {
                submitQuery();
            }
        }

        function setDecisionBadge(elementId, decision) {
            const badge = document.getElementById(elementId);
            if (!badge) return;
            badge.innerText = decision || "N/A";
            badge.className = "decision-badge " + (decision ? decision.toLowerCase() : "abstain");
        }

        function initChatList() {
            const list = document.getElementById("session-list");
            list.innerHTML = "";
            
            Object.keys(chatSessions).forEach(sid => {
                const item = document.createElement("div");
                item.className = "session-item" + (sid === currentSessionId ? " active" : "");
                item.innerText = chatSessions[sid].name;
                item.onclick = () => switchSession(sid);
                list.appendChild(item);
            });
            document.getElementById("session-badge").innerText = "Session: " + currentSessionId.substring(0, 8) + "...";
        }

        function switchSession(sid) {
            currentSessionId = sid;
            initChatList();
            
            const chatHistory = document.getElementById("chat-history");
            chatHistory.innerHTML = "";
            
            const msgs = chatSessions[sid].messages;
            if (msgs.length === 0) {
                chatHistory.appendChild(buildWelcomeCard());
                document.getElementById("inspector-panel").style.display = "none";
            } else {
                msgs.forEach(msg => {
                    const bubble = document.createElement("div");
                    bubble.className = "chat-bubble " + msg.role;
                    if (msg.role === "user") {
                        bubble.innerText = msg.content;
                    } else {
                        bubble.style.background = "rgba(255, 255, 255, 0.02)";
                        bubble.style.border = "1px solid rgba(255, 255, 255, 0.05)";
                        bubble.style.alignSelf = "flex-start";
                        bubble.style.borderBottomLeftRadius = "4px";
                        bubble.innerHTML = `<div style="font-weight: 600; color: var(--accent-cyan); margin-bottom: 6px;">Response:</div>` + msg.content.replace(/\\n/g, "<br>");
                    }
                    chatHistory.appendChild(bubble);
                });
                chatHistory.scrollTop = chatHistory.scrollHeight;
                
                if (chatSessions[sid].last_diag) {
                    showDiagnostics(chatSessions[sid].last_diag);
                } else {
                    document.getElementById("inspector-panel").style.display = "none";
                }
            }
        }

        async function startNewChat() {
            const response = await fetch("/api/session/new", { method: "POST" });
            const data = await response.json();
            const sid = data.session_id;
            
            chatSessions[sid] = {
                name: "Thread " + sid.substring(0, 5),
                messages: [],
                last_diag: null
            };
            
            switchSession(sid);
        }

        function showDiagnostics(data) {
            document.getElementById("inspector-panel").style.display = "flex";
            
            const l0_chunk = data.l0_chunk || { id: "N/A", title: "No chunk" };
            const l1_chunk = data.l1_chunk || { id: "N/A", title: "No chunk" };
            const l2_chunk = data.l2_chunk || { id: "N/A", title: "No chunk" };

            // Compare responses
            document.getElementById("l0-retrieved").innerText = "Retrieved Chunk: " + l0_chunk.id + " (" + l0_chunk.title + ")";
            document.getElementById("l0-answer").innerText = data.l0_answer || "No response";
            setDecisionBadge("l0-decision", data.l0_decision);

            document.getElementById("l1-retrieved").innerText = "Retrieved Chunk: " + l1_chunk.id + " (" + l1_chunk.title + ")";
            document.getElementById("l1-answer").innerText = data.l1_answer || "No response";
            setDecisionBadge("l1-decision", data.l1_decision);

            document.getElementById("l2-retrieved").innerText = "Retrieved Chunk: " + l2_chunk.id + " (" + l2_chunk.title + ")";
            document.getElementById("l2-answer").innerText = data.l2_answer || "No response";
            setDecisionBadge("l2-decision", data.l2_decision);

            // Fill metadata
            document.getElementById("json-metadata").innerText = JSON.stringify(data.parsed_query, null, 2);

            // Build diagnostics list
            const diagList = document.getElementById("diagnostics-list");
            diagList.innerHTML = "";
            if (data.candidates && data.candidates.length > 0) {
                data.candidates.forEach(cand => {
                    const c = cand.chunk || { id: "N/A", title: "Unknown", concepts: [] };
                    const item = document.createElement("div");
                    item.style.marginBottom = "12px";
                    item.style.fontSize = "0.85rem";
                    item.style.background = "rgba(255, 255, 255, 0.01)";
                    item.style.padding = "10px";
                    item.style.borderRadius = "8px";
                    item.style.border = "1px solid rgba(255, 255, 255, 0.03)";
                    
                    let penaltyHtml = cand.penalty > 0 
                        ? `<span style="color: var(--danger); font-weight: bold; margin-left: 8px;">Penalty: -${cand.penalty}</span>` 
                        : "";
                    let boostHtml = cand.boost > 0 
                        ? `<span style="color: var(--success); font-weight: bold; margin-left: 8px;">Boost: +${cand.boost}</span>` 
                        : "";

                    item.innerHTML = `
                        <div style="font-weight: 600; display: flex; justify-content: space-between;">
                            <span>[${c.id}] ${c.title}</span>
                            <span>Score: ${cand.score ? cand.score.toFixed(4) : "0.0000"}</span>
                        </div>
                        <div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 2px;">
                            Semantic Score: ${cand.semantic_score ? cand.semantic_score.toFixed(4) : "0.0000"} ${boostHtml} ${penaltyHtml}
                        </div>
                        <div class="tag-list">
                            ${c.concepts ? c.concepts.map(con => `<span class="d-tag">${con}</span>`).join("") : ""}
                        </div>
                    `;
                    diagList.appendChild(item);
                });
            } else {
                diagList.innerHTML = `<div style="color: var(--text-muted); font-size: 0.9rem;">No diagnostics available for this query.</div>`;
            }
        }

        async function submitQuery() {
            const input = document.getElementById("query-input");
            const query = input.value.trim();
            if (!query) return;

            // Clear welcome card
            const welcome = document.getElementById("welcome-card");
            if (welcome) welcome.style.display = "none";

            // Add user bubble
            const chatHistory = document.getElementById("chat-history");
            const userBubble = document.createElement("div");
            userBubble.className = "chat-bubble user";
            userBubble.innerText = query;
            chatHistory.appendChild(userBubble);
            chatHistory.scrollTop = chatHistory.scrollHeight;

            input.value = "";

            // Push to local memory
            chatSessions[currentSessionId].messages.push({
                role: "user",
                content: query
            });

            // Call API
            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ 
                        query: query,
                        session_id: currentSessionId
                    })
                });
                
                if (!response.ok) {
                    throw new Error("HTTP error " + response.status);
                }
                
                const data = await response.json();

                // Pick answer based on active mode
                const answerKey = activeMode + "_answer";
                const activeAnswer = data[answerKey] || data.l2_answer;
                const activeDecision = data[activeMode + "_decision"] || data.l2_decision;
                const modeLabel = modeLabelMap[activeMode];
                const modeColor = modeColorMap[activeMode];

                // Add system response bubble
                const systemBubble = document.createElement("div");
                systemBubble.className = "chat-bubble assistant";
                systemBubble.style.background = "rgba(255, 255, 255, 0.02)";
                systemBubble.style.border = "1px solid rgba(255, 255, 255, 0.05)";
                systemBubble.style.alignSelf = "flex-start";
                systemBubble.style.borderBottomLeftRadius = "4px";

                systemBubble.innerHTML = `<div style="font-weight: 600; color: ${modeColor}; margin-bottom: 6px;">${modeLabel} response:</div>` + activeAnswer.replace(/\\n/g, "<br>");
                chatHistory.appendChild(systemBubble);
                chatHistory.scrollTop = chatHistory.scrollHeight;

                // Save to local memory (always save L2 as canonical history for context)
                chatSessions[currentSessionId].messages.push({
                    role: "assistant",
                    content: data.l2_answer
                });
                chatSessions[currentSessionId].last_diag = data;

                // Switch UI title name based on first query
                if (chatSessions[currentSessionId].name.startsWith("Thread")) {
                    chatSessions[currentSessionId].name = query.substring(0, 15) + "...";
                    initChatList();
                }

                showDiagnostics(data);

            } catch (e) {
                console.error("API Call failed", e);
                const systemBubble = document.createElement("div");
                systemBubble.className = "chat-bubble assistant";
                systemBubble.style.background = "rgba(239, 68, 68, 0.1)";
                systemBubble.style.border = "1px solid var(--danger)";
                systemBubble.style.color = "var(--danger)";
                systemBubble.style.alignSelf = "flex-start";
                systemBubble.style.borderBottomLeftRadius = "4px";
                systemBubble.innerText = "Error: Failed to process query. The server might have encountered an exception or you entered an unresolvable medical context.";
                chatHistory.appendChild(systemBubble);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
        }

        // Auto-run first chat session creation on load
        window.onload = async () => {
            await startNewChat();
        };
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/session/new", methods=["POST"])
def create_session():
    session_id = str(uuid.uuid4())
    CHAT_SESSIONS[session_id] = []
    return jsonify({"session_id": session_id})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    query_text = data.get("query", "")
    session_id = data.get("session_id", "")
    
    if not query_text:
        return jsonify({"error": "Empty query"}), 400

    # 1. Quản lý hội thoại và Kế thừa ngữ cảnh (Context Carry-over / Resolution)
    history = CHAT_SESSIONS.get(session_id, [])
    
    with propagate_attributes(session_id=session_id):
        # Phân tích cú pháp câu hiện tại
        current_parsed = parser.parse(query_text)
        
        # Cơ chế kế thừa: Nếu câu hỏi hiện tại thiếu thông tin cốt lõi (disease, anatomy),
        # và có câu hỏi trước đó trong phiên chat, kế thừa từ bối cảnh trước đó.
        if not current_parsed.disease and history:
            # Tìm câu hỏi y khoa trước đó trong lịch sử
            for past_msg in reversed(history):
                if past_msg["role"] == "user" and past_msg.get("parsed"):
                    past_parsed = past_msg["parsed"]
                    if past_parsed.disease:
                        current_parsed.disease = past_parsed.disease
                        current_parsed.anatomy = list(set(current_parsed.anatomy + past_parsed.anatomy))
                        # Nếu câu hiện tại không khai báo clinical_state, kế thừa luôn trạng thái lâm sàng
                        if not current_parsed.clinical_state.phase:
                            current_parsed.clinical_state.phase = past_parsed.clinical_state.phase
                        break

        # 2. Chạy RAG qua Pipeline với bối cảnh đã giải quyết
        l0_res = pipeline.run_level_0(query_text, k=3, history=history)
        
        # Override Level 1 & 2 với cấu trúc query đã kế thừa ngữ cảnh
        all_candidates = retriever.search(query_text, k=len(retriever.chunks), alpha=0.5)
        
        # Tái tạo Level 1
        reranked_l1 = []
        for cand in all_candidates:
            chunk = cand["chunk"]
            semantic_score = cand["score"]
            boost = 0.0
            for d in current_parsed.disease:
                if d in chunk.concepts: boost += 0.4
            for a in current_parsed.anatomy:
                if a in chunk.concepts: boost += 0.3
            reranked_l1.append({
                "chunk": chunk,
                "score": semantic_score + boost,
                "semantic_score": semantic_score,
                "boost": boost,
                "penalty": 0.0
            })
        reranked_l1 = sorted(reranked_l1, key=lambda x: x["score"], reverse=True)
        l1_top = reranked_l1[:3]
        l1_answer, l1_decision = generator.generate_answer(query_text, l1_top, current_parsed, history=history)
        
        # Tái tạo Level 2
        reranked_l2 = reranker.rerank(all_candidates, current_parsed)
        l2_top = reranked_l2[:3]
        l2_answer, l2_decision = generator.generate_answer(query_text, l2_top, current_parsed, history=history)

    # Cập nhật lịch sử chat phía backend
    if session_id in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id].append({
            "role": "user",
            "content": query_text,
            "parsed": current_parsed
        })
        CHAT_SESSIONS[session_id].append({
            "role": "assistant",
            "content": l2_answer
        })


    # Đóng gói an toàn để tránh crash khi l0_top_cand hoặc l1_top hoặc l2_top trống (None)
    l0_top_cand = l0_res.get("top_candidate")
    l0_chunk_data = l0_top_cand["chunk"].model_dump() if (l0_top_cand and l0_top_cand.get("chunk")) else {"id": "N/A", "title": "No Chunk Retrieved", "text": "", "concepts": []}

    l1_chunk_data = l1_top[0]["chunk"].model_dump() if l1_top else {"id": "N/A", "title": "No Chunk Retrieved", "text": "", "concepts": []}
    l2_chunk_data = l2_top[0]["chunk"].model_dump() if l2_top else {"id": "N/A", "title": "No Chunk Retrieved", "text": "", "concepts": []}

    # Trả về kết quả
    return jsonify({
        "l0_chunk": l0_chunk_data,
        "l0_answer": l0_res["answer"],
        "l0_decision": l0_res["decision"],
        "l1_chunk": l1_chunk_data,
        "l1_answer": l1_answer,
        "l1_decision": l1_decision,
        "l2_chunk": l2_chunk_data,
        "l2_answer": l2_answer,
        "l2_decision": l2_decision,
        "parsed_query": current_parsed.model_dump(),
        "candidates": [
            {
                "chunk": cand["chunk"].model_dump() if cand.get("chunk") else {"id": "N/A", "title": "Unknown", "concepts": []},
                "score": cand.get("score", 0.0),
                "semantic_score": cand.get("semantic_score", 0.0),
                "boost": cand.get("boost", 0.0),
                "penalty": cand.get("penalty", 0.0)
            }
            for cand in reranked_l2
        ]
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
