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

function showLoadingMessage() {
    // Відображаємо повідомлення
    document.getElementById('loadingMessage').style.display = 'block';
}

let encryptionPassword;

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



// Функція для перевірки пароля при дешифруванні файлу
function checkDecryptFilePassword() {
    const decryptPassword = document.getElementById("decryptFilePassword").value;

    // Перевірка, чи збігається пароль із тим, що був введений при шифруванні
    if (decryptPassword === encryptionPassword) {
        return true; // Дешифрування відбувається
    } else {
        document.getElementById("decryptFileError").style.display = "block"; // Вивести помилку
        return false; // Зупиняємо виконання дешифрування
    }
}

// Функція для перевірки пароля при дешифруванні тексту
function checkDecryptTextPassword() {
    const decryptPassword = document.getElementById("decryptTextPassword").value;

    // Перевірка, чи збігається пароль із тим, що був введений при шифруванні
    if (decryptPassword === encryptionPassword) {
        return true; // Дешифрування відбувається
    } else {
        document.getElementById("decryptTextError").style.display = "block"; // Вивести помилку
        return false; // Зупиняємо виконання дешифрування
    }
}


async function encryptFile(event) {
    console.log("Encrypt file function triggered");
    event.preventDefault(); // Prevent form submission and page reload
    console.log("Form submission prevented");

    const fileInput = document.getElementById("encryptFile");
    const file = fileInput.files[0];
    const messageElement = document.getElementById("encryptFileMessage");

    if (!file) {
        console.error("No file selected.");
        messageElement.style.display = "block";
        messageElement.textContent = "Please select a file to encrypt.";
        return false;
    }

    console.log("File selected:", file.name);

    const formData = new FormData();
    formData.append("encrypt_file", file);

    try {
        console.log("Sending POST request to /lab3/encrypt_file...");

        const response = await fetch("/lab3/encrypt_file", {
            method: "POST",
            body: formData
        });

        const responseData = await response.json();
        console.log("Response received:", responseData);

        if (response.ok) {
            console.log("File encrypted successfully.");
            messageElement.style.display = "block";
            messageElement.style.color = "green";
            messageElement.textContent = responseData.message;
        } else {
            console.error("File encryption failed. Status:", response.status);
            messageElement.style.display = "block";
            messageElement.style.color = "red";
            messageElement.textContent = responseData.message || "File encryption failed.";
        }
    } catch (error) {
        console.error("Error during file encryption:", error);
        messageElement.style.display = "block";
        messageElement.style.color = "red";
        messageElement.textContent = "Error during encryption.";
    }

    return false; // Ensure no default behavior occurs
}


async function decryptFile(event) {
    event.preventDefault(); // Зупиняємо стандартне відправлення форми

    const fileInput = document.getElementById('decryptFile');
    const passwordInput = document.getElementById('decryptFilePassword');
    const messageElement = document.getElementById("decryptError");
    const successElement = document.getElementById("decryptFileSuccess");

    const file = fileInput.files[0];
    const password = passwordInput.value;

    if (!file || !password) {
        alert("Будь ласка, виберіть файл та введіть пароль для дешифрування.");
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

        if (response.ok) {
            const data = await response.json(); // Припустимо, що ви повертаєте JSON
            successElement.style.display = 'block';
            successElement.textContent = data.message;
            messageElement.style.display = 'none'; // Приховуємо помилку, якщо вона була
        } else {
            successElement.style.display = 'none';
            messageElement.style.display = 'block';
            messageElement.textContent = "Дешифрування не відбулося. Неправильний пароль або інша помилка.";
            console.log("Response status:", response.status);
            console.log("Response body:", await response.text());
        }
    } catch (error) {
        successElement.style.display = 'none';
        messageElement.style.display = 'block';
        messageElement.textContent = "Помилка під час дешифрування файлу.";
        console.error("Error during decryption:", error);
    }
}

document.getElementById("encryptFileForm").addEventListener("submit", encryptFile);
document.getElementById("decryptFileForm").addEventListener("submit", decryptFile);