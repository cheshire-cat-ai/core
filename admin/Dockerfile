FROM node:18.16.0-bullseye-slim

COPY . /app
# Create app directory
WORKDIR /app
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
RUN chmod 755 /app
USER appuser
WORKDIR /app

#ENV NODE_ENV=production
#RUN npm ci --only=production ; npm run build # Review package.json for promotion of devDependencies
RUN npm install
# Expose port 3000 and build + start application
EXPOSE 3000
# Run npm as our non-root user

#CMD ["/bin/bash", "-c", "npm run start"] # Review package.json for promotion of devDependencies
CMD ["/bin/bash", "-c", "npm run dev"]
