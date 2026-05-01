const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      main: './js/main.js',
      store: './js/store.js',
      avatar: './js/avatar.js',
      tryon: './js/tryon.js',
      'iw-sdk-integration': './js/iw-sdk-integration.js',
      'iw-sdk-store': './js/iw-sdk-store.js',
      'iw-sdk-product-display': './js/iw-sdk-product-display.js',
      'iw-sdk-avatar': './js/iw-sdk-avatar.js',
      'iw-sdk-try-on': './js/iw-sdk-try-on.js',
      'iw-sdk-commerce-analytics': './js/iw-sdk-commerce-analytics.js',
      'error-handler': './js/error-handler.js',
      'sam-3d-integration': './js/sam-3d-integration.js',
      'sam-3d-demo': './js/sam-3d-demo.js' // Add SAM 3D demo script
    },
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProduction ? '[name].[contenthash].bundle.js' : '[name].bundle.js',
      clean: true,
      publicPath: '/'
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env', '@babel/preset-react'],
              cacheDirectory: true
            }
          }
        },
        {
          test: /\.css$/,
          use: [
            'style-loader',
            {
              loader: 'css-loader',
              options: {
                importLoaders: 2,
                modules: false // Don't use CSS modules for this project
              }
            },
            'postcss-loader'
          ]
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'images/[name].[hash][ext]'
          }
        },
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'fonts/[name].[hash][ext]'
          }
        },
        {
          test: /\.(gltf|glb)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'models/[name].[hash][ext]'
          }
        }
      ]
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: './index.html',
        filename: 'index.html',
        minify: isProduction ? {
          removeComments: true,
          collapseWhitespace: true,
          removeRedundantAttributes: true,
          useShortDoctype: true,
          removeEmptyAttributes: true,
          removeStyleLinkTypeAttributes: true,
          keepClosingSlash: true,
          minifyJS: true,
          minifyCSS: true,
          minifyURLs: true,
        } : false
      })
    ],
    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction, // Remove console logs in production
            },
          },
        }),
      ],
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            enforce: true
          }
        }
      }
    },
    devServer: {
      static: {
        directory: path.join(__dirname, ''),
      },
      compress: true,
      port: process.env.PORT || 3000,
      host: '0.0.0.0', // Allow connections from Docker
      hot: true,
      open: process.env.NODE_ENV !== 'docker', // Don't auto-open in Docker
      historyApiFallback: true,
      client: {
        overlay: {
          errors: true,
          warnings: false,
        },
      },
      allowedHosts: 'all', // Allow connections from any host (for Docker)
    },
    resolve: {
      extensions: ['.js', '.jsx', '.json']
    },
    // Performance hints
    performance: {
      maxAssetSize: isProduction ? 500000 : 1000000, // 500KB in production, 1MB in development
      maxEntrypointSize: isProduction ? 500000 : 1000000,
      hints: isProduction ? 'warning' : false
    },
    // Source maps for debugging
    devtool: isProduction ? 'source-map' : 'eval-source-map'
  };
};