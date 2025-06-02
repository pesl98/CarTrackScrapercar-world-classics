// Global variables
let currentPage = 1;
let currentPerPage = 20;
let currentSearch = '';
let currentStatus = 'all';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    loadCars();
    
    // Set up search input with debounce
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentSearch = this.value;
            currentPage = 1;
            loadCars();
        }, 500);
    });
    
    // Status filter change handler
    document.getElementById('statusFilter').addEventListener('change', function() {
        currentStatus = this.value;
        currentPage = 1;
        loadCars();
    });
});

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stats = await response.json();
        
        document.getElementById('stat-total').textContent = formatNumber(stats.total_cars);
        document.getElementById('stat-active').textContent = formatNumber(stats.active_cars);
        document.getElementById('stat-sold').textContent = formatNumber(stats.sold_cars);
        document.getElementById('stat-days').textContent = stats.avg_days_on_market;
        document.getElementById('stat-changes').textContent = formatNumber(stats.recent_price_changes);
        document.getElementById('stat-price').textContent = '€' + formatNumber(stats.avg_price);
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        showAlert('Error', 'Failed to load dashboard statistics: ' + error.message, 'danger');
    }
}

// Load cars with current filters
async function loadCars() {
    showLoading(true);
    
    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: currentPerPage,
            search: currentSearch,
            status: currentStatus
        });
        
        const response = await fetch(`/api/cars?${params}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayCars(data.cars);
        displayPagination(data);
        
    } catch (error) {
        console.error('Error loading cars:', error);
        showAlert('Error', 'Failed to load cars: ' + error.message, 'danger');
        displayCars([]); // Show empty state
    } finally {
        showLoading(false);
    }
}

// Display cars in the table
function displayCars(cars) {
    const tbody = document.getElementById('carsTableBody');
    
    if (cars.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center py-5">
                    <div class="empty-state">
                        <i class="fas fa-car-side text-muted"></i>
                        <h5>No cars found</h5>
                        <p class="text-muted">Try adjusting your search filters or check back later.</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = cars.map(car => {
        const imageHtml = car.image_url 
            ? `<img src="${escapeHtml(car.image_url)}" alt="Car" class="car-image" onerror="this.style.display='none'">`
            : `<div class="car-image bg-light d-flex align-items-center justify-content-center">
                 <i class="fas fa-car text-muted"></i>
               </div>`;
        
        const statusClass = car.is_sold ? 'status-sold' : 'status-active';
        const statusText = car.is_sold ? 'Sold' : 'Active';
        
        const daysOnMarket = Math.round(car.days_on_market || 0);
        let daysClass = 'days-on-market';
        if (daysOnMarket > 60) daysClass += ' very-long-term';
        else if (daysOnMarket > 30) daysClass += ' long-term';
        
        return `
            <tr class="fade-in">
                <td>${imageHtml}</td>
                <td>
                    <div class="fw-bold">${escapeHtml(car.make)}</div>
                    <div class="text-muted small">${escapeHtml(car.model)}</div>
                </td>
                <td>${car.year || '-'}</td>
                <td>
                    <span class="badge price-badge bg-success">€${formatNumber(car.current_price)}</span>
                </td>
                <td>${car.mileage ? formatNumber(car.mileage) + ' km' : '-'}</td>
                <td>${car.fuel_type || '-'}</td>
                <td>
                    <span class="${daysClass}">${daysOnMarket} days</span>
                </td>
                <td>
                    <span class="badge ${statusClass}">${statusText}</span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary btn-view-details" 
                            onclick="viewCarDetails(${car.id})">
                        <i class="fas fa-eye me-1"></i>View
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Display pagination
function displayPagination(data) {
    const pagination = document.getElementById('pagination');
    
    if (data.total_pages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let paginationHtml = '';
    
    // Previous button
    if (data.page > 1) {
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${data.page - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
    }
    
    // Page numbers
    const startPage = Math.max(1, data.page - 2);
    const endPage = Math.min(data.total_pages, data.page + 2);
    
    if (startPage > 1) {
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(1)">1</a>
            </li>
        `;
        if (startPage > 2) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === data.page ? 'active' : '';
        paginationHtml += `
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    if (endPage < data.total_pages) {
        if (endPage < data.total_pages - 1) {
            paginationHtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${data.total_pages})">${data.total_pages}</a>
            </li>
        `;
    }
    
    // Next button
    if (data.page < data.total_pages) {
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${data.page + 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    }
    
    pagination.innerHTML = paginationHtml;
}

// Change page
function changePage(page) {
    currentPage = page;
    loadCars();
}

// Change items per page
function changePerPage() {
    currentPerPage = parseInt(document.getElementById('perPageSelect').value);
    currentPage = 1;
    loadCars();
}

// Apply filters
function applyFilters() {
    currentSearch = document.getElementById('searchInput').value;
    currentStatus = document.getElementById('statusFilter').value;
    currentPage = 1;
    loadCars();
}

// View car details
function viewCarDetails(carId) {
    window.location.href = `/car/${carId}`;
}

// Manual scrape trigger
async function manualScrape() {
    const button = event.target;
    const originalText = button.innerHTML;
    
    // Show loading state
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Scraping...';
    
    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Success', result.message, 'success');
            // Refresh data
            loadDashboardStats();
            loadCars();
        } else {
            showAlert('Error', result.error || 'Scraping failed', 'danger');
        }
        
    } catch (error) {
        console.error('Error during manual scrape:', error);
        showAlert('Error', 'Failed to start scraping: ' + error.message, 'danger');
    } finally {
        // Restore button state
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Show/hide loading spinner
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

// Show alert modal
function showAlert(title, message, type = 'info') {
    const modal = new bootstrap.Modal(document.getElementById('alertModal'));
    const modalTitle = document.getElementById('alertModalTitle');
    const modalBody = document.getElementById('alertModalBody');
    
    modalTitle.textContent = title;
    modalBody.innerHTML = `<div class="alert alert-${type} mb-0">${escapeHtml(message)}</div>`;
    
    modal.show();
}

// Utility functions
function formatNumber(num) {
    if (!num) return '0';
    return new Intl.NumberFormat('en-US').format(num);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Download CSV export
function downloadCSV() {
    window.location.href = '/api/export/csv';
}

// Auto-refresh data every 5 minutes
setInterval(() => {
    loadDashboardStats();
    loadCars();
}, 5 * 60 * 1000);
