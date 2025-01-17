let timerInterval;
let messageContexts = [];
let messageId = 1;

function scrollToBottom() {
    var div = document.getElementById("upperid");
    div.scrollTop = div.scrollHeight;
}

scrollToBottom();

document.getElementById("userinputform").addEventListener("submit", function (event) {
    event.preventDefault();
    formsubmitted();
});

// Detecta a tecla Enter
document.getElementById('userinput').addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();  // Evita a quebra de linha no textarea
        document.getElementById('userinputform').dispatchEvent(new Event('submit'));
    }
});

const formsubmitted = async () => {
    let userinput = document.getElementById('userinput').value;
    let dbSelection = document.getElementById('db-selection').value;
    let searchType = document.getElementById('search-type').value;
    let modelSelection = document.getElementById('model-selection').value;
    let contextDocs = document.getElementById('context-docs').value;
    let chatHistory = document.getElementById('chat-history').value;
    let sendbtn = document.getElementById('sendbtn');
    let userinputarea = document.getElementById('userinput');
    let upperdiv = document.getElementById('upperid');

    // Adiciona a mensagem do usuário ao chat
    upperdiv.innerHTML = upperdiv.innerHTML + `<div class="message"><div class="usermessagediv"><div class="usermessage">${userinput}</div></div></div>`;
    sendbtn.disabled = true;
    userinputarea.disabled = true;
    scrollToBottom();

    // Inicia o contador e altera o placeholder para "Wait..."
    document.getElementById('userinput').value = "";
    startTimer();
    const startTime = new Date(); // Captura o tempo de início
    try {
        const response = await fetch('/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                {
                    msg: userinput,
                    config: {
                        db: dbSelection,
                        searchType: searchType,
                        model: modelSelection,
                        docsQtd: parseInt(contextDocs),
                        history: chatHistory
                    }
                }) // Envia o input do usuário no corpo da requisição
        });

        // Tenta processar a resposta JSON, mesmo em caso de erro
        let json = await response.json();

        // Se o status não estiver no intervalo 200-299, levanta um erro com os detalhes da resposta
        if (!response.ok) {
            throw new Error(JSON.stringify(json));  // Passa o JSON completo do erro para a exceção
        }

        stopTimer(); // Para o timer ao finalizar a requisição

        const endTime = new Date(); // Captura o tempo de fim
        const timeTaken = ((endTime - startTime) / 1000).toFixed(2); // Calcula o tempo em segundos

        // Restaura o placeholder após o sucesso
        document.getElementById('userinput').placeholder = "Your message...";

        // Verifica se há uma resposta na chave `response`
        if (json.result) {
            let message = json.result;
            let currentMessageId = messageId; // Atribui o número atual da resposta
            messageContexts.push(json.context); // Armazena o contexto da resposta
            console.log(json.used_config) // TODO colocar configuração na mensagem

            upperdiv.innerHTML = upperdiv.innerHTML + `<div class="message"><div class="appmessagediv"><div class="appmessage" id="temp-${currentMessageId}"></div></div></div>`;
            let temp = document.getElementById(`temp-${currentMessageId}`);
            let index = 0;

            function displayNextLetter() {
                scrollToBottom();
                if (index < message.length) {
                    temp.innerHTML = temp.innerHTML + message[index];
                    index++;
                    setTimeout(displayNextLetter, 3);
                } else {
                    // Adiciona um link para ver o contexto da resposta específica
                    temp.innerHTML += `<br><a href="#" class="more-info" onclick="showModal(${currentMessageId})">See Context</a> <span class="time-taken">(${timeTaken}s)</span>`;
                    temp.removeAttribute('id');
                    sendbtn.disabled = false;
                    userinputarea.disabled = false;
                }
            }

            displayNextLetter();
            scrollToBottom();

            messageId++; // Incrementa o contador para a próxima mensagem
        } else {
            throw new Error(json.message || "Unknown error occurred.");
        }

    } catch (error) {
        stopTimer(); // Para o timer ao ocorrer um erro

        // Restaura o placeholder após erro
        document.getElementById('userinput').placeholder = "Your message...";

        // Tenta processar a mensagem de erro e o trace (caso tenha sido retornado pelo backend)
        let errorDetails = {};
        try {
            errorDetails = JSON.parse(error.message);  // Tenta fazer o parse do JSON de erro
        } catch (parseError) {
            errorDetails.message = "Unknown error.";
            errorDetails.trace = "";
        }

        // Exibe a mensagem de erro e um link para ver mais detalhes
        upperdiv.innerHTML = upperdiv.innerHTML + `
            <div class="message">
                <div class="appmessagediv">
                    <div class="appmessage" style="border: 1px solid red;">
                        <strong>Error:</strong> ${errorDetails.message || "Unknown error"} <br>
                        <span id="more-info" style="display:none;">${errorDetails.trace || "No traceback available."}</span>
                        <a class="more-info" href="#" onclick="toggleTrace(event)">Read More</a>
                    </div>
                </div>
            </div>`;
        sendbtn.disabled = false;
        userinputarea.disabled = false;
    }
    scrollToBottom();
}

