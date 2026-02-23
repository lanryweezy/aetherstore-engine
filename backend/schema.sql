-- Database Schema for Aetherstore Engine
-- Defines tables for stores, products, users, avatars, and transactions

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Brands/Stores table
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_user_id UUID REFERENCES users(id),
    description TEXT,
    logo_url VARCHAR(500),
    settings JSONB DEFAULT '{}', -- Store template, color scheme, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Stores table (3D stores)
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    template VARCHAR(100) DEFAULT 'modern-gallery', -- modern-gallery, vintage-loft, luxury-palace, etc.
    description TEXT,
    settings JSONB DEFAULT '{}', -- layout, lighting, music, etc.
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id) ON DELETE CASCADE,
    store_id UUID REFERENCES stores(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    size_chart JSONB, -- e.g., {S: {chest: 85, waist: 65}, M: {chest: 90, waist: 70}, ...}
    colors JSONB, -- e.g., ['red', 'blue', 'black']
    materials JSONB, -- e.g., {fabric: 'cotton', lining: 'silk'}
    dimensions JSONB, -- e.g., {width: 50, height: 70, depth: 5}
    care_instructions TEXT,
    model_3d_url VARCHAR(500), -- URL to GLB/GLTF file
    textures_urls JSONB, -- URLs to texture files
    physics_properties JSONB, -- Properties for cloth simulation
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Product images table
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User avatars table
CREATE TABLE user_avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scan_data_url VARCHAR(500), -- URL to scan file or 3D model
    measurements JSONB, -- e.g., {height: 175, chest: 95, waist: 80, hips: 95}
    body_type VARCHAR(50), -- pear, apple, hourglass, etc.
    avatar_3d_url VARCHAR(500), -- URL to 3D avatar model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Try-on sessions table
CREATE TABLE tryon_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    avatar_id UUID REFERENCES user_avatars(id) ON DELETE SET NULL,
    session_data JSONB, -- Contains pose, lighting, camera angle, etc.
    fit_analysis JSONB, -- Contains fit quality, size recommendations, etc.
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Shopping carts table
CREATE TABLE shopping_carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cart items table
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID REFERENCES shopping_carts(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    selected_size VARCHAR(10),
    selected_color VARCHAR(50),
    price_at_time DECIMAL(10, 2), -- Price at time of adding to cart
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, product_id, selected_size, selected_color)
);

-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    cart_id UUID REFERENCES shopping_carts(id) ON DELETE SET NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, confirmed, paid, shipped, delivered, cancelled
    shipping_address JSONB,
    billing_address JSONB,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    price_at_time DECIMAL(10, 2), -- Price at time of purchase
    size VARCHAR(10),
    color VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Store analytics table
CREATE TABLE store_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    page_views INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    session_duration_seconds INTEGER DEFAULT 0,
    tryon_sessions_count INTEGER DEFAULT 0,
    add_to_cart_count INTEGER DEFAULT 0,
    purchase_count INTEGER DEFAULT 0,
    revenue DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(store_id, date)
);

-- Product analytics table
CREATE TABLE product_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    tryon_count INTEGER DEFAULT 0,
    add_to_cart_count INTEGER DEFAULT 0,
    purchase_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, date)
);

-- AI model performance table
CREATE TABLE ai_model_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    confidence_score DECIMAL(5, 4), -- 0.0000 to 1.0000
    execution_time_ms INTEGER,
    feedback JSONB, -- User feedback on AI suggestions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3D asset management table
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID, -- Can be brand_id or user_id
    owner_type VARCHAR(20), -- 'brand' or 'user'
    asset_type VARCHAR(50), -- 'model', 'texture', 'animation', 'scan'
    file_url VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER, -- in bytes
    mime_type VARCHAR(100),
    dimensions JSONB, -- for images: {width: int, height: int}, for 3D models: {polygons: int}
    status VARCHAR(20) DEFAULT 'active', -- active, processing, error, deleted
    metadata JSONB, -- Additional metadata specific to asset type
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Brand templates table (for store creation)
CREATE TABLE brand_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- 'luxury', 'streetwear', 'vintage', etc.
    settings JSONB DEFAULT '{}', -- default layout, colors, lighting, etc.
    preview_image_url VARCHAR(500),
    is_public BOOLEAN DEFAULT false, -- Whether template is available to all users
    created_by UUID REFERENCES users(id), -- NULL for system templates
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_products_brand_id ON products(brand_id);
CREATE INDEX idx_products_store_id ON products(store_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_stores_brand_id ON stores(brand_id);
CREATE INDEX idx_tryon_sessions_user_id ON tryon_sessions(user_id);
CREATE INDEX idx_tryon_sessions_product_id ON tryon_sessions(product_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_store_analytics_store_date ON store_analytics(store_id, date);
CREATE INDEX idx_product_analytics_product_date ON product_analytics(product_id, date);
CREATE INDEX idx_user_avatars_user_id ON user_avatars(user_id);