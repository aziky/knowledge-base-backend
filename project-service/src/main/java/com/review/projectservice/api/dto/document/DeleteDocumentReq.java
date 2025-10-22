package com.review.projectservice.api.dto.document;

import java.util.List;
import java.util.UUID;

public record DeleteDocumentReq(
        List<UUID> documentIds
) {
}
