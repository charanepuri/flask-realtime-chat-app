const socket = io();

socket.emit(
    "user_connected",
    {
        username: username
    }
);

let typingTimer;

const sendBtn = document.getElementById("send-btn");

const messageInput =
document.getElementById("message");

messageInput.addEventListener(
    "input",
    () => {

        socket.emit(
            "typing",
            {
                username: username
            }
        );

        clearTimeout(typingTimer);

        typingTimer =
        setTimeout(() => {

            socket.emit(
                "stop_typing"
            );

        }, 1000);
    }
);

const chatBox =
document.getElementById("chat-box");


sendBtn.addEventListener("click", () => {

    const message =
    messageInput.value;

    if(message.trim() === "")
        return;

    socket.emit(
        "send_message",
        {
            username: username,
            message: message,
            room : currentRoom
        }
    );

    messageInput.value = "";

    socket.emit(
        "stop_typing"
    );
});

const joinRoomBtn =
document.getElementById(
    "join-room-btn"
);

let currentRoom = "General";

joinRoomBtn.addEventListener(
    "click",
    () => {

        currentRoom =
        document.getElementById(
            "room-select"
        ).value;

        socket.emit(
            "join_room",
            {
                username: username,
                room: currentRoom
            }
        );
    }
);

socket.on(
    "receive_message",
    (data) => {

        const div =
        document.createElement("div");

        if(data.username === username){

            div.classList.add(
                "message",
                "own-message"
            );

            div.innerHTML =
            `
            <strong>You</strong>
            <br>
            ${data.message}
            `;
        }

        else{

            div.classList.add(
                "message",
                "other-message"
            );

            div.innerHTML =
            `
            <strong>${data.username}</strong>
            <br>
            ${data.message}
            `;
        }

        chatBox.appendChild(div);

        chatBox.scrollTop =
        chatBox.scrollHeight;
    }
);

socket.on(
    "online_users",
    (users) => {

        const onlineList =
        document.getElementById(
            "online-users"
        );

        onlineList.innerHTML = "";

        users.forEach(user => {

            const li =
            document.createElement("li");

            li.classList.add(
                "list-group-item"
            );

            li.innerHTML =
            `
            🟢 <strong>${user}</strong>
            `;

            onlineList.appendChild(li);

        });

    }
);

socket.on(
    "user_joined",
    (data) => {

        const div =
        document.createElement("div");

        div.innerHTML =
        `<p><em>${data.message}</em></p>`;

        chatBox.appendChild(div);

    }
);

socket.on(
    "user_left",
    (data) => {

        const div =
        document.createElement("div");

        div.innerHTML =
        `<p><em>${data.message}</em></p>`;

        chatBox.appendChild(div);

    }
);

socket.on(
    "show_typing",
    (data) => {

        document.getElementById(
            "typing-indicator"
        ).innerHTML =
        `${data.username} is typing...`;
    }
);


socket.on(
    "hide_typing",
    () => {

        document.getElementById(
            "typing-indicator"
        ).innerHTML = "";
    }
);

socket.on(
    "room_notification",
    (data) => {

        const div =
        document.createElement("div");

        div.innerHTML =
        `<p><em>${data.message}</em></p>`;

        chatBox.appendChild(div);
    }
);

