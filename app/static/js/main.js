// Function to toggle mobile menu
function toggleMenu() {
    const navbarCollapse = document.getElementById('navbarNav');
    if (navbarCollapse) {
        navbarCollapse.classList.toggle('show');
    }
}


function createMetricCard(container, label, value, delta = null) {
    const metricCard = document.createElement('div');
    metricCard.className = 'metric-card';
    
    const labelEl = document.createElement('div');
    labelEl.className = 'metric-label';
    labelEl.textContent = label;
    
    const valueEl = document.createElement('div');
    valueEl.className = 'metric-value';
    valueEl.textContent = value;
    
    metricCard.appendChild(labelEl);
    metricCard.appendChild(valueEl);
    
    if (delta !== null) {
        const deltaEl = document.createElement('div');
        deltaEl.className = `metric-delta ${parseFloat(delta) >= 0 ? 'positive' : 'negative'}`;
        deltaEl.textContent = `${delta >= 0 ? '+' : ''}${delta}%`;
        metricCard.appendChild(deltaEl);
    }
    
    container.appendChild(metricCard);
}

// Close alert messages when clicking the X button
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.style.display = 'none';
        });
    });
    
});