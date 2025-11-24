FROM postgres:15

# Set environment variables
ENV POSTGRES_DB=monopoly
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

# Copy the schema file to the initialization directory
# Scripts in this directory are run when the container is started for the first time
COPY src/monopoly/db/schema.sql /docker-entrypoint-initdb.d/