function closeModal() {
    document.getElementById('context-modal').classList.add('hidden');
}

function showModal(contextId) {
    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = ''; // Limpa o conteúdo anterior do modal

    // Verifica se há contexto para o ID fornecido
    if (messageContexts[contextId - 1]) { // Como os índices no array começam em 0
        messageContexts[contextId - 1].forEach(contextData => {
            const row = document.createElement('tr');
            row.classList.add('bg-white', 'dark:bg-gray-800');

            row.innerHTML = `
                <td class="px-6 py-4">${contextData.proteins_structures}</td>
                <td class="px-6 py-4">${contextData.page}</td>
                <td class="px-6 py-4">${contextData.title}</td>
                <td class="px-6 py-4">${contextData.doi}</td>
                <td class="px-6 py-4">${contextData.content}</td>
            `;

            modalBody.appendChild(row);
        });

        document.getElementById('context-modal').classList.remove('hidden');
    } else {
        console.error("No context found for this message.");
    }
}


// Função para alternar a visibilidade do trace
function toggleTrace(event) {
    event.preventDefault(); // Previne o comportamento padrão do link
    let moreInfo = event.target.previousElementSibling; // Seleciona o elemento <span> com o trace
    if (moreInfo.style.display === "none") {
        moreInfo.style.display = "block"; // Mostra o trace
        event.target.innerText = "Read less"; // Muda o texto do link
    } else {
        moreInfo.style.display = "none"; // Esconde o trace
        event.target.innerText = "Read less"; // Volta o texto do link
    }
}

function startTimer() {
    let seconds = 0;
    timerInterval = setInterval(() => {
        seconds++;
        document.getElementById('userinput').placeholder = `Wait... (${seconds}s)`;
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

const closeSidebarBtn = document.getElementById('close-sidebar-btn');
const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
const sidebar = document.getElementById('sidebar');

toggleSidebarBtn.addEventListener('click', () => {
    if (sidebar.classList.contains('hidden-sidebar')) {
        sidebar.classList.remove('hidden-sidebar');
        sidebar.classList.add('show-sidebar');
    } else {
        sidebar.classList.remove('show-sidebar');
        sidebar.classList.add('hidden-sidebar');
    }
});

closeSidebarBtn.addEventListener('click', () => {
    sidebar.classList.remove('show-sidebar');
    sidebar.classList.add('hidden-sidebar');
});

const chatHistorySlider = document.getElementById('chat-history-slider');

// Add event listener for click
chatHistorySlider.addEventListener('click', function () {
    alert('This feature will be available in a future update.');
});

// Get elements
const openModalBtn = document.getElementById('open-modal-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const configModal = document.getElementById('config-modal');

// Open modal on button click
openModalBtn.addEventListener('click', function () {
    configModal.classList.remove('hidden');
    configModal.classList.add('flex');
});

// Close modal on button click
closeModalBtn.addEventListener('click', function () {
    configModal.classList.remove('flex');
    configModal.classList.add('hidden');
});
