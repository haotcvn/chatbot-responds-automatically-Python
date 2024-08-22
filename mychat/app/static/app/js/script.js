// const fileInput = document.querySelector('#fileInput');
// const fileBtn = document.querySelector('#fileBtn');
// const fileList = document.querySelector('#fileList');

// // const urlInput = document.querySelector('#urlInput');
// // const urlBtn = document.querySelector('#urlBtn');

// let selectedFiles = []

// const fileShow = (file) => {
//     let fileName = file.name;
//     let fileType = file.type.split('/').pop()
//     //let fileType = fileName.split('.').pop()

//     const showFileBoxElem = document.createElement("li");
//     showFileBoxElem.classList.add("showfilebox");

//     const leftElem = document.createElement("div");
//     leftElem.classList.add("left");

//     const fileTypeElem = document.createElement("span");
//     fileTypeElem.classList.add("filetype");
//     fileTypeElem.textContent = fileType;

//     leftElem.appendChild(fileTypeElem);
//     const fileNameElem = document.createElement("h5");
//     fileNameElem.textContent = fileName;
//     leftElem.appendChild(fileNameElem);
//     showFileBoxElem.appendChild(leftElem);

//     const rightElem = document.createElement("div");
//     rightElem.classList.add("right");

//     const crossElem = document.createElement("span");
//     crossElem.innerHTML = "&#215;";
//     rightElem.appendChild(crossElem);

//     showFileBoxElem.appendChild(rightElem);
//     fileList.appendChild(showFileBoxElem);

//     crossElem.addEventListener("click", () => {
//         fileList.removeChild(showFileBoxElem);
//         selectedFiles = selectedFiles.filter(f => f !== file);
//         if (fileList.children.length === 0) {
//             fileBtn.style.display = 'none';
//             clearSessionStatus();
//         }
//     });
// };

// const clearSessionStatus = () => {
//     fetch('/clear_files_status/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         }
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log('Success:', data);
//     })
//     .catch((error) => {
//         console.error('Error:', error);
//     });
// };

// fileInput.addEventListener('change', () => {
//     const files = Array.from(fileInput.files);
//     files.forEach(file => {
//         if (!selectedFiles.some(f => f.name === file.name)) {
//             selectedFiles.push(file)
//             fileShow(file);
//         }
//     });
//     fileBtn.style.display = files.length > 0 ? 'inline-block' : 'none';
// });

// fileBtn.addEventListener('click', async () => {
//     if (selectedFiles.length > 0) {
//         const formData = new FormData();
//         selectedFiles.forEach(file => {
//             formData.append('files', file);
//         });
    
//         try {
//             const response = await fetch("/upload_files/", {
//                 method: "POST",
//                 body: formData,
//                 headers: {
//                     'X-CSRFToken': getCookie('csrftoken')
//                 }
//             });
        
//             if (response.ok) {
//                 alert("Tệp đã được tải lên thành công!");
//             } else {
//                 throw new Error("Đã xảy ra lỗi khi tải lên tệp.");
//             }
//         } catch (error) {
//             console.error("Lỗi:", error.message);
//             alert("Đã xảy ra lỗi khi tải lên tệp.");
//         }
//     }
// });

// urlInput.addEventListener('input', () => {
//     urlBtn.style.display = urlInput.value.length > 0 ? 'inline-block' : 'none';
// })

const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

let userText = null;
let storedAElement = null; // Store the aElement for later use
let isDetailVisible = false; // Flag to track the visibility state

const loadDataFromLocalstorage = () => {
    const themeColor = localStorage.getItem("themeColor");

    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";

    const defaultText = `<div class="default-text">
                            <h1>ChatTCH</h1>
                            <p>Bắt đầu cuộc trò chuyện và khám phá sức mạnh của AI.<br> Lịch sử trò chuyện của bạn sẽ được hiển thị tại đây.</p>
                        </div>`

    chatContainer.innerHTML = localStorage.getItem("all-chats") || defaultText;
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
}

const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
}

