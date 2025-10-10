package com.review.userservice.shared.utils;

import com.nimbusds.jose.JWSAlgorithm;
import com.nimbusds.jose.JWSHeader;
import com.nimbusds.jose.JWSSigner;
import com.nimbusds.jose.crypto.MACSigner;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;
import com.review.userservice.infrastructure.config.domain.entity.User;
import com.review.userservice.infrastructure.properties.JwtProperties;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.stereotype.Component;

import java.util.Date;


@Component
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class JwtUtil {

    JwtProperties jwtProperties;

    public String generateToken(User user) {
        try {
            JWSSigner signer = new MACSigner(jwtProperties.secretKey().getBytes());

            JWTClaimsSet claimsSet = new JWTClaimsSet.Builder()
                    .subject(user.getId().toString())
                    .issuer(jwtProperties.issuer())
                    .claim("email", user.getEmail())
                    .claim("role", user.getRole())
                    .claim("fullname", user.getFullName())
//                    .claim("status", user)
                    .issueTime(new Date())
                    .expirationTime(new Date(System.currentTimeMillis() + jwtProperties.duration() * 1000))
                    .build();

            SignedJWT signedJWT = new SignedJWT(
                    new JWSHeader(JWSAlgorithm.HS256),
                    claimsSet
            );

            signedJWT.sign(signer);
            return signedJWT.serialize();
        } catch (Exception e) {
            throw new RuntimeException("Error at generate token");
        }
    }

}