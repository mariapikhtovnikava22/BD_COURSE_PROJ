# Используем Node.js образ
FROM node:20

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем проект
COPY . .

# Указываем порт для сервера
EXPOSE 3000

# Команда для запуска
CMD ["npm", "start"]