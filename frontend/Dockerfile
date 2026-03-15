FROM node:20-alpine

# Enable corepack and activate pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy lockfile and manifest
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy rest of the source
COPY . .

# Open port
EXPOSE 5173

# Run with 0.0.0.0 so vite binds to the container not localhost
CMD ["pnpm", "dev"]
