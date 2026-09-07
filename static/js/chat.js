/**
 * AI College Assistant - Interactive Chat Engine
 * Handles message streaming, markdown rendering, code block copy,
 * speech recognition, text-to-speech, and responsive mobile navigation.
 */

// DOM Elements
const input = document.getElementById("input");
const chatbox = document.getElementById("chatbox");
const micBtn = document.getElementById("mic");
const typingIndicator = document.getElementById("typingIndicator");
const audioStatusPill = document.getElementById("audioStatusPill");

// SVGs
const BOT_ICON_SVG = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8.01" y2="16"></line><line x1="16" y1="16" x2="16.01" y2="16"></line></svg>`;
const COPY_ICON_SVG = `<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
const CHECK_ICON_SVG = `<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

let isWaitingResponse = false;
let codeBlockCounter = 0;

/**
 * Format current local time (e.g. 10:45 PM)
 */
function getCurrentTimeString() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Send user message to Flask /chat API
 */
async function sendMessage() {
    if (!input || isWaitingResponse) return;
    const message = input.value.trim();
    if (!message) return;

    // Render user bubble
    addUserMessage(message);
    input.value = "";
    input.focus();

    // Show typing wave indicator
    showTypingIndicator(true);
    isWaitingResponse = true;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        showTypingIndicator(false);
        isWaitingResponse = false;

        if (data.reply) {
            addBotMessage(data.reply);
            if (!data.error) {
                speak(data.reply);
            }
        } else {
            addBotMessage("Sorry, I didn't receive a response. Please try again.");
        }
    } catch (error) {
        showTypingIndicator(false);
        isWaitingResponse = false;
        addBotMessage("⚠️ Connection error: Unable to reach the server. (" + error.message + ")");
    }
}

/**
 * Render User message bubble
 */
function addUserMessage(text) {
    const timeStr = getCurrentTimeString();
    const userInitial = window.CURRENT_USER_NAME ? window.CURRENT_USER_NAME.charAt(0).toUpperCase() : 'U';

    const row = document.createElement("div");
    row.className = "message-row user-row";
    row.innerHTML = `
        <div class="msg-avatar">${escapeHTML(userInitial)}</div>
        <div class="msg-bubble">
            <div class="msg-header">
                <span class="msg-sender">You</span>
                <span class="msg-time">${timeStr}</span>
            </div>
            <div class="msg-text">${escapeHTML(text)}</div>
        </div>
    `;

    chatbox.appendChild(row);
    scrollToBottom();
}

/**
 * Render Bot message bubble with Markdown and code blocks
 */
function addBotMessage(rawText) {
    const timeStr = getCurrentTimeString();
    const formattedHtml = renderRichMarkdown(rawText);

    const row = document.createElement("div");
    row.className = "message-row bot-row";
    row.innerHTML = `
        <div class="msg-avatar">${BOT_ICON_SVG}</div>
        <div class="msg-bubble">
            <div class="msg-header">
                <span class="msg-sender">${BOT_ICON_SVG} AI Assistant</span>
                <span class="msg-time">${timeStr}</span>
            </div>
            <div class="msg-text">${formattedHtml}</div>
        </div>
    `;

    chatbox.appendChild(row);
    scrollToBottom();
}

/**
 * Parse & format assistant text into beautiful Markdown & Code Blocks
 */
