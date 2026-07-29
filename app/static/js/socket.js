console.log("socket.js loaded");
const socket = io();

socket.on("connect", () => {
    console.log("Connected:", socket.id);
});

// Helper function to update sidebar message count in real-time on any page
function updateSidebarBadge(incrementBy) {
    const badges = document.querySelectorAll(".user-nav-badge, .msg-unread-badge, .owner-nav-badge");
    badges.forEach(badge => {
        let count = parseInt(badge.innerText.trim()) || 0;
        count += incrementBy;
        badge.innerText = count;
        if (count > 0) {
            badge.classList.remove("d-none");
            badge.style.display = "inline-block";
        } else {
            badge.classList.add("d-none");
            badge.style.display = "none";
        }
    });
}

function joinChat(otherUser) {
    socket.emit("join_chat", {
        other_user: otherUser
    });
}

function sendMessage(receiver, property, message) {
    socket.emit("send_message", {
        receiver_id: receiver,
        property_id: property,
        message: message
    });
}

socket.on("joined_room", (data) => {
    console.log("Joined room:", data.room);
});

socket.on("new_message", (msg) => {
    const chat = document.getElementById("chat-box");
    if (!chat) return;

    if (typeof CURRENT_USER_ID === "undefined" || typeof currentReceiver === "undefined") return;

    const other = String(msg.sender_id) === String(CURRENT_USER_ID) ? msg.receiver_id : msg.sender_id;

    if (Number(other) !== Number(currentReceiver)) return;

    const mine = String(msg.sender_id) === String(CURRENT_USER_ID);

    chat.innerHTML += `
    <div class="d-flex mb-3 ${mine ? "justify-content-end" : "justify-content-start"}">
        <div class="px-3 py-2 rounded-4 shadow-sm"
             style="
             max-width:70%;
             background:${mine ? "#0d6efd" : "white"};
             color:${mine ? "white" : "#212529"};
             ">
            ${msg.message}
            <div class="small mt-1 text-end opacity-75">
                just now
            </div>
        </div>
    </div>
    `;

    chat.scrollTop = chat.scrollHeight;
});