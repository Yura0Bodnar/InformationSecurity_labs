function loadActiveLab() {
    const activeLab = localStorage.getItem('activeLab');
    if (activeLab) {
        showLab(activeLab);
    }
}

function showLab(labId) {
    const labs = document.querySelectorAll('.lab-content');
    labs.forEach(lab => lab.classList.remove('active'));
    const selectedLab = document.getElementById(labId);
    selectedLab.classList.add('active');
}

function downloadResults() {
    window.location.href = '/download_results'; // Завантаження файлу
}

window.onload = loadActiveLab;
