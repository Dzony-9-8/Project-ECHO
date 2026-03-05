/**
 * ECHO V4 — Central API Service (frontend/src/services/api.js)
 * Replaces inline fetch() calls scattered across components.
 * All backend communication goes through this module.
 */

const BASE_URL = "http://127.0.0.1:8000";

/**
 * Send a chat message and consume the UACP stream (SSE via POST)
 * @param {object} opts
 * @param {function} onChunk Callback fired when a new JSON fragment arrives
 */
export async function sendChatStream({
    message,
    task_type = "conversation",
    tags = [],
    onChunk
}) {
    const response = await fetch(`${BASE_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_input: message,
            task_type,
            tags
        }),
    });

    if (!response.ok) {
        const err = await response.text();
        throw new Error(err || "API Stream Error");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE logic: split by double newline
        const parts = buffer.split("\n\n");
        buffer = parts.pop(); // keep the trailing unfinished chunk in buffer

        for (const part of parts) {
            if (part.startsWith("data: ")) {
                const dataStr = part.slice(6).trim();
                if (dataStr === "[DONE]") return;

                try {
                    const data = JSON.parse(dataStr);
                    if (onChunk) onChunk(data);
                } catch (e) {
                    console.error("Failed to parse SSE JSON chunk:", dataStr, e);
                }
            }
        }
    }
}

/**
 * Fetch session insights.
 * @param {string} sessionId
 */
export async function fetchInsight(sessionId = "current_session") {
    const response = await fetch(`${BASE_URL}/v1/insights/session/${sessionId}`);
    if (!response.ok) throw new Error("Insight fetch failed");
    return response.json();
}

/**
 * Fetch system health and resource profile.
 */
export async function fetchHealth() {
    const response = await fetch(`${BASE_URL}/health`);
    if (!response.ok) throw new Error("Health check failed");
    return response.json();
}

/**
 * Transcribe audio via the backend mock endpoint.
 * @param {FormData} formData
 */
export async function transcribeAudio(formData) {
    const response = await fetch(`${BASE_URL}/v1/audio/transcriptions`, {
        method: "POST",
        body: formData,
    });
    if (!response.ok) throw new Error("Transcription failed");
    return response.json();
}
