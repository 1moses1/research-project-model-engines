FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Install dependencies with legacy peer deps and force resolution
RUN npm install --legacy-peer-deps --force

# Copy source code
COPY public ./public
COPY src ./src

# Set environment variable to increase memory limit for build
ENV NODE_OPTIONS=--max_old_space_size=4096

# Build for production
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
