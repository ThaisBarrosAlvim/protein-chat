let timerInterval;
let responseContext = [];

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

    try {
        const response = await fetch('/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({msg: userinput}) // Envia o input do usuário no corpo da requisição
        });

        // Tenta processar a resposta JSON, mesmo em caso de erro
        let json = await response.json();

        // Se o status não estiver no intervalo 200-299, levanta um erro com os detalhes da resposta
        if (!response.ok) {
            throw new Error(JSON.stringify(json));  // Passa o JSON completo do erro para a exceção
        }

        stopTimer(); // Para o timer ao finalizar a requisição

        // Restaura o placeholder após o sucesso
        document.getElementById('userinput').placeholder = "Your message...";

        // Verifica se há uma resposta na chave `response`
        if (json.result) {
            let message = json.result;
            responseContext = json.context; // Armazena o contexto globalmente
            upperdiv.innerHTML = upperdiv.innerHTML + `<div class="message"><div class="appmessagediv"><div class="appmessage" id="temp"></div></div></div>`;
            let temp = document.getElementById('temp');
            let index = 0;

            function displayNextLetter() {
                scrollToBottom();
                if (index < message.length) {
                    temp.innerHTML = temp.innerHTML + message[index];
                    index++;
                    setTimeout(displayNextLetter, 30);
                } else {
                    temp.innerHTML += `<br><a href="#" class="more-info" onclick="showModal()">See Context</a>`;
                    temp.removeAttribute('id');
                    sendbtn.disabled = false;
                    userinputarea.disabled = false;
                }
            }

            displayNextLetter();
            scrollToBottom();
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
                        <span  id="more-info" style="display:none;">${errorDetails.trace || "No traceback available."}</span>
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

function showModal() {
    // Limpa o corpo do modal antes de adicionar novos dados
    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = ''; // Limpa as linhas anteriores, se houver

    // Itera sobre o contexto e cria uma linha de tabela para cada documento
    responseContext.forEach(contextData => {
        const row = document.createElement('tr'); // Cria uma nova linha
        row.classList.add('bg-white', 'dark:bg-gray-800'); // Adiciona classes para fundo no modo claro e escuro

        row.innerHTML = `
                            <td class="px-6 py-4">${contextData.file}</td>
                            <td class="px-6 py-4">${contextData.page}</td>
                            <td class="px-6 py-4">${contextData.title}</td>
                            <td class="px-6 py-4">${contextData.doi}</td>
                            <td class="px-6 py-4">${contextData.content}</td>
                            `;

        modalBody.appendChild(row); // Adiciona a nova linha ao tbody
    });

    // Exibe o modal
    document.getElementById('context-modal').classList.remove('hidden');
}


// Função para alternar a visibilidade do trace
function toggleTrace(event) {
    event.preventDefault(); // Previne o comportamento padrão do link
    let moreInfo = event.target.previousElementSibling; // Seleciona o elemento <span> com o trace
    if (moreInfo.style.display === "none") {
        moreInfo.style.display = "block"; // Mostra o trace
        event.target.innerText = "Ler menos"; // Muda o texto do link
    } else {
        moreInfo.style.display = "none"; // Esconde o trace
        event.target.innerText = "Ler mais"; // Volta o texto do link
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