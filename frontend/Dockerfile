FROM node:18

# Create app directory
WORKDIR /app

# Install app dependencies
COPY frontend/package*.json ./
RUN npm install

# Bundle app source
COPY frontend .
RUN npm run build

# Expose port 3000 and start application
EXPOSE 3000
CMD [ "npm", "start" ]
