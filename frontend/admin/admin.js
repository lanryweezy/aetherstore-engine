// Aetherstore Admin Interface
// Brand management system for creating and managing 3D stores

class AdminInterface {
    constructor() {
        this.currentView = 'dashboard';
        this.products = [];
        this.currentTemplate = 'modern-gallery';
        this.currentLayout = 'grid';
        
        this.init();
    }
    
    init() {
        console.log('Initializing Aetherstore Admin Interface...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        this.loadProducts();
        
        // Set up navigation
        this.setupNavigation();
        
        // Show dashboard by default
        this.showSection('dashboard');
    }
    
    setupEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const sectionId = e.target.getAttribute('href').substring(1);
                this.showSection(sectionId);
            });
        });
        
        // Template selection
        document.querySelectorAll('.template-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const template = e.currentTarget.getAttribute('data-template');
                this.selectTemplate(template);
            });
        });
        
        // Layout selection
        document.querySelectorAll('.layout-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const layout = e.currentTarget.getAttribute('data-layout');
                this.selectLayout(layout);
            });
        });
        
        // Store design controls
        document.getElementById('enter-preview')?.addEventListener('click', () => {
            this.enterStorePreview();
        });
        
        document.getElementById('save-store')?.addEventListener('click', () => {
            this.saveStoreDesign();
        });
        
        document.getElementById('publish-store')?.addEventListener('click', () => {
            this.publishStore();
        });
        
        // Product management
        document.getElementById('add-product-btn')?.addEventListener('click', () => {
            this.openProductModal();
        });
        
        document.querySelector('.close')?.addEventListener('click', () => {
            this.closeProductModal();
        });
        
        document.querySelector('.cancel-btn')?.addEventListener('click', () => {
            this.closeProductModal();
        });
        
        document.getElementById('product-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProduct();
        });
        
        document.getElementById('add-color')?.addEventListener('click', () => {
            this.addColorInput();
        });
        
        // Color pickers
        document.getElementById('primary-color')?.addEventListener('change', (e) => {
            this.updateStorePreviewColor('primary', e.target.value);
        });
        
        document.getElementById('secondary-color')?.addEventListener('change', (e) => {
            this.updateStorePreviewColor('secondary', e.target.value);
        });
    }
    
    setupNavigation() {
        // Initialize active navigation state
        document.querySelector('.nav-link.active')?.classList.remove('active');
        document.querySelector('.nav-link[href="#dashboard"]').classList.add('active');
    }
    
    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show selected section
        document.getElementById(sectionId).classList.add('active');
        
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`.nav-link[href="#${sectionId}"]`).classList.add('active');
        
        // Load specific data for section
        switch(sectionId) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'store-design':
                this.loadStoreDesignData();
                break;
            case 'products':
                this.loadProducts();
                break;
            case 'analytics':
                this.loadAnalyticsData();
                break;
        }
        
        this.currentView = sectionId;
    }
    
    loadDashboardData() {
        // Simulate loading dashboard metrics
        console.log('Loading dashboard data...');
        
        // Update visitor count
        const visitorCard = document.querySelector('.dashboard-cards .card:nth-child(1) p');
        visitorCard.textContent = Math.floor(Math.random() * 1000) + 2000;
        
        // Update try-on count
        const tryonCard = document.querySelector('.dashboard-cards .card:nth-child(2) p');
        tryonCard.textContent = Math.floor(Math.random() * 100) + 300;
        
        // In a real implementation, this would fetch from the backend
    }
    
    selectTemplate(template) {
        // Update UI to show selected template
        document.querySelectorAll('.template-item').forEach(item => {
            item.classList.remove('active');
        });
        
        event.currentTarget.classList.add('active');
        this.currentTemplate = template;
        
        console.log(`Selected template: ${template}`);
        
        // Update store preview
        this.updateStorePreview();
    }
    
    selectLayout(layout) {
        // Update UI to show selected layout
        document.querySelectorAll('.layout-option').forEach(option => {
            option.classList.remove('active');
        });
        
        event.currentTarget.classList.add('active');
        this.currentLayout = layout;
        
        console.log(`Selected layout: ${layout}`);
        
        // Update store preview
        this.updateStorePreview();
    }
    
    updateStorePreviewColor(type, color) {
        // Update the store preview with selected color
        console.log(`Updated ${type} color to: ${color}`);
        
        // In a real implementation, this would update the 3D preview
        const previewContainer = document.querySelector('.preview-placeholder');
        if (type === 'primary') {
            previewContainer.style.backgroundColor = color;
            previewContainer.style.color = this.getContrastColor(color);
        }
    }
    
    getContrastColor(hexColor) {
        // Calculate whether to use light or dark text based on background
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        return brightness > 128 ? '#000000' : '#FFFFFF';
    }
    
    updateStorePreview() {
        // Update the 3D preview based on selected template and layout
        console.log(`Updating store preview with template: ${this.currentTemplate}, layout: ${this.currentLayout}`);
        
        const previewContainer = document.querySelector('.preview-placeholder');
        previewContainer.innerHTML = `
            <p>${this.currentTemplate.replace('-', ' ')} - ${this.currentLayout}</p>
            <p>3D Store Visualization</p>
            <button id="enter-preview">Enter Store</button>
        `;
        
        // Reattach event listener
        document.getElementById('enter-preview')?.addEventListener('click', () => {
            this.enterStorePreview();
        });
    }
    
    enterStorePreview() {
        // Open store in preview mode
        console.log('Entering store preview mode');
        
        // In a real implementation, this would open the 3D store in an iframe or new window
        alert('Opening store preview in 3D environment...');
    }
    
    async saveStoreDesign() {
        // Save the store design to the backend
        const storeDesign = {
            template: this.currentTemplate,
            layout: this.currentLayout,
            primaryColor: document.getElementById('primary-color')?.value || '#4ecdc4',
            secondaryColor: document.getElementById('secondary-color')?.value || '#ff6b6b',
            lighting: document.getElementById('lighting-setting')?.value || 'bright',
            updatedAt: new Date().toISOString()
        };
        
        console.log('Saving store design:', storeDesign);
        
        try {
            // Simulate API call
            const response = await this.makeApiRequest('/stores', {
                method: 'POST',
                body: JSON.stringify(storeDesign)
            });
            
            console.log('Store design saved:', response);
            alert('Store design saved successfully!');
        } catch (error) {
            console.error('Error saving store design:', error);
            alert('Error saving store design. Please try again.');
        }
    }
    
    async publishStore() {
        // Publish the store to make it live
        console.log('Publishing store...');
        
        try {
            // Simulate API call
            const response = await this.makeApiRequest('/stores/publish', {
                method: 'POST',
                body: JSON.stringify({ 
                    template: this.currentTemplate,
                    isPublished: true 
                })
            });
            
            console.log('Store published:', response);
            alert('Store published successfully! It is now live for customers.');
        } catch (error) {
            console.error('Error publishing store:', error);
            alert('Error publishing store. Please try again.');
        }
    }
    
    loadProducts() {
        // Simulate loading products from the backend
        this.products = [
            {
                id: 'prod-001',
                name: 'Designer Jacket',
                description: 'Premium leather jacket with metallic details',
                price: 499.99,
                category: 'outerwear',
                sizes: ['S', 'M', 'L', 'XL'],
                colors: ['#000000', '#8B4513', '#DC143C'],
                image: 'jacket-thumb.jpg'
            },
            {
                id: 'prod-002',
                name: 'Evening Gown',
                description: 'Elegant floor-length gown with sequin details',
                price: 799.99,
                category: 'dresses',
                sizes: ['XS', 'S', 'M'],
                colors: ['#FFD700', '#C0C0C0', '#000000'],
                image: 'gown-thumb.jpg'
            },
            {
                id: 'prod-003',
                name: 'Designer Sneakers',
                description: 'Limited edition sneakers with LED lights',
                price: 299.99,
                category: 'shoes',
                sizes: ['7', '8', '9', '10', '11'],
                colors: ['#FFFFFF', '#000000', '#FF00FF'],
                image: 'sneakers-thumb.jpg'
            }
        ];
        
        this.renderProductGrid();
        console.log(`Loaded ${this.products.length} products`);
    }
    
    renderProductGrid() {
        const productGrid = document.querySelector('.product-grid');
        productGrid.innerHTML = '';
        
        this.products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                <div class="product-image">
                    <img src="images/${product.image}" alt="${product.name}" style="max-width:100%; max-height:100%;">
                </div>
                <div class="product-info">
                    <h3>${product.name}</h3>
                    <p>${product.description.substring(0, 50)}...</p>
                    <div class="product-price">$${product.price}</div>
                    <div class="product-actions">
                        <button onclick="adminInterface.editProduct('${product.id}')" class="btn-secondary">Edit</button>
                        <button onclick="adminInterface.deleteProduct('${product.id}')" class="btn-secondary" style="background-color:#e74c3c;">Delete</button>
                    </div>
                </div>
            `;
            productGrid.appendChild(productCard);
        });
    }
    
    openProductModal(productId = null) {
        const modal = document.getElementById('product-modal');
        const title = document.getElementById('modal-title');
        
        if (productId) {
            title.textContent = 'Edit Product';
            // Load product data for editing
            const product = this.products.find(p => p.id === productId);
            if (product) {
                document.getElementById('product-name').value = product.name;
                document.getElementById('product-description').value = product.description;
                document.getElementById('product-price').value = product.price;
                document.getElementById('product-category').value = product.category;
                // Set size checkboxes
                product.sizes.forEach(size => {
                    const sizeCheckbox = document.querySelector(`input[type="checkbox"][value="${size}"]`);
                    if (sizeCheckbox) sizeCheckbox.checked = true;
                });
            }
        } else {
            title.textContent = 'Add New Product';
            // Reset form
            document.getElementById('product-form').reset();
        }
        
        modal.style.display = 'block';
    }
    
    closeProductModal() {
        document.getElementById('product-modal').style.display = 'none';
    }
    
    saveProduct() {
        const productData = {
            id: document.getElementById('product-id')?.value || `prod_${Date.now()}`,
            name: document.getElementById('product-name').value,
            description: document.getElementById('product-description').value,
            price: parseFloat(document.getElementById('product-price').value),
            category: document.getElementById('product-category').value,
            sizes: [],
            colors: []
        };
        
        // Get selected sizes
        document.querySelectorAll('#product-form input[type="checkbox"]:checked').forEach(checkbox => {
            productData.sizes.push(checkbox.value);
        });
        
        // Get selected colors
        document.querySelectorAll('#product-form input[type="color"]').forEach(colorInput => {
            productData.colors.push(colorInput.value);
        });
        
        if (productData.name && productData.price) {
            // Add or update product in the list
            const existingIndex = this.products.findIndex(p => p.id === productData.id);
            if (existingIndex !== -1) {
                this.products[existingIndex] = productData;
            } else {
                this.products.push(productData);
            }
            
            // Update UI
            this.renderProductGrid();
            
            // Close modal
            this.closeProductModal();
            
            console.log('Product saved:', productData);
            alert(`Product ${existingIndex !== -1 ? 'updated' : 'added'} successfully!`);
        } else {
            alert('Please fill in all required fields (name and price).');
        }
    }
    
    editProduct(productId) {
        this.openProductModal(productId);
    }
    
    deleteProduct(productId) {
        if (confirm('Are you sure you want to delete this product?')) {
            this.products = this.products.filter(p => p.id !== productId);
            this.renderProductGrid();
            console.log(`Product ${productId} deleted`);
        }
    }
    
    addColorInput() {
        const colorInputs = document.querySelector('.color-inputs');
        const newColorInput = document.createElement('input');
        newColorInput.type = 'color';
        newColorInput.value = '#ffffff';
        colorInputs.insertBefore(newColorInput, document.getElementById('add-color'));
    }
    
    async loadAnalyticsData() {
        // Load analytics data for the store
        console.log('Loading analytics data...');
        
        // In a real implementation, this would fetch from the backend
        // For now, simulate with mock data
        const analyticsData = {
            monthlyVisitors: 2450,
            monthlyRevenue: 35600,
            conversionRate: 3.2,
            avgOrderValue: 185.50
        };
        
        console.log('Analytics data loaded:', analyticsData);
    }
    
    async loadStoreDesignData() {
        // Load store design data
        console.log('Loading store design data...');
        
        // In a real implementation, this would fetch from the backend
        // For now, keep the current design values
    }
    
    // API Helper method
    async makeApiRequest(endpoint, options = {}) {
        // In a real implementation, this would make actual API calls
        // For now, simulate with a promise
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: { message: 'Request successful' }
                });
            }, 500);
        });
    }
}

// Initialize the admin interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.adminInterface = new AdminInterface();
    
    // Close modal when clicking outside of it
    window.onclick = function(event) {
        const modal = document.getElementById('product-modal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
});