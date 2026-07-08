from talentcopilot.ai_core.models import StructuredOutputEnvelope


class StructuredOutputValidator:
    def validate_required_fields(
        self,
        schema_name: str,
        data: dict,
        required_fields: list[str],
    ) -> StructuredOutputEnvelope:
        errors = []
        for field in required_fields:
            if field not in data or data.get(field) in (None, "", []):
                errors.append(f"Missing required field: {field}")

        return StructuredOutputEnvelope(
            schema_name=schema_name,
            data=data,
            validation_status="Valid" if not errors else "Invalid",
            errors=errors,
        )
