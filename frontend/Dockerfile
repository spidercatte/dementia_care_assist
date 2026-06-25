# Stage 1: Build static assets
FROM node:20-alpine AS build

WORKDIR /app

# Copy package management files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy frontend source files
COPY . .

# Set up build argument for backend URL and inject as environment variable for Vite
ARG VITE_BACKEND_URL
ENV VITE_BACKEND_URL=${VITE_BACKEND_URL}

ARG VITE_USER_API_KEY
ENV VITE_USER_API_KEY=${VITE_USER_API_KEY}

# Build production assets
RUN npm run build

# Stage 2: Serve built assets using Nginx
FROM nginx:alpine

# Copy built files from stage 1 to the Nginx serving directory
COPY --from=build /app/dist /usr/share/nginx/html

# Apply custom Nginx configuration for Single Page Application routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
