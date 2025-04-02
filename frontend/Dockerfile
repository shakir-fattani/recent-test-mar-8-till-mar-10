
# Stage 1: Build the application
FROM node:23-alpine AS builder

RUN npm i -g npm
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm i

# Copy the rest of the application code
COPY . .

# Build the Next.js application
RUN npm run build

# Stage 2: Run the application
FROM node:23-alpine
RUN npm i -g npm

WORKDIR /app

ENV NODE_ENV=production

# Copy necessary files from the builder stage
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose the port the app runs on
EXPOSE 3000

# Run the application
CMD ["npm", "start"]
