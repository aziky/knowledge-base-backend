FROM maven:3.9.6-eclipse-temurin-21 AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /usr/src/app
COPY --from=builder /app/target/user-service-0.0.1-SNAPSHOT.jar app.jar
#COPY .env .env

# Expose port
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
