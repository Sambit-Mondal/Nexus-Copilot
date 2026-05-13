# Client (Next.js) Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY client/package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY client/ .

# Build the application with API URL
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "start"]