const getChatResponse = async (incomingChatDiv, userText) => {
    const pElement = document.createElement("p")
    storedAElement = document.createElement("a"); // Initialize the aElement here
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            question: userText,
        })
    }

    try {
        const response = await (await fetch("/get_answer/", requestOptions)).json();
        if(response.answer) {
            pElement.classList.add("answer")
            pElement.textContent = response.answer.trim();

            if(response.source) {
                storedAElement.textContent = "\n\n* Các câu nguồn *\n\n" + response.source;
                // pElement.appendChild(aElement)
            }
            
        } else {
            pElement.classList.add("answer")
            pElement.textContent = "Không có phản hồi!";
            pElement.style.color = "rgb(233, 80, 80)";
        }
    } catch (error) {
        pElement.classList.add("error");
        pElement.textContent = error.message;
    }

    incomingChatDiv.querySelector(".typing-animation").remove();
    incomingChatDiv.querySelector(".chat-details").appendChild(pElement);
    localStorage.setItem("all-chats", chatContainer.innerHTML);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
}

const handleOutgoingChat = async () => {
    userText = chatInput.value.trim();
    if(!userText) return;

    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="static/app/images/user.png" alt="user-img">
                        <p>${userText}</p>
                    </div>
                </div>`;

    const outgoingChatDiv = createChatElement(html, "outgoing");
    chatContainer.querySelector(".default-text")?.remove();
    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    setTimeout(() => showTypingAnimation(userText), 500);
}

const showTypingAnimation = (userText) => {
    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="static/app/images/chatbot.png" alt="chatbot-img">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                    <div class="funBtn">
                        <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                        <span onclick="detailResponse(this)" class="material-symbols-rounded">info</span>
                    </div>
                </div>`;

    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    getChatResponse(incomingChatDiv, userText);
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const copyResponse = (copyBtn) => {
    const reponseTextElement = copyBtn.parentElement.parentElement.querySelector("p");
    navigator.clipboard.writeText(reponseTextElement.textContent);
    copyBtn.textContent = "done";
    setTimeout(() => copyBtn.textContent = "content_copy", 1000);
}

const detailResponse = (detailBtn) => {
    detailBtn.textContent = isDetailVisible ? "info" : "visibility_off";
    
    const pElement = detailBtn.closest(".chat-content").querySelector("p");

    if (isDetailVisible) {
        pElement.removeChild(storedAElement); // Remove the aElement when hiding
    } else {
        pElement.appendChild(storedAElement); // Append the stored aElement when showing
    }

    isDetailVisible = !isDetailVisible; // Toggle the flag
}

// let isSpeaking = false;
// const speakText = (speakBtn) => {
//     console.log("Nhấn")

// };

deleteButton.addEventListener("click", () => {
    if(confirm("Bạn có chắc chắn muốn xóa tất cả các cuộc trò chuyện không?")) {
        localStorage.removeItem("all-chats");
        loadDataFromLocalstorage();
    }
});

themeButton.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", themeButton.innerText);
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

const initialInputHeight = chatInput.scrollHeight;

chatInput.addEventListener("input", () => {   
    chatInput.style.height =  `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

loadDataFromLocalstorage();
sendButton.addEventListener("click", handleOutgoingChat);

const sidebar = document.querySelector(".sidebar");
const sidebarLockBtn = document.querySelector("#lock-icon");

const toggleLock = () => {
  sidebar.classList.toggle("locked");
  if (!sidebar.classList.contains("locked")) {
    sidebar.classList.add("hoverable");
    sidebarLockBtn.classList.replace("bx-lock-alt", "bx-lock-open-alt");
  } else {
    sidebar.classList.remove("hoverable");
    sidebarLockBtn.classList.replace("bx-lock-open-alt", "bx-lock-alt");
  }
};

const hideSidebar = () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.add("close");
  }
};

const showSidebar = () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.remove("close");
  }
};


if (window.innerWidth < 800) {
  sidebar.classList.add("close");
  sidebar.classList.remove("locked");
  sidebar.classList.remove("hoverable");
}

sidebarLockBtn.addEventListener("click", toggleLock);
sidebar.addEventListener("mouseleave", hideSidebar);
sidebar.addEventListener("mouseenter", showSidebar);

