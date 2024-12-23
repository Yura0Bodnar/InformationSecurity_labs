// Завантаження активної лабораторної роботи з localStorage
function loadActiveLab(labId) {
    // Отримуємо всі елементи з класом 'lab-content'
    const labs = document.querySelectorAll('.lab-content');

    // Проходимо по кожній лабораторній роботі
    labs.forEach(lab => {
        // Якщо ID елемента відповідає labId, показуємо його, інакше приховуємо
        if (lab.id === labId) {
            lab.style.display = 'block'; // Показуємо активну лабораторну роботу
        } else {
            lab.style.display = 'none'; // Приховуємо всі інші лабораторні роботи
        }
    });
}

// Функція для завантаження результатів (для першої лабораторної роботи)
function downloadResults() {
    window.location.href = '/download_results'; // Завантаження файлу
}


async function submitPasswordForm(event) {
    event.preventDefault(); // Prevent the default form submission

    const password = document.getElementById("encryptionPassword").value;

    try {
        const response = await fetch("/lab3/set_password", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ "password": password })
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data.message); // Log success message

            // Display the success message to the user
            document.getElementById("passwordSaveMessage").style.display = "block";
            document.getElementById("passwordSaveMessage").textContent = data.message;

            // Show the encryption section and hide the password section
            document.getElementById("encryptionSection").style.display = "block";
            document.getElementById("passwordSection").style.display = "none";
        } else {
            console.error("Failed to save password.");
        }
    } catch (error) {
        console.error("Error:", error);
    }
}


// Функція для відображення повідомлення про завантаження
function showLoadingMessage() {
    document.getElementById('loadingMessage').style.display = 'block';
}

// Функція для приховування повідомлення про завантаження
function hideLoadingMessage() {
    document.getElementById('loadingMessage').style.display = 'none';
}

async function encryptFile(event) {
    event.preventDefault(); // Зупиняємо стандартне відправлення форми
    showLoadingMessage(); // Показуємо повідомлення про завантаження

    const fileInput = document.getElementById("encryptFile");
    const file = fileInput.files[0];
    const messageElement = document.getElementById("encryptFileMessage");
    const timeElement = document.getElementById("encryptionTime"); // Новий елемент для виведення часу шифрування

    if (!file) {
        console.error("File not provided.");
        messageElement.style.display = "block";
        messageElement.textContent = "Please select a file to encrypt.";
        hideLoadingMessage(); // Приховуємо повідомлення про завантаження
        return false;
    }

    const formData = new FormData();
    formData.append("encrypt_file", file);

    try {
        const response = await fetch("/lab3/encrypt_file", {
            method: "POST",
            body: formData
        });

        const responseData = await response.json();
        if (response.ok) {
            messageElement.style.display = "block";
            messageElement.style.color = "green";
            messageElement.textContent = responseData.message;

            // Виводимо час шифрування
            if (responseData.rc5_enc_time) {
                timeElement.style.display = "block"; // Показуємо блок з часом
                timeElement.style.color = "green";
                timeElement.textContent = responseData.rc5_enc_time; // Виводимо час
            }
        } else {
            messageElement.style.display = "block";
            messageElement.style.color = "red";
            messageElement.textContent = "File encryption failed.";
        }
    } catch (error) {
        console.error("Error during file encryption:", error);
        messageElement.style.display = "block";
        messageElement.style.color = "red";
        messageElement.textContent = "Error during encryption.";
    } finally {
        hideLoadingMessage(); // Приховуємо повідомлення після завершення операції
    }

    return false;
}


