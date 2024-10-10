// Завантаження активної лабораторної роботи з localStorage
function loadActiveLab() {
    // Спробуємо завжди показувати лабораторну 2 для тестування
    showLab('lab2');
}

// Функція для показу конкретної лабораторної роботи
function showLab(labId) {
    const labs = document.querySelectorAll('.lab-content');
    labs.forEach(lab => lab.classList.remove('active')); // Прибираємо активність з усіх лабораторних

    const selectedLab = document.getElementById(labId);

    if (selectedLab) {
        selectedLab.classList.add('active'); // Додаємо клас "active" до вибраної лабораторної
        console.log(`Lab with ID ${labId} is now active.`);
        localStorage.setItem('activeLab', labId); // Зберігаємо активну лабораторну в localStorage
    } else {
        console.error(`Lab with ID ${labId} not found.`);
    }
}

// Функція для завантаження результатів (для першої лабораторної роботи)
function downloadResults() {
    window.location.href = '/download_results'; // Завантаження файлу
}

function showLoadingMessage() {
    // Відображаємо повідомлення
    document.getElementById('loadingMessage').style.display = 'block';
}