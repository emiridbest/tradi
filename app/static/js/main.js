// Function to toggle mobile menu
function toggleMenu() {
    const navbarCollapse = document.getElementById('navbarNav');
    if (navbarCollapse) {
        navbarCollapse.classList.toggle('show');
    }
}

// Function to save recent stock symbols to localStorage
function saveRecentStock(symbol) {
    if (!symbol) return;
    
    let recentStocks = JSON.parse(localStorage.getItem('recentStocks') || '[]');
    
    recentStocks = recentStocks.filter(s => s !== symbol);
    
    recentStocks.unshift(symbol);
    
    recentStocks = recentStocks.slice(0, 5);
    
    localStorage.setItem('recentStocks', JSON.stringify(recentStocks));
}

// Function to create a metric card like Streamlit's st.metric()
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
    
    // Store the symbol when analyzing
    const form = document.getElementById('analysisForm');
    if (form) {
        form.addEventListener('submit', function() {
            const symbol = document.getElementById('symbol').value;
            if (symbol) {
                saveRecentStock(symbol);
            }
        });
    }
});