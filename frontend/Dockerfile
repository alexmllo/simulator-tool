FROM node:20-slim

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

RUN npm run build

EXPOSE 4200

CMD ["npm", "start", "--", "--host", "0.0.0.0", "--disable-host-check"] 