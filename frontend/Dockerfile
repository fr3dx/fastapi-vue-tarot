# Stage 1: Build the frontend
FROM bitnami/node:24.0.1-debian-12-r1 AS builder

# Build args
ARG VITE_BACKEND_URL
ARG VITE_GOOGLE_CLIENT_ID

# Set environment variables
ENV VITE_BACKEND_URL=${VITE_BACKEND_URL}
ENV VITE_GOOGLE_CLIENT_ID=${VITE_GOOGLE_CLIENT_ID}

# Set working directory
WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy source files and build the project
COPY frontend .
RUN npm run build

# Stage 2: Serve the built static files
FROM nginx:alpine

# Copy the build files from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port that the frontend will be served on
EXPOSE 80

# Command to run the Nginx server
CMD ["nginx", "-g", "daemon off;"]
