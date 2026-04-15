import os
import requests
import shutil
from django.conf import settings
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, Http404

from .models import Summary
from .serializers import SummarySerializer, SummaryListSerializer


class SummaryCreateView(APIView):
    """
    Upload audio → proxy to FastAPI → save result in DB.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response(
                {'detail': 'Aucun fichier audio fourni.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reference_voice = request.FILES.get('reference_voice')
        mode = request.data.get('mode', 'resumeaudio')
        target_words = request.data.get('target_words', 150)

        try:
            # Build multipart form for FastAPI
            files = {
                'audio': (audio_file.name, audio_file.read(), audio_file.content_type),
            }
            if reference_voice:
                files['reference'] = (
                    reference_voice.name,
                    reference_voice.read(),
                    reference_voice.content_type
                )
            elif mode == 'resumeaudio':
                default_ref_path = os.path.join(settings.MEDIA_ROOT, 'audio_reference', 'ma_voix_ref.wav')
                if os.path.exists(default_ref_path):
                    with open(default_ref_path, 'rb') as f:
                        ref_content = f.read()
                    files['reference'] = (
                        'ma_voix_ref.wav',
                        ref_content,
                        'audio/wav'
                    )

            data = {}
            if mode in ['resume', 'resumeaudio']:
                data['target_words'] = str(target_words)

            # Proxy request to FastAPI
            fastapi_url = f"{settings.FASTAPI_URL}/{mode}"
            print(f"DEBUG - Proxying to FastAPI: {fastapi_url}")
            response = requests.post(
                fastapi_url,
                files=files,
                data=data,
                timeout=600  # 10 minutes max for processing
            )

            if response.status_code != 200:
                error_detail = 'Erreur du service de résumé.'
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', error_detail)
                except Exception:
                    pass
                return Response(
                    {'detail': error_detail},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            result = response.json()

            # Handle unexpected list responses from FastAPI (e.g. error tuples [dict, 500])
            if isinstance(result, list):
                if len(result) > 0 and isinstance(result[0], dict) and 'error' in result[0]:
                    return Response({'detail': result[0]['error']}, status=status.HTTP_502_BAD_GATEWAY)
                return Response({'detail': 'Format inattendu depuis le service FastAPI.'}, status=status.HTTP_502_BAD_GATEWAY)

            # Check if dict contains an error
            if isinstance(result, dict) and 'error' in result:
                return Response({'detail': result['error']}, status=status.HTTP_502_BAD_GATEWAY)

            if not isinstance(result, dict):
                return Response({'detail': 'Type de réponse inattendu depuis FastAPI.'}, status=status.HTTP_502_BAD_GATEWAY)

            # Download generated files from FastAPI and save locally
            media_dir = os.path.join(settings.MEDIA_ROOT, f'user_{request.user.id}')
            os.makedirs(media_dir, exist_ok=True)

            transcript_rel = ''
            summary_rel = ''
            audio_rel = ''

            # If FastAPI didn't return a "files" dict, we still need to create files locally 
            # if we want the frontend download buttons to work. We'll use the returned text.
            transcript_text = result.get('transcription', '')
            resume_text = result.get('resume', '')

            # Download transcript file if URL provided
            if result.get('files', {}).get('transcript'):
                transcript_rel = self._download_file(
                    result['files']['transcript'], media_dir,
                    f'user_{request.user.id}'
                )
            elif transcript_text:
                # Manual creation
                transcript_filename = f"{os.path.splitext(audio_file.name)[0]}_transcript.txt"
                local_path = os.path.join(media_dir, transcript_filename)
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(transcript_text)
                transcript_rel = f'user_{request.user.id}/{transcript_filename}'

            # Download summary file if URL provided
            if result.get('files', {}).get('summary_text'):
                summary_rel = self._download_file(
                    result['files']['summary_text'], media_dir,
                    f'user_{request.user.id}'
                )
            elif resume_text:
                # Manual creation
                summary_filename = f"{os.path.splitext(audio_file.name)[0]}_summary.txt"
                local_path = os.path.join(media_dir, summary_filename)
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(resume_text)
                summary_rel = f'user_{request.user.id}/{summary_filename}'

            # Download audio file if URL provided
            if result.get('files', {}).get('summary_audio'):
                audio_rel = self._download_file(
                    result['files']['summary_audio'], media_dir,
                    f'user_{request.user.id}'
                )

            # Save to database
            summary_obj = Summary.objects.create(
                user=request.user,
                original_filename=audio_file.name,
                transcript=transcript_text,
                summary_text=resume_text,
                word_count=result.get('word_count', 0),
                target_words=int(target_words),
                faithfulness=result.get('faithfulness', 0.0),
                transcript_file=transcript_rel,
                summary_file=summary_rel,
                audio_file=audio_rel,
            )

            # Try to read full transcript from downloaded file
            if transcript_rel:
                transcript_path = os.path.join(settings.MEDIA_ROOT, transcript_rel)
                if os.path.exists(transcript_path):
                    with open(transcript_path, 'r', encoding='utf-8') as f:
                        summary_obj.transcript = f.read()
                    summary_obj.save()

            # Try to read full summary from downloaded file
            if summary_rel:
                summary_path = os.path.join(settings.MEDIA_ROOT, summary_rel)
                if os.path.exists(summary_path):
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary_obj.summary_text = f.read()
                    summary_obj.save()

            serializer = SummarySerializer(summary_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except requests.exceptions.ConnectionError:
            return Response(
                {'detail': 'Impossible de se connecter au service de résumé. Vérifiez que FastAPI est lancé sur le port 8000.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except requests.exceptions.Timeout:
            return Response(
                {'detail': 'Le traitement a pris trop de temps. Réessayez avec un fichier plus court.'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception as e:
            return Response(
                {'detail': f'Erreur inattendue: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _download_file(self, file_path, media_dir, user_prefix):
        """Download a file from FastAPI and save it locally."""
        try:
            url = f"{settings.FASTAPI_URL}{file_path}"
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                filename = os.path.basename(file_path)
                local_path = os.path.join(media_dir, filename)
                with open(local_path, 'wb') as f:
                    f.write(resp.content)
                return f'{user_prefix}/{filename}'
        except Exception:
            pass
        return ''


class SummaryListView(generics.ListAPIView):
    """List all summaries for the authenticated user."""
    serializer_class = SummaryListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Summary.objects.filter(user=self.request.user)


class SummaryDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a specific summary."""
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Summary.objects.filter(user=self.request.user)


class SummaryDownloadView(APIView):
    """Download a file associated with a summary."""
    permission_classes = [IsAuthenticated]

    def get(self, request, summary_id, file_type):
        try:
            summary = Summary.objects.get(id=summary_id, user=request.user)
        except Summary.DoesNotExist:
            raise Http404

        file_map = {
            'transcript': summary.transcript_file,
            'summary': summary.summary_file,
            'audio': summary.audio_file,
        }

        rel_path = file_map.get(file_type, '')
        if not rel_path:
            raise Http404

        full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
        if not os.path.exists(full_path):
            raise Http404

        return FileResponse(open(full_path, 'rb'), as_attachment=True)


class HealthView(APIView):
    """Check if FastAPI backend is reachable."""
    permission_classes = []

    def get(self, request):
        try:
            resp = requests.get(
                f"{settings.FASTAPI_URL}/health",
                timeout=5
            )
            if resp.status_code == 200:
                return Response({'status': 'ok', 'fastapi': 'connected'})
        except Exception:
            pass
        return Response(
            {'status': 'ok', 'fastapi': 'disconnected'},
            status=status.HTTP_200_OK
        )
