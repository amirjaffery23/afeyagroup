# Use a Node.js image to build the frontend
FROM node:16 as build

# Set the working directory in the container
WORKDIR /app

# Copy only the package files first (optimize caching)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Debug: Check if node_modules is installed
RUN ls -la node_modules

# Copy the rest of the application code
COPY . .

# Debug: List the contents of /app and src/utils
RUN ls -la /app
RUN ls -la /app/src/utils

# Build the application for production
RUN npm run build

# Use a lightweight web server to serve the frontend
FROM nginx:alpine

# Copy the built frontend files to Nginx's web directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port the server runs on
EXPOSE 80 3000

# Start the web server
CMD ["nginx", "-g", "daemon off;"]
