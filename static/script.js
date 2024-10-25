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

// Функція для показу конкретної лабораторної роботи

// Функція для завантаження результатів (для першої лабораторної роботи)
function downloadResults() {
    window.location.href = '/download_results'; // Завантаження файлу
}

function showLoadingMessage() {
    // Відображаємо повідомлення
    document.getElementById('loadingMessage').style.display = 'block';
}

// Зберігаємо пароль для шифрування
let encryptionPassword = '';

// Функція для встановлення пароля для шифрування
function setEncryptionPassword() {
    // Зберігаємо пароль
    encryptionPassword = document.getElementById("encryptionPassword").value;

    // Показуємо секцію з шифруванням/дешифруванням
    document.getElementById("encryptionSection").style.display = "block";
    document.getElementById("passwordSection").style.display = "none";
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
            event.preventDefault();  // Зупиняємо стандартне відправлення форми

            const formData = new FormData();
            const fileInput = document.getElementById('encryptFile');
            const file = fileInput.files[0];

            if (!file) {
                alert("Будь ласка, виберіть файл для шифрування.");
                return;
            }

            formData.append("encrypt_file", file);

            try {
                const response = await fetch("/lab3/encrypt_file", {
                    method: "POST",
                    body: formData
                });

                if (response.ok) {
                    const result = await response.text();
                    document.getElementById('encryptFileSuccess').style.display = 'block';
                    document.getElementById('encryptFileSuccess').innerText = "Файл успішно зашифровано!";
                } else {
                    alert("Сталася помилка під час шифрування.");
                }
            } catch (error) {
                console.error("Помилка:", error);
                alert("Сталася помилка під час шифрування.");
            }
        }

async function decryptFile(event) {
    event.preventDefault();  // Зупиняємо стандартне відправлення форми

    const formData = new FormData();
    const fileInput = document.getElementById('decryptFile');
    const passwordInput = document.getElementById('decryptFilePassword');
    const file = fileInput.files[0];
    const password = passwordInput.value;

    if (!file || !password) {
        alert("Будь ласка, виберіть файл та введіть пароль для дешифрування.");
        return;
    }

    formData.append("decrypt_file", file);
    formData.append("decrypt_password", password);

    try {
        const response = await fetch("/lab3/decrypt_file", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const result = await response.text();
            document.getElementById('decryptFileSuccess').style.display = 'block';
            document.getElementById('decryptFileSuccess').innerText = "Файл успішно дешифровано!";
        } else {
            document.getElementById('decryptError').style.display = 'block';
        }
    } catch (error) {
        console.error("Помилка:", error);
        document.getElementById('decryptError').style.display = 'block';
    }
}
