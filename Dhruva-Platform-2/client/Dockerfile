FROM node:16-alpine

# Set working directory
WORKDIR /usr/app

# Install git
RUN apk add --no-cache git

# Copy package files first (for better caching)
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"]

