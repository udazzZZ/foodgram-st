FROM node:21.7.1-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set registry https://registry.npmjs.org/ && \
    for attempt in 1 2 3; do \
      npm ci --legacy-peer-deps --prefer-offline --no-audit && break; \
      if [ "$attempt" = "3" ]; then exit 1; fi; \
      npm cache verify || true; \
      sleep 10; \
    done
COPY . ./
RUN npm run build

FROM nginx:1.25.4-alpine
WORKDIR /usr/share/nginx/html

COPY --from=builder /app/build .

COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
