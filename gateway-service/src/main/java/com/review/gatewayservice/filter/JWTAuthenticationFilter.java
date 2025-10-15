package com.review.gatewayservice.filter;

import com.nimbusds.jose.JWSVerifier;
import com.nimbusds.jose.crypto.MACVerifier;
import com.nimbusds.jwt.SignedJWT;
import com.review.common.shared.CustomHeader;
import com.review.gatewayservice.properties.JwtProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.ReactiveSecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

import java.util.Date;
import java.util.List;

@Component
@Slf4j
@RequiredArgsConstructor
public class JWTAuthenticationFilter implements WebFilter {

    private final JwtProperties jwtProperties;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        log.info("Start parsing jwt");
        ServerHttpRequest request = exchange.getRequest();

        String header = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);
        if (header == null || !header.startsWith("Bearer ")) {
            return chain.filter(exchange);
        }

        String token = header.substring(7);
        try {
            SignedJWT signedJWT = SignedJWT.parse(token);
            JWSVerifier verifier = new MACVerifier(jwtProperties.secretKey());

            if (!signedJWT.verify(verifier)) {
                exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
                return exchange.getResponse().setComplete();
            }

            Date expirationTime = signedJWT.getJWTClaimsSet().getExpirationTime();
            if (expirationTime == null || new Date().after(expirationTime)) {
                exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
                return exchange.getResponse().setComplete();
            }

            String userId = signedJWT.getJWTClaimsSet().getSubject();
            String role = (String) signedJWT.getJWTClaimsSet().getClaim("role");
            String email = (String) signedJWT.getJWTClaimsSet().getClaim("email");
            String fullName = (String) signedJWT.getJWTClaimsSet().getClaim("fullName");
            ServerHttpRequest mutatedRequest = request.mutate()
                    .header(CustomHeader.X_USER_ID, userId)
                    .header(CustomHeader.X_ROLES, role)
                    .header(CustomHeader.X_EMAIL, email)
                    .header(CustomHeader.X_FULL_NAME, fullName)
                    .build();

            ServerWebExchange mutatedExchange = exchange.mutate()
                    .request(mutatedRequest).build();

            List<SimpleGrantedAuthority> authorities = List.of(new SimpleGrantedAuthority(role));
            Authentication auth = new UsernamePasswordAuthenticationToken(userId, null, authorities);

            return chain.filter(mutatedExchange)
                    .contextWrite(ReactiveSecurityContextHolder.withAuthentication(auth));

        } catch (Exception e) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

    }
}