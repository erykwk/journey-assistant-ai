# Etap 1: Budowanie
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Etap 2: Serwowanie
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Kopiujemy konfigurację Nginx, aby poprawnie obsługiwać routing po stronie klienta
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
