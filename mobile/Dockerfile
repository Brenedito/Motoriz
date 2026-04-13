FROM node:20
WORKDIR /app
COPY MotorizApp/package*.json ./
RUN npm install
COPY MotorizApp/ .
CMD ["npx", "react-native", "start"]