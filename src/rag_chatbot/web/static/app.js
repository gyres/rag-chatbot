const uploadForm = document.querySelector("#upload-form");
const fileInput = document.querySelector("#file-input");
const statusBox = document.querySelector("#status");

const chatWindow = document.querySelector("#chat-window");
const messageForm = document.querySelector("#message-form");
const messageInput = document.querySelector("#message-input");

const resetButtons = document.querySelectorAll("[data-reset]");


function setStatus(message, isError = false) {
    statusBox.textContent = message;
    statusBox.classList.toggle("error", isError);
}


function getErrorMessage(data, fallbackMessage) {
    if (typeof data?.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data?.detail)) {
        return data.detail.map((item) => item.msg).join(" ");
    }

    return fallbackMessage;
}


function escapeHtml(text) {
    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatAssistantText(text) {
    const escapedText = escapeHtml(text);
    const lines = escapedText.split("\n");

    const htmlParts = [];
    let isInsideList = false;

    for (const line of lines) {
        const bulletMatch = line.match(/^\s*[-*]\s+(.+)/);

        if (bulletMatch) {
            if (!isInsideList) {
                htmlParts.push("<ul>");
                isInsideList = true;
            }

            htmlParts.push(`<li>${bulletMatch[1]}</li>`);
            continue;
        }

        if (isInsideList) {
            htmlParts.push("</ul>");
            isInsideList = false;
        }

        if (line.trim() === "") {
            htmlParts.push("<br>");
        } else {
            htmlParts.push(`<p>${line}</p>`);
        }
    }

    if (isInsideList) {
        htmlParts.push("</ul>");
    }

    return htmlParts
        .join("")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`(.+?)`/g, "<code>$1</code>");
}


function addMessage(role, text) {
    const message = document.createElement("div");
    message.classList.add("message", role);

    const label = document.createElement("strong");
    label.textContent = role === "user" ? "You" : role === "system" ? "System" : "Assistant";

    const content = document.createElement("div");
    content.classList.add("message-content");

    if (role === "assistant") {
        content.classList.add("formatted");
        content.innerHTML = formatAssistantText(text);
    } else {
        content.textContent = text;
    }

    message.appendChild(label);
    message.appendChild(content);
    chatWindow.appendChild(message);

    chatWindow.scrollTop = chatWindow.scrollHeight;
}


uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        setStatus("Please choose a PDF or TXT file first.", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Uploading and processing document...");

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(getErrorMessage(data, "Document upload failed."));
        }

        setStatus(data.message);
        addMessage("system", `Uploaded: ${data.filename}`);

    } catch (error) {
        setStatus(error.message, true);
    }
});


messageForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage("user", message);
    messageInput.value = "";
    messageInput.disabled = true;

    try {
        const response = await fetch("/message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(getErrorMessage(data, "Message request failed."));
        }

        addMessage("assistant", data.response);

    } catch (error) {
        addMessage("system", error.message);

    } finally {
        messageInput.disabled = false;
        messageInput.focus();
    }
});


resetButtons.forEach((button) => {
    button.addEventListener("click", async () => {
        const endpoint = button.dataset.reset;

        try {
            const response = await fetch(endpoint, {
                method: "POST",
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(getErrorMessage(data, "Reset request failed."));
            }

            setStatus(data.message);
            addMessage("system", data.message);

        } catch (error) {
            setStatus(error.message, true);
        }
    });
});