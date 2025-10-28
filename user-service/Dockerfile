FROM maven:3.9.6-eclipse-temurin-21 AS builder
WORKDIR /app

# Copy toàn bộ project để Maven có thể resolve dependency giữa modules
COPY . /app

# Build only user-service and its dependency: common
RUN mvn clean package -DskipTests -f /app/pom.xml -pl user-service,common-library

FROM eclipse-temurin:21-jre
WORKDIR /usr/src/app
COPY --from=builder /app/user-service/target/user-service-0.0.1-SNAPSHOT.jar app.jar
#COPY .env .env

# Expose port
EXPOSE 7071
ENTRYPOINT ["java", "-jar", "app.jar"]
