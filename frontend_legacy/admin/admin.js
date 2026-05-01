// Aetherstore Admin Interface
// Brand management system for creating and managing 3D stores

class AdminInterface {
    constructor() {
        this.currentView = 'dashboard';
        this.products = [];
        this.currentTemplate = 'modern-gallery';
        this.currentLayout = 'grid';
        
        // History state for undo/redo
        this.history = [];
        this.historyIndex = -1;

        this.init();
    }
    
    saveState() {
        // Remove redo stack if we save a new state while not at the end
        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }

        const state = {
            template: this.currentTemplate,
            layout: this.currentLayout
        };

        this.history.push(state);
        this.historyIndex++;
        this.updateUndoRedoButtons();
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            const state = this.history[this.historyIndex];
            this.applyState(state);
            this.updateUndoRedoButtons();
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            const state = this.history[this.historyIndex];
            this.applyState(state);
            this.updateUndoRedoButtons();
        }
    }

    applyState(state) {
        if (!state) return;

        this.currentTemplate = state.template;
        this.currentLayout = state.layout;

        // Update UI
        document.querySelectorAll('.template-item').forEach(item => {
            if (item.getAttribute('data-template') === this.currentTemplate) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        document.querySelectorAll('.layout-option').forEach(option => {
            if (option.getAttribute('data-layout') === this.currentLayout) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });

        this.updateStorePreview();
    }

    updateUndoRedoButtons() {
        const undoBtn = document.getElementById('undo-store');
        const redoBtn = document.getElementById('redo-store');

        if (undoBtn) undoBtn.disabled = this.historyIndex <= 0;
        if (redoBtn) redoBtn.disabled = this.historyIndex >= this.history.length - 1;
    }

    init() {
        console.log('Initializing Aetherstore Admin Interface...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Setup Drag and Drop
        this.setupDragAndDrop();

        // Load initial data
        this.loadProducts();
        
        // Set up navigation
        this.setupNavigation();
        
        // Initial state save
        this.saveState();

        // Show dashboard by default
        this.showSection('dashboard');
    }
    
    setupDragAndDrop() {
        // Global drag events for the window
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        const dropZoneElement = document.querySelector(".drop-zone");
        if (!dropZoneElement) return;

        const inputElement = dropZoneElement.querySelector(".drop-zone__input");

        dropZoneElement.addEventListener("click", (e) => {
            inputElement.click();
        });

        inputElement.addEventListener("change", (e) => {
            if (inputElement.files.length) {
                this.updateThumbnail(dropZoneElement, inputElement.files[0]);
            }
        });

        dropZoneElement.addEventListener("dragover", (e) => {
            dropZoneElement.classList.add("drop-zone--over");
        });

        ["dragleave", "dragend"].forEach((type) => {
            dropZoneElement.addEventListener(type, (e) => {
                dropZoneElement.classList.remove("drop-zone--over");
            });
        });

        // Add file drop logic to the window so the entire screen can receive files
        document.body.addEventListener("drop", (e) => {
            // Check if we're on the products tab before accepting drop
            if (this.currentView !== 'products') return;

            const file = e.dataTransfer.files[0];
            if (file && (file.name.endsWith('.glb') || file.name.endsWith('.gltf'))) {
                 // Try to open the add product modal if it's not open
                 const modal = document.getElementById('product-modal');
                 if (modal && modal.style.display !== 'block') {
                     // Need to trigger the actual UI button or method
                     const btn = document.getElementById('add-product-btn');
                     if (btn) btn.click();
                 }

                 // Update the drop zone specifically
                 const dropZone = document.querySelector(".drop-zone");
                 if (dropZone) {
                    inputElement.files = e.dataTransfer.files;
                    this.updateThumbnail(dropZone, file);
                    dropZone.classList.remove("drop-zone--over");
                 }
            } else if (file) {
                alert("Only .glb or .gltf files are supported for 3D models.");
            }
        });

        dropZoneElement.addEventListener("drop", (e) => {
            e.stopPropagation(); // Stop the body drop event from firing
            if (e.dataTransfer.files.length) {
                inputElement.files = e.dataTransfer.files;
                this.updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
            }
            dropZoneElement.classList.remove("drop-zone--over");
        });
    }

    updateThumbnail(dropZoneElement, file) {
        let thumbnailElement = dropZoneElement.querySelector(".drop-zone__thumb");

        // First time - remove the prompt
        if (dropZoneElement.querySelector(".drop-zone__prompt")) {
            dropZoneElement.querySelector(".drop-zone__prompt").remove();
        }

        // First time - there is no thumbnail element, so lets create it
        if (!thumbnailElement) {
            thumbnailElement = document.createElement("div");
            thumbnailElement.classList.add("drop-zone__thumb");
            dropZoneElement.appendChild(thumbnailElement);
        }

        thumbnailElement.dataset.label = file.name;

        // Show a placeholder for 3D files since we can't easily preview them in standard img
        thumbnailElement.style.backgroundImage = 'none';
        thumbnailElement.style.display = 'flex';
        thumbnailElement.style.alignItems = 'center';
        thumbnailElement.style.justifyContent = 'center';
        thumbnailElement.innerHTML = '<span>📦 3D Model Selected</span>';

        // Update the actual preview container message
        const previewContainer = document.getElementById('model-preview-container');
        if (previewContainer) {
            previewContainer.innerHTML = `<p>File loaded: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)</p>`;
        }
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
        
        document.getElementById('undo-store')?.addEventListener('click', () => {
            this.undo();
        });

        document.getElementById('redo-store')?.addEventListener('click', () => {
            this.redo();
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
        this.saveState();
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
        this.saveState();
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
        
        // Show skeleton loading if products are empty (simulating loading state)
        if (!this.products || this.products.length === 0) {
            for (let i = 0; i < 4; i++) {
                const skeletonCard = document.createElement('div');
                skeletonCard.className = 'product-card skeleton-container';
                skeletonCard.style.padding = '15px';
                skeletonCard.innerHTML = `
                    <div class="skeleton-image"></div>
                    <div class="skeleton-title"></div>
                    <div class="skeleton-text"></div>
                    <div class="skeleton-text" style="width: 50%;"></div>
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <div class="skeleton-button" style="width: 50%;"></div>
                        <div class="skeleton-button" style="width: 50%;"></div>
                    </div>
                `;
                productGrid.appendChild(skeletonCard);
            }
            return;
        }

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