function renderRichMarkdown(text) {
    if (!text) return "";

    // Normalize line breaks
    let raw = text.replace(/\r\n/g, "\n");

    // 1. Extract and format multi-line code blocks: ```lang ... ``` or ``` ... ```
    raw = raw.replace(/```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```/g, function(match, lang, code) {
        codeBlockCounter++;
        const blockId = `code_block_${codeBlockCounter}`;
        const displayLang = lang.trim() ? lang.trim().toUpperCase() : 'CODE';
        const escapedCode = escapeHTML(code.trim());

        return `
            <div class="code-block-wrapper">
                <div class="code-block-header">
                    <span>${displayLang}</span>
                    <button type="button" class="code-copy-btn" onclick="copyCode(this, '${blockId}')">
                        ${COPY_ICON_SVG} <span>Copy</span>
                    </button>
                </div>
                <pre><code id="${blockId}">${escapedCode}</code></pre>
            </div>
        `;
    });

    // 2. Format inline code `code`
    raw = raw.replace(/`([^`]+)`/g, function(match, code) {
        return `<code class="inline-code">${escapeHTML(code)}</code>`;
    });

    // 3. Format Bold text **text**
    raw = raw.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // 4. Format lines into lists or paragraphs
    const lines = raw.split("\n");
    let result = [];
    let inList = false;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();

        // Check if line is already part of a code block wrapper
        if (line.includes('<div class="code-block-wrapper">') || line.includes('</pre>') || line.includes('</div>')) {
            if (inList) {
                result.push("</ul>");
                inList = false;
            }
            result.push(lines[i]);
            continue;
        }

        // Bullet point lines: •, -, *
        if (/^[•\-\*]\s+(.*)/.test(line)) {
            const content = line.replace(/^[•\-\*]\s+/, '');
            if (!inList) {
                result.push("<ul>");
                inList = true;
            }
            result.push(`<li>${content}</li>`);
        } 
        // Numbered list: 1. , 2.
        else if (/^\d+\.\s+(.*)/.test(line)) {
            const content = line.replace(/^\d+\.\s+/, '');
            if (!inList) {
                result.push("<ul>");
                inList = true;
            }
            result.push(`<li>${content}</li>`);
        } 
        else {
            if (inList) {
                result.push("</ul>");
                inList = false;
            }

            if (line.length === 0) {
                // Empty line acts as paragraph divider
                continue;
            } else {
                result.push(`<p>${line}</p>`);
            }
        }
    }

    if (inList) {
        result.push("</ul>");
    }

    return result.join("\n");
}

/**
 * Copy code snippet to clipboard with visual checkmark
 */
function copyCode(btn, codeId) {
    const codeEl = document.getElementById(codeId);
    if (!codeEl) return;

    const text = codeEl.innerText || codeEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
        const originalContent = btn.innerHTML;
        btn.innerHTML = `${CHECK_ICON_SVG} <span style="color:#10b981">Copied!</span>`;
        setTimeout(() => {
            btn.innerHTML = originalContent;
        }, 2000);
    }).catch(err => {
        console.error("Copy failed:", err);
    });
}

/**
 * Toggle Typing Wave Indicator
 */
function showTypingIndicator(show) {
    if (!typingIndicator) return;
    if (show) {
        typingIndicator.classList.add("active");
    } else {
        typingIndicator.classList.remove("active");
    }
    scrollToBottom();
}

/**
 * Quick question chip click
 */
function quick(question) {
    if (!input) return;
    input.value = question;
    sendMessage();
}

/**
 * Clear chat history
 */
async function clearChat() {
    try {
        await fetch("/clear", { method: "POST" });
    } catch (error) {
        console.warn("Clear chat error:", error);
    }

    // Reset chatbox with initial greeting
    const studentName = window.CURRENT_USER_NAME || "Student";
    chatbox.innerHTML = `
        <div class="message-row bot-row">
            <div class="msg-avatar">${BOT_ICON_SVG}</div>
            <div class="msg-bubble">
                <div class="msg-header">
                    <span class="msg-sender">${BOT_ICON_SVG} AI Assistant</span>
                    <span class="msg-time">${getCurrentTimeString()}</span>
                </div>
                <div class="msg-text">
                    <p>Conversation cleared! 👋 Hello <strong>${escapeHTML(studentName)}</strong>, what would you like to learn or prepare for today?</p>
                </div>
            </div>
        </div>
    `;

    closeMobileDrawer();
    scrollToBottom();
}

/**
 * Voice Input using Web Speech API
 */
function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Voice recognition is best supported in Google Chrome, Edge, and Safari.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    if (micBtn) {
        micBtn.classList.add("is-recording");
        micBtn.setAttribute("title", "Listening...");
    }

    recognition.start();

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        if (input) {
            input.value = transcript;
            sendMessage();
        }
        resetMicState();
    };

    recognition.onerror = function() {
        resetMicState();
    };

    recognition.onend = function() {
        resetMicState();
    };
}

function resetMicState() {
    if (micBtn) {
        micBtn.classList.remove("is-recording");
        micBtn.setAttribute("title", "Voice Input");
    }
}

/**
 * Text-to-speech with stop controls
 */
function speak(text) {
    if (!("speechSynthesis" in window)) return;

    window.speechSynthesis.cancel();

    // Clean text for speech
    const cleanText = text
        .replace(/```[\s\S]*?```/g, "Code block omitted.")
        .replace(/`[^`]+`/g, "")
        .replace(/[*#_•\-]/g, "")
        .replace(/[🤖🐍☕🗄💻📊🌐🎨⚡🧠📝📚🎓🧮✨👋😊●]/g, "")
        .trim();

    if (!cleanText) return;

    const speech = new SpeechSynthesisUtterance(cleanText);
    speech.rate = 0.96;
    speech.pitch = 1.0;

    speech.onstart = function() {
        if (audioStatusPill) {
            audioStatusPill.classList.add("active");
        }
    };

    speech.onend = function() {
        if (audioStatusPill) {
            audioStatusPill.classList.remove("active");
        }
    };

    speech.onerror = function() {
        if (audioStatusPill) {
            audioStatusPill.classList.remove("active");
        }
    };

    window.speechSynthesis.speak(speech);
}

function stopSpeaking() {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
    if (audioStatusPill) {
        audioStatusPill.classList.remove("active");
    }
}

/**
 * Mobile Drawer Toggle
 */
function toggleMobileDrawer() {
    const drawer = document.getElementById("mobileDrawer");
    const overlay = document.getElementById("drawerOverlay");
    if (!drawer || !overlay) return;

    const isOpen = drawer.classList.contains("open");
    if (isOpen) {
        drawer.classList.remove("open");
        overlay.classList.remove("open");
    } else {
        drawer.classList.add("open");
        overlay.classList.add("open");
    }
}

function closeMobileDrawer() {
    const drawer = document.getElementById("mobileDrawer");
    const overlay = document.getElementById("drawerOverlay");
    if (drawer) drawer.classList.remove("open");
    if (overlay) overlay.classList.remove("open");
}

/**
 * Safe HTML escape
 */
function escapeHTML(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Scroll chatbox to bottom smoothly
 */
function scrollToBottom() {
    if (chatbox) {
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    if (input) {
        input.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
    }

    // Format any initial welcome messages in chatbox
    const initialBotMsg = document.querySelector(".bot-row .msg-text");
    if (initialBotMsg && initialBotMsg.dataset.raw) {
        initialBotMsg.innerHTML = renderRichMarkdown(initialBotMsg.dataset.raw);
    }

    scrollToBottom();
});
