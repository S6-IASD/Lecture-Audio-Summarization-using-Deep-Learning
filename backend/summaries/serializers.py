from rest_framework import serializers
from .models import Summary


class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = [
            'id', 'original_filename', 'transcript', 'summary_text',
            'word_count', 'target_words', 'faithfulness',
            'transcript_file', 'summary_file', 'audio_file',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class SummaryListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views (no full transcript/summary text)."""
    class Meta:
        model = Summary
        fields = [
            'id', 'original_filename', 'word_count', 'target_words',
            'faithfulness', 'audio_file', 'created_at'
        ]
        read_only_fields = fields