async function decryptFile(event) {
    event.preventDefault();  // Зупиняємо стандартне відправлення форми
    showLoadingMessage(); // Показуємо повідомлення про завантаження

    const fileInput = document.getElementById('decryptFile');
    const passwordInput = document.getElementById('decryptFilePassword');
    const messageElement = document.getElementById("decryptError");
    const successElement = document.getElementById("decryptFileSuccess");
    const timeElement = document.getElementById("decryptionTime"); // Новий елемент для виведення часу дешифрування

    const file = fileInput.files[0];
    const password = passwordInput.value;

    if (!file || !password) {
        alert("Будь ласка, виберіть файл та введіть пароль для дешифрування.");
        hideLoadingMessage(); // Приховуємо повідомлення про завантаження
        return;
    }

    const formData = new FormData();
    formData.append("decrypt_file", file);
    formData.append("password", password);

    try {
        const response = await fetch("/lab3/decrypt_file", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        if (response.ok) {
            successElement.style.display = 'block';
            successElement.textContent = data.message;
            messageElement.style.display = 'none'; // Приховуємо помилку, якщо вона була

            // Виводимо час дешифрування
            if (data.rc5_dec_time) {
                timeElement.style.display = 'block'; // Показуємо блок з часом
                timeElement.style.color = 'green';
                timeElement.textContent = data.rc5_dec_time; // Виводимо час
            }
        } else {
            successElement.style.display = 'none';
            messageElement.style.display = 'block';
            messageElement.textContent = "Дешифрування не відбулося. Неправильний пароль або інша помилка.";
        }
    } catch (error) {
        console.error("Error during decryption:", error);
        successElement.style.display = 'none';
        messageElement.style.display = 'block';
        messageElement.textContent = "Помилка під час дешифрування файлу.";
    } finally {
        hideLoadingMessage(); // Приховуємо повідомлення після завершення операції
    }
}


document.getElementById("encryptFileForm").addEventListener("submit", encryptFile);
document.getElementById("decryptFileForm").addEventListener("submit", decryptFile);


// Функція для асинхронного шифрування тексту
async function encryptTextForm(event) {
    event.preventDefault(); // Зупиняємо стандартне відправлення форми
    showLoadingMessage(); // Показуємо повідомлення про завантаження

    const text = document.getElementById("encryptText").value;
    const messageElement = document.getElementById("encryptTextMessage");

    try {
        const response = await fetch("/lab3/encrypt_text", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ "input_text": text })
        });

        if (response.ok) {
            const data = await response.json();
            messageElement.style.display = "block";
            messageElement.style.color = "green";
            messageElement.innerHTML = data.message;
        } else {
            messageElement.style.display = "block";
            messageElement.style.color = "red";
            messageElement.innerHTML = "Шифрування не вдалося.";
        }
    } catch (error) {
        console.error("Помилка під час шифрування тексту:", error);
        messageElement.style.display = "block";
        messageElement.style.color = "red";
        messageElement.innerHTML = "Помилка під час шифрування тексту.";
    } finally {
        hideLoadingMessage(); // Приховуємо повідомлення після завершення операції
    }
}

// Функція для асинхронного дешифрування тексту
async function decryptTextForm(event) {
    event.preventDefault();

    const encryptedText = document.getElementById("decryptText").value;
    const password = document.getElementById("decryptTextPassword").value;

    try {
        const response = await fetch("/lab3/decrypt_text", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ "input_text": encryptedText, "password": password })
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById("decryptTextMessage").style.display = "block";
            document.getElementById("decryptTextMessage").style.color = "green";
            document.getElementById("decryptTextMessage").innerHTML = data.message;
        } else {
            document.getElementById("decryptTextMessage").style.display = "block";
            document.getElementById("decryptTextMessage").style.color = "red";
            document.getElementById("decryptTextMessage").innerHTML = "Неправильний пароль.";
        }
    } catch (error) {
        console.error("Помилка під час дешифрування тексту:", error);
        document.getElementById("decryptTextMessage").style.display = "block";
        document.getElementById("decryptTextMessage").style.color = "red";
        document.getElementById("decryptTextMessage").innerHTML = "Помилка під час дешифрування тексту.";
    }
    return false;
}

document.getElementById("encryptTextForm").addEventListener("submit", encryptTextForm);
document.getElementById("decryptTextForm").addEventListener("submit", decryptTextForm);


async function decryptStringRSA() {
    const encryptedText = document.getElementById("encryptedText").value;
    const resultDiv = document.getElementById("decryptResult");

    try {
        const response = await fetch('/lab4/decrypt_string', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ encrypted_text: encryptedText }),
        });

        const result = await response.json();

        if (result.status === "success") {
            resultDiv.innerHTML = `<h4>Розшифрований текст:</h4><p>${result.decrypted_result}</p>`;
            resultDiv.style.color = "green";
        } else {
            resultDiv.innerHTML = `<h4>Помилка:</h4><p>${result.message}</p>`;
            resultDiv.style.color = "red";
        }
    } catch (error) {
        console.error("Помилка запиту:", error);
        resultDiv.innerHTML = `<h4>Помилка:</h4><p>Сталася помилка під час запиту до сервера.</p>`;
        resultDiv.style.color = "red";
    }
}


document.getElementById("verifySignatureForm").addEventListener("submit", async (event) => {
    event.preventDefault(); // Запобігає стандартній відправці форми

    const signature = document.getElementById("signature").value; // Отримуємо значення підпису
    const resultDiv = document.getElementById("verificationResult"); // Блок для результатів перевірки

    try {
        // Відправка запиту на сервер
        const response = await fetch("/lab5/verify_signature", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({ signature: signature }),
        });

        if (response.ok) {
            const html = await response.text(); // Отримуємо HTML як текст

            // Визначення кольору залежно від результату
            if (html.includes("Підпис дійсний")) {
                resultDiv.style.color = "green";
            } else if (html.includes("Підпис недійсний")) {
                resultDiv.style.color = "red";
            } else {
                resultDiv.style.color = "black"; // У разі непередбаченого результату
            }

            resultDiv.innerHTML = html; // Вставляємо отриманий HTML у блок результатів
        } else {
            resultDiv.innerHTML = `<h4>Помилка сервера: ${response.status}</h4>`;
            resultDiv.style.color = "red";
        }
    } catch (error) {
        console.error("Помилка запиту:", error);
        resultDiv.innerHTML = `<h4>Помилка: Сталася помилка під час запиту до сервера.</h4>`;
        resultDiv.style.color = "red";
    }
});
